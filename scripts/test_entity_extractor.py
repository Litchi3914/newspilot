import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.review.entity_extractor import extract_sensitive_entities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="examples/sample_draft.txt")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    entities = [x.model_dump() for x in extract_sensitive_entities(text)]
    print(json.dumps(entities, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
