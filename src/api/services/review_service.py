from __future__ import annotations
from datetime import datetime
import csv
from pathlib import Path
import time

from src.api.schemas.review import ReviewRequest, ReviewResponse, ReviewMetadata
from src.api.schemas.errors import APIError, ErrorCode
from src.reviewer.review_pipeline import ReviewPipeline
from src.storage.review_record_store import is_review_record_storage_enabled, save_review_record


def _append_api_log(path: str, row: dict):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    headers = ['request_id','path','method','status','latency_ms','retriever','llm_provider','success','error_count','input_char_count','created_at']
    exists = p.exists()
    with p.open('a', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=headers)
        if not exists:
            w.writeheader()
        w.writerow({k: row.get(k,'') for k in headers})


class ReviewService:
    def __init__(self, chunks_path: str = 'data/chunks/article_chunks.jsonl', api_log_path: str = 'data/logs/api_request_log.csv'):
        self.chunks_path = chunks_path
        self.api_log_path = api_log_path

    def review(self, request: ReviewRequest, request_id: str) -> ReviewResponse:
        start = time.time()
        errors: list[APIError] = []
        try:
            pipe = ReviewPipeline(
                chunks_path=self.chunks_path,
                retriever=request.options.retriever,
                llm_provider=request.options.llm_provider,
            )
            out = pipe.run(
                title=request.title or '',
                draft_text=request.draft_text,
                article_type=None if request.article_type == 'auto' else request.article_type,
                options={
                    'request_id': request_id,
                    'top_k': 5,
                    'enable_llm': request.options.enable_llm,
                    'enable_diff': request.options.enable_diff,
                    'fast_mode': request.options.fast_mode,
                },
            )
            for e in out.get('errors', []):
                code = ErrorCode.LLM_CALL_FAILED if e.get('stage','').startswith('review') or e.get('stage','').startswith('revise') else ErrorCode.UNKNOWN_ERROR
                errors.append(APIError(code=code, message=e.get('error_message',''), stage=e.get('stage','pipeline'), recoverable=True))

            status = out.get('status', 'success')
            if status not in {'success','partial_success','failed'}:
                status = 'partial_success'

            m = out.get('metadata', {})
            meta = ReviewMetadata(
                retriever=request.options.retriever,
                llm_provider=request.options.llm_provider,
                enable_rule_check=request.options.enable_rule_check,
                enable_retrieval=request.options.enable_retrieval,
                enable_llm=request.options.enable_llm,
                enable_diff=request.options.enable_diff,
                fast_mode=bool(m.get('fast_mode', request.options.fast_mode)),
                revision_effective=bool(m.get('revision_effective', False)),
                input_char_count=len(request.draft_text),
                output_char_count=len(out.get('revised_text','') or ''),
                latency_ms=int((time.time()-start)*1000),
            )

            resp = ReviewResponse(
                request_id=request_id,
                status=status,
                detected_type=out.get('detected_type'),
                original_title=out.get('original_title') or request.title,
                original_text=out.get('original_text') or request.draft_text,
                revised_title=out.get('revised_title'),
                revised_text=out.get('revised_text'),
                rule_check_result=out.get('rule_check_result', {}),
                retrieval_results=out.get('retrieval_results', []),
                llm_review_result=out.get('llm_review_result', {}),
                diff_ops=out.get('diff_ops', []),
                review_result=out.get('review_result', {}),
                edit_operations=out.get('edit_operations', []),
                issues=out.get('issues', []),
                sensitive_entities=out.get('sensitive_entities', []),
                rag_references=out.get('rag_references', []),
                summary=out.get('summary', {}),
                data={
                    'original': {'title': request.title or '', 'content': out.get('original_text') or request.draft_text},
                    'revised': {'title': out.get('revised_title') or request.title or '', 'content': out.get('revised_text') or ''},
                    'diff': out.get('diff_ops', []),
                    'issues': out.get('issues', []) or out.get('llm_review_result', {}).get('issues', []),
                    'summary': out.get('summary', {}),
                    'edit_operations': out.get('edit_operations', []),
                    'sensitive_entities': out.get('sensitive_entities', []),
                    'rag_references': out.get('rag_references', []),
                },
                errors=errors,
                metadata=meta,
            )
            if is_review_record_storage_enabled():
                saved = save_review_record(
                    request_id=request_id,
                    title=request.title,
                    input_text=request.draft_text,
                    revised_text=resp.revised_text,
                    issues=resp.issues,
                    diff_result=[op.model_dump(mode='json') for op in resp.diff_ops],
                    raw_result={
                        'status': resp.status,
                        'api_version': resp.api_version,
                        'pipeline_version': resp.pipeline_version,
                        'detected_type': resp.detected_type,
                        'summary': resp.summary,
                        'errors': [e.model_dump(mode='json') for e in resp.errors],
                    },
                    options=request.options.model_dump(mode='json'),
                    client_meta={
                        'source': request.source,
                        'review_mode': request.review_mode,
                        'article_type': request.article_type,
                    },
                )
                resp.metadata.storage_status = 'saved' if saved else 'failed'
            else:
                resp.metadata.storage_status = 'disabled'
            _append_api_log(self.api_log_path, {
                'request_id': request_id,
                'path': '/api/v1/review',
                'method': 'POST',
                'status': resp.status,
                'latency_ms': meta.latency_ms,
                'retriever': request.options.retriever,
                'llm_provider': request.options.llm_provider,
                'success': resp.status != 'failed',
                'error_count': len(resp.errors),
                'input_char_count': len(request.draft_text),
                'created_at': datetime.now().isoformat(timespec='seconds'),
            })
            return resp
        except Exception:
            errors.append(APIError(code=ErrorCode.PIPELINE_FAILED, message='Review pipeline failed.', stage='pipeline', recoverable=False))
            meta = ReviewMetadata(
                retriever=request.options.retriever,
                llm_provider=request.options.llm_provider,
                enable_rule_check=request.options.enable_rule_check,
                enable_retrieval=request.options.enable_retrieval,
                enable_llm=request.options.enable_llm,
                enable_diff=request.options.enable_diff,
                fast_mode=request.options.fast_mode,
                revision_effective=False,
                input_char_count=len(request.draft_text),
                output_char_count=0,
                latency_ms=int((time.time()-start)*1000),
            )
            _append_api_log(self.api_log_path, {
                'request_id': request_id,
                'path': '/api/v1/review',
                'method': 'POST',
                'status': 'failed',
                'latency_ms': meta.latency_ms,
                'retriever': request.options.retriever,
                'llm_provider': request.options.llm_provider,
                'success': False,
                'error_count': len(errors),
                'input_char_count': len(request.draft_text),
                'created_at': datetime.now().isoformat(timespec='seconds'),
            })
            return ReviewResponse(
                request_id=request_id,
                status='failed',
                detected_type=None,
                original_title=request.title,
                original_text=request.draft_text,
                revised_title=None,
                revised_text=None,
                rule_check_result={},
                retrieval_results=[],
                llm_review_result={},
                diff_ops=[],
                errors=errors,
                metadata=meta,
            )
