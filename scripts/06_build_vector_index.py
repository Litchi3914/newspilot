import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import math
from collections import Counter

from src.storage.jsonl_writer import read_jsonl


def tokenize(text: str) -> list[str]:
    ascii_tokens = [w for w in text.replace("\n", " ").split(" ") if w.strip()]
    zh_tokens = [ch for ch in text if "\u4e00" <= ch <= "\u9fff"]
    return ascii_tokens + zh_tokens


def cosine_sim(a: Counter, b: Counter) -> float:
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/chunks/article_chunks.jsonl")
    parser.add_argument("--query", default="交流会在会议室召开")
    parser.add_argument("--topk", type=int, default=5)
    parser.add_argument("--vectorstore", default="mock")
    args = parser.parse_args()

    rows = read_jsonl(args.input)
    q = Counter(tokenize(args.query))
    scored = []
    for r in rows:
        score = cosine_sim(q, Counter(tokenize(r.get("chunk_text", ""))))
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)

    for i, (score, r) in enumerate(scored[: args.topk], start=1):
        print(f"相似稿件 {i}:")
        print(f"标题：{r.get('title','')}")
        print(f"栏目：{r.get('category','')}")
        print(f"类型：{r.get('article_type','')}")
        print(f"链接：{r.get('url','')}")
        print(f"相似原因：关键词重合度={score:.3f}")
        print()


if __name__ == "__main__":
    main()
