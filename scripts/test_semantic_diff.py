import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.review.semantic_diff import build_semantic_diff


def main():
    original = "智芯辅导员工作室 AI 辅导员建设专题交流会在水产楼 B205 会议室召开。"
    revised = "AI 辅导员建设专题交流会在水产楼 B205 会议室召开，智芯辅导员工作室全体成员参加会议。"
    edits = [x.model_dump() for x in build_semantic_diff(original, revised)]
    print(json.dumps(edits, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
