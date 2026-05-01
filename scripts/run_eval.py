import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
from src.evaluator.eval_runner import run_eval


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--samples', default='data/eval/eval_samples.jsonl')
    p.add_argument('--chunks', default='data/chunks/article_chunks.jsonl')
    p.add_argument('--out-csv', default='data/eval/eval_result.csv')
    p.add_argument('--out-md', default='data/eval/eval_report.md')
    p.add_argument('--retriever', default='bm25')
    p.add_argument('--llm-provider', default='mock')
    a = p.parse_args()

    Path('data/eval').mkdir(parents=True, exist_ok=True)
    run_eval(a.samples, a.chunks, a.out_csv, a.out_md, retriever=a.retriever, llm_provider=a.llm_provider)


if __name__ == '__main__':
    main()
