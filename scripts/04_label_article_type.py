import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import pandas as pd

from src.labeling.article_type_rules import classify_article
from src.storage.jsonl_writer import read_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/clean_jsonl/articles_clean.jsonl")
    parser.add_argument("--output", default="data/structured/articles_labeled.csv")
    args = parser.parse_args()

    rows = []
    for r in read_jsonl(args.input):
        pred = classify_article(r.get("title", ""), r.get("category", ""), r.get("body_clean", ""))
        rows.append({
            "article_id": r.get("article_id", ""),
            "title": r.get("title", ""),
            "category": r.get("category", ""),
            "article_type": pred["article_type"],
            "type_confidence": pred["type_confidence"],
            "label_method": "rule_based",
            "rules_hit": "|".join(pred["rules_hit"]),
        })
    pd.DataFrame(rows).to_csv(args.output, index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()

