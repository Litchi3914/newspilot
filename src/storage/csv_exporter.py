import pandas as pd

from src.storage.jsonl_writer import read_jsonl


DEFAULT_FIELDS = [
    "article_id", "url", "source_site", "category", "title", "publish_date",
    "editor", "reporter", "correspondent", "reviewer", "body_clean",
    "crawl_time", "parse_time", "status", "article_type", "type_confidence",
]


def export_jsonl_to_csv(input_path: str, output_path: str, fields: list[str] | None = None) -> None:
    rows = read_jsonl(input_path)
    cols = fields or DEFAULT_FIELDS
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    df = df[cols]
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
