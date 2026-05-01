import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import json
import re

from src.labeling.article_type_rules import classify_article
from src.review.element_checker import ElementChecker
from src.retrieval.tfidf_retriever import TfidfRetriever
from src.storage.jsonl_writer import read_jsonl


def build_issues(text: str, article_type: str, element_result: dict, similar_count: int) -> list[dict]:
    issues: list[dict] = []

    for item in element_result["checks"]:
        if not item["passed"]:
            issues.append(
                {
                    "type": "新闻要素",
                    "severity": "high",
                    "problem": f"缺少要素：{item['element']}",
                    "suggestion": item["suggestion"],
                }
            )

    lead = text.split("\n")[0] if text.strip() else ""
    if len(lead) < 80:
        issues.append({"type": "结构", "severity": "medium", "problem": "导语可能过短", "suggestion": "建议导语补齐时间、地点、主体和会议主题。"})
    if len(text) < 300:
        issues.append({"type": "内容", "severity": "medium", "problem": "正文可能偏短", "suggestion": "建议补充关键事实、过程和结果。"})

    if article_type == "会议新闻" and not re.search(r"(指出|强调|表示|介绍|交流|分享)", text):
        issues.append({"type": "内容", "severity": "medium", "problem": "会议内容展开不足", "suggestion": "建议补充会议发言、交流要点和结论。"})

    if similar_count == 0:
        issues.append({"type": "检索", "severity": "low", "problem": "未检索到相似范文", "suggestion": "建议扩充知识库数据规模。"})

    return issues


def to_markdown(report: dict) -> str:
    lines = [
        "# 新闻稿审阅报告",
        "",
        "## 1. 稿件类型判断",
        f"- 类型: {report['article_type']}",
        f"- 置信度: {report['article_type_confidence']}",
        "",
        "## 2. 新闻要素检查",
        f"- 通过/总数: {report['element_check']['passed']}/{report['element_check']['total']}",
        f"- 通过率: {report['element_check']['pass_rate']}",
    ]
    for x in report["element_check"]["items"]:
        lines.append(f"- {x['element']}: {'通过' if x['passed'] else '缺失'}")

    lines.extend(["", "## 3. 相似范文推荐"])
    if not report["similar_examples"]:
        lines.append("- 未检索到相似范文")
    else:
        for r in report["similar_examples"]:
            lines.append(f"- {r['title']} | {r['category']} | {r['article_type']} | {r['url']}")

    lines.extend(["", "## 4. 主要问题"])
    if not report["issues"]:
        lines.append("- 未发现明显问题")
    else:
        for i in report["issues"]:
            lines.append(f"- [{i['severity']}] {i['problem']}；建议：{i['suggestion']}")

    lines.extend([
        "",
        "## 5. 修改建议",
        f"- 标题: {report['suggestions']['title']}",
        f"- 导语: {report['suggestions']['lead']}",
        f"- 结构: {report['suggestions']['structure']}",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text", default="")
    parser.add_argument("--text-file", default="")
    parser.add_argument("--chunks", default="data/chunks/article_chunks.jsonl")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--out-json", default="data/demo_outputs/review_report.json")
    parser.add_argument("--out-md", default="data/demo_outputs/review_report.md")
    args = parser.parse_args()

    text = args.text.strip()
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8")
    if not text:
        raise ValueError("请提供 --text 或 --text-file")

    clf = classify_article(title=text[:40], category="", body_clean=text)
    article_type = clf["article_type"]

    checker = ElementChecker()
    element = checker.check(text=text, article_type=article_type)

    chunks = read_jsonl(args.chunks)
    retriever = TfidfRetriever(chunks)
    similar = retriever.search(query=text, top_k=args.top_k, dedupe_article=True)

    issues = build_issues(text=text, article_type=article_type, element_result=element, similar_count=len(similar))

    report = {
        "article_type": article_type,
        "article_type_confidence": clf["type_confidence"],
        "element_check": {
            "total": element["summary"]["total"],
            "passed": element["summary"]["passed"],
            "failed": element["summary"]["failed"],
            "pass_rate": element["summary"]["pass_rate"],
            "items": element["checks"],
        },
        "similar_examples": similar,
        "issues": issues,
        "suggestions": {
            "title": "建议标题突出会议主题和建设方向。",
            "lead": "建议导语补齐时间、地点、主体和会议主题。",
            "structure": "建议按照导语—会议背景—交流内容—指导意见—总结展望组织。",
        },
    }

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(to_markdown(report), encoding="utf-8")


if __name__ == "__main__":
    main()
