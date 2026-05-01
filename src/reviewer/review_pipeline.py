from __future__ import annotations
from datetime import datetime
from pathlib import Path
import csv
import time

from src.reviewer.rule_engine import ReviewRuleEngine
from src.diff.text_diff import TextDiffGenerator
from src.knowledge_base.builder import NewsKnowledgeBase
from src.llm.factory import create_llm_client, load_llm_config
from src.llm.schemas import default_review_result, validate_or_fallback
from src.review.pipeline import build_review_result


def _append_llm_log(log_path: str, row: dict) -> None:
    p = Path(log_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        'request_id', 'provider', 'model', 'method', 'prompt_version', 'input_char_count', 'output_char_count',
        'latency_ms', 'success', 'error_type', 'error_message', 'fallback_used', 'created_at'
    ]
    exists = p.exists()
    with p.open('a', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k, '') for k in headers})


class ReviewPipeline:
    def __init__(self, chunks_path: str, retriever: str = 'bm25', llm_provider: str | None = None):
        self.engine = ReviewRuleEngine()
        self.diff = TextDiffGenerator()
        self.kb = NewsKnowledgeBase(retriever_name=retriever)
        self.kb.build(chunks_path)
        self.retriever = retriever

        self.llm_cfg = load_llm_config('configs/llm.yaml')
        if llm_provider:
            self.llm_cfg['provider'] = llm_provider
        self.llm = create_llm_client(self.llm_cfg)

    def run(self, title: str, draft_text: str, article_type: str | None = None, options: dict | None = None) -> dict:
        options = options or {}
        request_id = options.get('request_id') or ('review_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
        errors = []

        enable_llm = bool(options.get('enable_llm', True))
        enable_diff = bool(options.get('enable_diff', True))
        fast_mode = bool(options.get('fast_mode', True))

        rule = self.engine.review(title=title, text=draft_text, article_type=article_type)
        detected = rule['detected_type']
        refs = self.kb.search(draft_text, top_k=options.get('top_k', 5), filters={'article_type': detected})

        provider = self.llm_cfg.get('provider', 'mock')
        model = self.llm_cfg.get('openai', {}).get('model', 'mock') if provider == 'openai' else 'mock'
        log_path = self.llm_cfg.get('logging', {}).get('log_path', 'data/logs/llm_call_log.csv')

        llm_review_result = default_review_result(detected)
        llm_review_result['revised_title'] = title
        llm_review_result['revised_text'] = draft_text

        if enable_llm:
            methods = ['revise_article'] if fast_mode else ['review_article', 'revise_article']
            total_llm_start = time.time()

            for method in methods:
                elapsed = time.time() - total_llm_start
                if method == 'revise_article' and (not fast_mode) and elapsed > 60:
                    errors.append({
                        'stage': method,
                        'error_type': 'skipped_due_to_time_budget',
                        'error_message': f'skipped revise call after {int(elapsed)}s to avoid timeout'
                    })
                    continue

                start = time.time()
                ok = True
                err_type = ''
                err_msg = ''
                fallback_used = False
                out = {}
                try:
                    if method == 'review_article':
                        out = self.llm.review_article(title, draft_text, detected, references=refs, rule_check_result=rule)
                    else:
                        out = self.llm.revise_article(title, draft_text, detected, references=refs, issues=[])
                except Exception as exc:  # noqa: BLE001
                    ok = False
                    err_type = type(exc).__name__
                    err_msg = str(exc)
                    fallback_used = True
                    out = {}

                merged = {**llm_review_result, **out}
                valid, schema_ok, schema_err = validate_or_fallback(merged, llm_review_result)
                if not schema_ok:
                    ok = False
                    fallback_used = True
                    err_type = err_type or 'schema_validation_error'
                    err_msg = err_msg or schema_err
                llm_review_result = valid

                if not ok:
                    errors.append({'stage': method, 'error_type': err_type, 'error_message': err_msg})

                latency = int((time.time() - start) * 1000)
                _append_llm_log(log_path, {
                    'request_id': request_id,
                    'provider': provider,
                    'model': model,
                    'method': method,
                    'prompt_version': 'v1-fast' if fast_mode else 'v1',
                    'input_char_count': len(draft_text or ''),
                    'output_char_count': len(str(out)),
                    'latency_ms': latency,
                    'success': ok,
                    'error_type': err_type,
                    'error_message': err_msg,
                    'fallback_used': fallback_used,
                    'created_at': datetime.now().isoformat(timespec='seconds'),
                })
        else:
            errors.append({'stage': 'llm', 'error_type': 'disabled', 'error_message': 'LLM disabled by option.'})

        revised_title = llm_review_result.get('revised_title') or title
        revised_text = llm_review_result.get('revised_text') or draft_text
        revision_effective = (revised_text or '').strip() != (draft_text or '').strip()

        diff_ops = []
        if enable_diff:
            try:
                diff_ops = self.diff.generate(draft_text, revised_text, llm_review_result.get('issues', []))
            except Exception as exc:  # noqa: BLE001
                errors.append({'stage': 'diff', 'error_type': type(exc).__name__, 'error_message': str(exc)})
                diff_ops = []

        status = 'success' if not any(e.get('error_type') not in {'disabled'} for e in errors) else 'partial_success'
        structured_result = build_review_result(
            source_text=draft_text,
            revised_text=revised_text,
            article_type=detected,
            rag_references=refs,
            rule_check_result=rule,
            llm_result=llm_review_result,
        ).model_dump(mode='json')

        return {
            'request_id': request_id,
            'status': status,
            'version': structured_result.get('version', 'review_result_v1'),
            'detected_type': detected,
            'original_title': title,
            'original_text': draft_text,
            'rule_check_result': rule,
            'retrieval_results': refs,
            'llm_review_result': llm_review_result,
            'revised_title': revised_title,
            'revised_text': revised_text,
            'diff_ops': diff_ops,
            'review_result': structured_result,
            'source_text': structured_result.get('source_text', draft_text),
            'edit_operations': structured_result.get('edit_operations', []),
            'issues': structured_result.get('issues', []),
            'sensitive_entities': structured_result.get('sensitive_entities', []),
            'rag_references': structured_result.get('rag_references', refs),
            'summary': structured_result.get('summary', {}),
            'errors': errors,
            'metadata': {
                'provider': provider,
                'model': model,
                'created_at': datetime.now().isoformat(timespec='seconds'),
                'retriever': self.retriever,
                'enable_llm': enable_llm,
                'enable_diff': enable_diff,
                'fast_mode': fast_mode,
                'revision_effective': revision_effective,
            },
        }
