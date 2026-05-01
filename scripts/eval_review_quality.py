import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json
import time

from src.reviewer.review_pipeline import ReviewPipeline


def percentile(vals, p):
    if not vals:
        return 0
    vals = sorted(vals)
    idx = int((len(vals)-1) * p)
    return vals[idx]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default='data/eval/review_eval_set_v1.jsonl')
    p.add_argument('--output', default='reports/gray_release_eval_report.md')
    p.add_argument('--chunks', default='data/chunks/article_chunks.jsonl')
    p.add_argument('--retriever', default='bm25')
    p.add_argument('--llm-provider', default='mock')
    args = p.parse_args()

    rows = []
    for line in Path(args.input).read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))

    pipe = ReviewPipeline(chunks_path=args.chunks, retriever=args.retriever, llm_provider=args.llm_provider)

    success = 0
    failed = 0
    elapsed = []
    error_summary = {}

    for r in rows:
        st = time.time()
        out = pipe.run(title=r.get('title',''), draft_text=r.get('content',''), article_type=None, options={'top_k':5,'enable_llm':True,'enable_diff':True})
        ms = int((time.time()-st)*1000)
        elapsed.append(ms)
        if out.get('status') in {'success','partial_success'}:
            success += 1
        else:
            failed += 1
        for e in out.get('errors', []):
            k = e.get('error_type','unknown')
            error_summary[k] = error_summary.get(k, 0) + 1

    total = len(rows)
    success_rate = round(success * 100 / max(total,1), 2)
    error_rate = round(failed * 100 / max(total,1), 2)
    avg_ms = int(sum(elapsed)/max(len(elapsed),1))
    p95 = percentile(elapsed, 0.95)

    gate_success = success_rate >= 95
    gate_error = error_rate <= 5
    gate_avg = avg_ms <= 30000
    gate_p95 = p95 <= 45000
    passed = gate_success and gate_error and gate_avg and gate_p95

    md = [
        '# 灰度测试准入评估报告',
        '',
        '## 1. 评估基本信息',
        f'- 评估数据集：{args.input}',
        f'- 样本数量：{total}',
        f'- 模型模式：{args.llm_provider}',
        f'- 检索模式：{args.retriever}',
        '',
        '## 2. 核心指标',
        '| 指标 | 阈值 | 当前结果 | 是否通过 |',
        '|---|---|---|---|',
        f'| 接口成功率 | >= 95% | {success_rate}% | {"通过" if gate_success else "不通过"} |',
        f'| 接口错误率 | <= 5% | {error_rate}% | {"通过" if gate_error else "不通过"} |',
        f'| 平均响应时间 | <= 30s | {avg_ms/1000:.2f}s | {"通过" if gate_avg else "不通过"} |',
        f'| P95 响应时间 | <= 45s | {p95/1000:.2f}s | {"通过" if gate_p95 else "不通过"} |',
        '| 严重误判率 | <= 10% | 待人工复核 | 待判断 |',
        '| 人工可采纳率 | >= 70% | 待人工复核 | 待判断 |',
        '| diff 可读性通过率 | >= 80% | 待人工复核 | 待判断 |',
        '| 前端展示异常率 | <= 5% | 待联调统计 | 待判断 |',
        '',
        '## 3. 错误分布',
        json.dumps(error_summary, ensure_ascii=False),
        '',
        '## 4. 主要问题',
        '- 目前主要为脚手架评估，需补充人工标注内容细化质量判断。',
        '',
        '## 5. 是否建议进入灰度',
        f'- 结论：{"建议进入小范围灰度" if passed else "暂不建议，需继续优化"}',
        '',
        '## 6. 后续改进项',
        '- 增加人工可采纳率与diff可读性人工复核流程。',
        '- 扩展评估样本到50条以上。',
        ''
    ]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text('\n'.join(md), encoding='utf-8')


if __name__ == '__main__':
    main()
