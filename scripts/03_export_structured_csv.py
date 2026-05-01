import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse

from src.storage.csv_exporter import export_jsonl_to_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/clean_jsonl/articles_clean.jsonl")
    parser.add_argument("--output", default="data/structured/articles_structured.csv")
    args = parser.parse_args()
    export_jsonl_to_csv(args.input, args.output)


if __name__ == "__main__":
    main()

