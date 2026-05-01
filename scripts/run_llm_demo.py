import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json
from src.llm.factory import load_llm_config, create_llm_client
from src.llm.schemas import default_review_result, validate_or_fallback


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='data/demo_inputs/sample_article.txt')
    p.add_argument('--provider', default='mock')
    p.add_argument('--real-call', action='store_true')
    p.add_argument('--out', default='data/demo_outputs/llm_review_demo.json')
    a = p.parse_args()

    text = Path(a.input).read_text(encoding='utf-8') if Path(a.input).exists() else '示例稿件：4月28日上午召开交流会。'

    cfg = load_llm_config('configs/llm.yaml')
    cfg['provider'] = a.provider
    cfg['enable_real_call'] = bool(a.real_call)
    client = create_llm_client(cfg)

    c = client.classify_article_type('示例标题', text)
    atype = c.get('detected_type', '其他')
    r = client.review_article('示例标题', text, atype, references=[], rule_check_result={})
    v = client.revise_article('示例标题', text, atype, references=[], issues=[])

    merged = {**default_review_result(atype), **r, **v}
    valid, ok, err = validate_or_fallback(merged, default_review_result(atype))

    out = {
        'provider': cfg['provider'],
        'enable_real_call': cfg['enable_real_call'],
        'classify': c,
        'result': valid,
        'schema_ok': ok,
        'schema_error': err,
    }
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
