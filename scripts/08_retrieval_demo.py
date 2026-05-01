import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json

from src.retrieval.tfidf_retriever import TfidfRetriever
from src.storage.jsonl_writer import read_jsonl


def to_markdown(query: str, results: list[dict]) -> str:
    lines = ["# 相似范文检索结果", "", "## 查询文本", query, "", "## Top 结果"]
    if not results:
        lines.append("未检索到结果。")
        return "\n".join(lines) + "\n"
    for r in results:
        lines.extend([
            f"### {r['rank']}. {r['title']}",
            f"- score: {r['score']}",
            f"- 栏目: {r['category']}",
            f"- 类型: {r['article_type']}",
            f"- 日期: {r['publish_date']}",
            f"- 链接: {r['url']}",
            f"- chunk_id: {r['chunk_id']}",
            f"- 匹配原因: {r['match_reason']}",
            f"- 片段: {r['chunk_text'][:220]}...",
            "",
        ])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks", default="data/chunks/article_chunks.jsonl")
    parser.add_argument("--query", default="")
    parser.add_argument("--query-file", default="")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--dedupe-article", action="store_true")
    parser.add_argument("--out-json", default="data/demo_outputs/retrieval_result.json")
    parser.add_argument("--out-md", default="data/demo_outputs/retrieval_result.md")
    args = parser.parse_args()

    query = args.query.strip()
    if args.query_file:
        query = Path(args.query_file).read_text(encoding="utf-8")
    if not query:
        raise ValueError("请通过 --query 或 --query-file 提供查询文本")

    chunks = read_jsonl(args.chunks)
    retriever = TfidfRetriever(chunks)
    results = retriever.search(query=query, top_k=args.top_k, dedupe_article=args.dedupe_article)

    payload = {
        "query": query,
        "top_k": args.top_k,
        "dedupe_article": bool(args.dedupe_article),
        "result_count": len(results),
        "results": results,
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(to_markdown(query, results), encoding="utf-8")


if __name__ == "__main__":
    main()
