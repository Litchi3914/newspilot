import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import csv

from src.parser.article_parser import parse_article_html
from src.storage.jsonl_writer import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw_jsonl/articles_raw.jsonl")
    parser.add_argument("--output", default="data/clean_jsonl/articles_clean.jsonl")
    args = parser.parse_args()

    raws = read_jsonl(args.input)
    cleans = []
    failed = []
    for raw in raws:
        row = parse_article_html(raw)
        cleans.append(row)
        if row.get("status") != "parsed":
            failed.append({"article_id": row.get("article_id"), "url": row.get("url"), "reason": "quality_check_failed"})

    write_jsonl(args.output, cleans, append=False)
    with open("data/logs/parse_failed.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["article_id", "url", "reason"])
        writer.writeheader()
        writer.writerows(failed)


if __name__ == "__main__":
    main()

