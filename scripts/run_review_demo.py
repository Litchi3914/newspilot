import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json
from src.reviewer.review_pipeline import ReviewPipeline


def _normalize_output(raw: dict) -> dict:
    # Ensure final contract keys always exist.
    return {
        'request_id': raw.get('request_id', ''),
        'status': raw.get('status', 'success'),
        'original_title': raw.get('original_title', ''),
        'original_text': raw.get('original_text', ''),
        'detected_type': raw.get('detected_type', ''),
        'rule_check_result': raw.get('rule_check_result', {}),
        'retrieval_results': raw.get('retrieval_results', []),
        'llm_review_result': raw.get('llm_review_result', {}),
        'revised_title': raw.get('revised_title', ''),
        'revised_text': raw.get('revised_text', ''),
        'diff_ops': raw.get('diff_ops', []),
        'review_result': raw.get('review_result', {}),
        'version': raw.get('version', 'review_result_v1'),
        'source_text': raw.get('source_text', raw.get('original_text', '')),
        'edit_operations': raw.get('edit_operations', []),
        'issues': raw.get('issues', []),
        'sensitive_entities': raw.get('sensitive_entities', []),
        'rag_references': raw.get('rag_references', raw.get('retrieval_results', [])),
        'summary': raw.get('summary', {}),
        'errors': raw.get('errors', []),
        'metadata': {
            'provider': (raw.get('metadata') or {}).get('provider', 'mock'),
            'model': (raw.get('metadata') or {}).get('model', 'mock'),
            'created_at': (raw.get('metadata') or {}).get('created_at', ''),
            'retriever': (raw.get('metadata') or {}).get('retriever', ''),
            'enable_llm': (raw.get('metadata') or {}).get('enable_llm', True),
            'enable_diff': (raw.get('metadata') or {}).get('enable_diff', True),
        },
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='examples/sample_draft.txt')
    p.add_argument('--retriever', default='bm25')
    p.add_argument('--llm-provider', default='mock')
    p.add_argument('--enable-llm', action='store_true')
    p.add_argument('--enable-diff', action='store_true')
    p.add_argument('--chunks', default='data/chunks/article_chunks.jsonl')
    p.add_argument('--output', default='outputs/review_result.json')
    a = p.parse_args()

    text = Path(a.input).read_text(encoding='utf-8')
    # Backward compatible behavior: if flags absent, both enabled by default.
    enable_llm = True if '--enable-llm' not in sys.argv else bool(a.enable_llm)
    enable_diff = True if '--enable-diff' not in sys.argv else bool(a.enable_diff)

    pipe = ReviewPipeline(chunks_path=a.chunks, retriever=a.retriever, llm_provider=a.llm_provider)
    raw = pipe.run(
        title='示例稿件',
        draft_text=text,
        article_type=None,
        options={'top_k': 5, 'enable_llm': enable_llm, 'enable_diff': enable_diff},
    )
    out = _normalize_output(raw)

    out_path = Path(a.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    # Keep old demo outputs for backward compatibility.
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/review_result.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    Path('outputs/review_result.md').write_text('# Review Result\n\n' + out.get('revised_text', ''), encoding='utf-8')


if __name__ == '__main__':
    main()
