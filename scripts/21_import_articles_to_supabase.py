from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from src.storage.article_store import clean_date, clean_text, upsert_articles


def map_article(row: dict[str, Any]) -> dict[str, Any] | None:
    source_url = clean_text(row.get("url") or row.get("source_url"))
    title = clean_text(row.get("title"))
    if not source_url or not title:
        return None

    author = clean_text(row.get("author") or row.get("reporter") or row.get("correspondent") or row.get("editor"))
    metadata = {
        "article_id": clean_text(row.get("article_id")),
        "source_site": clean_text(row.get("source_site")),
        "editor": clean_text(row.get("editor")),
        "reporter": clean_text(row.get("reporter")),
        "correspondent": clean_text(row.get("correspondent")),
        "reviewer": clean_text(row.get("reviewer")),
        "article_type": clean_text(row.get("article_type")),
        "type_confidence": clean_text(row.get("type_confidence")),
        "crawl_time": clean_text(row.get("crawl_time")),
        "parse_time": clean_text(row.get("parse_time")),
        "status": clean_text(row.get("status")),
    }
    return {
        "source_url": source_url,
        "title": title,
        "publish_date": clean_date(row.get("publish_date") or row.get("publish_time")),
        "department": clean_text(row.get("department")),
        "category": clean_text(row.get("category")),
        "author": author,
        "content": clean_text(row.get("body_clean") or row.get("content")),
        "metadata": {k: v for k, v in metadata.items() if v is not None},
    }


def read_rows(path: Path, limit: int | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            mapped = map_article(raw)
            if mapped:
                rows.append(mapped)
            if limit and len(rows) >= limit:
                break
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Import article metadata/content to Supabase.")
    parser.add_argument("--input", default="data/structured/articles_structured.csv")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    rows = read_rows(ROOT / args.input, args.limit)
    print(json.dumps({"input": args.input, "preview_count": len(rows), "sample": rows[:1]}, ensure_ascii=False, indent=2))

    if args.dry_run:
        print(json.dumps({"dry_run": True, "would_upsert": len(rows)}, ensure_ascii=False, indent=2))
        return 0

    try:
        data = upsert_articles(rows)
        print(json.dumps({"dry_run": False, "success_count": len(data) or len(rows), "failed_count": 0}, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"dry_run": False, "success_count": 0, "failed_count": len(rows), "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
