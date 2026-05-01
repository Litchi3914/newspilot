import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json

from src.review.element_checker import ElementChecker


def to_markdown(result: dict) -> str:
    s = result["summary"]
    lines = [
        "# 新闻要素检查结果",
        "",
        f"- 稿件类型: {result['article_type']}",
        f"- 通过/总数: {s['passed']}/{s['total']}",
        f"- 通过率: {s['pass_rate']}",
        "",
        "## 明细",
    ]
    for c in result["checks"]:
        status = "通过" if c["passed"] else "缺失"
        lines.append(f"- {c['element']}: {status}")
        lines.append(f"  证据: {c['evidence'] or '-'}")
        lines.append(f"  建议: {c['suggestion'] or '-'}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="")
    parser.add_argument("--text-file", default="")
    parser.add_argument("--article-type", default="会议新闻")
    parser.add_argument("--out-json", default="data/demo_outputs/element_check_result.json")
    parser.add_argument("--out-md", default="data/demo_outputs/element_check_result.md")
    args = parser.parse_args()

    text = args.text.strip()
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    if not text:
        raise ValueError("请提供 --text 或 --text-file")

    checker = ElementChecker()
    result = checker.check(text=text, article_type=args.article_type)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(to_markdown(result), encoding="utf-8")


if __name__ == "__main__":
    main()
