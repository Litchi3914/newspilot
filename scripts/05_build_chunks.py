import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import pandas as pd

from src.chunking.article_chunker import build_chunks
from src.storage.jsonl_writer import read_jsonl, write_jsonl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/clean_jsonl/articles_clean.jsonl")
    parser.add_argument("--labels", default="data/structured/articles_labeled.csv")
    parser.add_argument("--output", default="data/chunks/article_chunks.jsonl")
    args = parser.parse_args()

    type_map = {}
    if pd.io.common.file_exists(args.labels):
        df = pd.read_csv(args.labels)
        type_map = {str(r["article_id"]): str(r["article_type"]) for _, r in df.iterrows()}

    out = []
    for a in read_jsonl(args.input):
        out.extend(build_chunks(a, type_map.get(a.get("article_id", ""), "")))

    write_jsonl(args.output, out, append=False)


if __name__ == "__main__":
    main()

