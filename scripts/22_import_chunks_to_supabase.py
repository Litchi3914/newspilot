from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from src.storage.article_store import clean_date, clean_text, upsert_article_chunks


def map_chunk(row: dict[str, Any]) -> dict[str, Any] | None:
    source_url = clean_text(row.get("url") or row.get("source_url"))
    chunk_text = clean_text(row.get("chunk_text"))
    if not source_url or not chunk_text:
        return None

    metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    metadata = {
        **metadata,
        "chunk_id": clean_text(row.get("chunk_id")),
        "article_id": clean_text(row.get("article_id")),
        "article_type": clean_text(row.get("article_type")),
        "char_count": row.get("char_count"),
        "publish_time": clean_text(row.get("publish_time")),
    }
    return {
        "source_url": source_url,
        "title": clean_text(row.get("title")),
        "publish_date": clean_date(row.get("publish_date") or row.get("publish_time")),
        "category": clean_text(row.get("category")),
        "chunk_index": int(row.get("chunk_index") or 0),
        "chunk_text": chunk_text,
        "metadata": {k: v for k, v in metadata.items() if v is not None},
    }


def read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            if not line.strip():
                continue
            mapped = map_chunk(json.loads(line))
            if mapped:
                rows.append(mapped)
            if limit and len(rows) >= limit:
                break
    return rows


def batched(rows: list[dict[str, Any]], batch_size: int):
    for start in range(0, len(rows), batch_size):
        yield rows[start:start + batch_size]


def main() -> int:
    parser = argparse.ArgumentParser(description="Import article chunks to Supabase.")
    parser.add_argument("--input", default="data/chunks/article_chunks.jsonl")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    rows = read_rows(ROOT / args.input, args.limit)
    print(json.dumps({"input": args.input, "preview_count": len(rows), "sample": rows[:1]}, ensure_ascii=False, indent=2))

    if args.dry_run:
        print(json.dumps({"dry_run": True, "would_upsert": len(rows), "batch_size": args.batch_size}, ensure_ascii=False, indent=2))
        return 0

    success_count = 0
    failed_count = 0
    try:
        for batch in batched(rows, args.batch_size):
            data = upsert_article_chunks(batch)
            success_count += len(data) or len(batch)
        print(json.dumps({"dry_run": False, "success_count": success_count, "failed_count": failed_count}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        failed_count = len(rows) - success_count
        print(json.dumps({"dry_run": False, "success_count": success_count, "failed_count": failed_count, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
