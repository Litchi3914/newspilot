from __future__ import annotations
import json
from pathlib import Path
import csv

from src.reviewer.review_pipeline import ReviewPipeline
from src.evaluator.metrics import bool_rate


def _normalize_detected_type(t: str) -> str:
    return (t or '').strip()


def _has_missing_element_hit(pred_element_items: list[dict], gold_missing: list[str]) -> bool:
    if not gold_missing:
        return True
    pred_missing = {x.get('element') for x in pred_element_items if x.get('status') == 'missing'}
    # relaxed: hit if any gold missing element appears in predicted missing set
    return any(g in pred_missing for g in gold_missing)


def run_eval(samples_path: str, chunks_path: str, out_csv: str, out_md: str, retriever: str = 'bm25', llm_provider: str = 'mock'):
    samples = []
    p = Path(samples_path)
    if p.exists():
        for line in p.read_text(encoding='utf-8-sig').splitlines():
            line = line.strip()
            if line:
                samples.append(json.loads(line))

    pipe = ReviewPipeline(chunks_path=chunks_path, retriever=retriever, llm_provider=llm_provider)
    rows = []
    for s in samples:
        result = pipe.run(
            title=s.get('title', ''),
            draft_text=s.get('draft_text', ''),
            article_type=None,
            options={'top_k': 5, 'enable_llm': True, 'enable_diff': True},
        )
        pred_type = _normalize_detected_type(result.get('detected_type', ''))
        gold_type = _normalize_detected_type(s.get('gold_article_type', ''))

        element_items = ((result.get('rule_check_result') or {}).get('element_check') or [])
        gold_missing = s.get('gold_missing_elements', []) or []

        rows.append({
            'sample_id': s.get('sample_id', ''),
            'type_correct': pred_type == gold_type,
            'missing_element_hit': _has_missing_element_hit(element_items, gold_missing),
            'has_revised_text': bool(result.get('revised_text')),
            'has_diff_ops': bool(result.get('diff_ops')),
            'has_references': bool(result.get('retrieval_results')),
            'status': result.get('status', ''),
            'error_count': len(result.get('errors', [])),
        })

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(
            f,
            fieldnames=['sample_id', 'type_correct', 'missing_element_hit', 'has_revised_text', 'has_diff_ops', 'has_references', 'status', 'error_count']
        )
        w.writeheader()
        w.writerows(rows)

    type_acc = bool_rate([x['type_correct'] for x in rows]) if rows else 0.0
    elem_hit = bool_rate([x['missing_element_hit'] for x in rows]) if rows else 0.0
    revised_rate = bool_rate([x['has_revised_text'] for x in rows]) if rows else 0.0
    diff_rate = bool_rate([x['has_diff_ops'] for x in rows]) if rows else 0.0
    ref_rate = bool_rate([x['has_references'] for x in rows]) if rows else 0.0

    md = [
        '# Eval Report',
        '',
        f'- samples: {len(rows)}',
        f'- type_accuracy: {type_acc}%',
        f'- missing_element_hit_rate: {elem_hit}%',
        f'- revised_text_success_rate: {revised_rate}%',
        f'- diff_ops_success_rate: {diff_rate}%',
        f'- references_success_rate: {ref_rate}%',
        '',
        '## Notes',
        '- 当前评估集为脚手架样本，用于流程稳定性和字段完整性验证。',
        '- 后续建议补充人工标注高质量样本以提升指标可信度。',
        '',
    ]
    Path(out_md).write_text('\n'.join(md), encoding='utf-8')

