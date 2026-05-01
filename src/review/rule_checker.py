from __future__ import annotations

import re

from src.review.models import Issue, Severity


def run_rule_checker(text: str, article_type: str = "auto") -> list[Issue]:
    issues: list[Issue] = []

    def add(kind: str, span: str, problem: str, suggestion: str, severity: Severity = Severity.LOW) -> None:
        issues.append(
            Issue(
                id=f"issue_rule_{len(issues) + 1:03d}",
                type=kind,
                span=span,
                problem=problem,
                suggestion=suggestion,
                severity=severity,
            )
        )

    if re.search(r"[!！?？]{2,}", text):
        add("punctuation", "", "存在连续多个标点。", "建议统一为单个中文标点。")

    if re.search(r"[，。；：][,.;:]", text):
        add("punctuation", "", "中文标点和英文标点可能混用。", "建议统一中文新闻稿标点。")

    for match in re.finditer(r"([\u4e00-\u9fa5]{1,3})\1", text):
        add("wording", match.group(0), "疑似重复词。", "请确认是否为误输入。")

    for sentence in re.split(r"[。！？]", text):
        if len(sentence) > 120:
            add("grammar", sentence[:80], "句子过长，影响阅读。", "建议拆分为两到三句。", Severity.MEDIUM)
            break

    if text.count("“") != text.count("”"):
        add("punctuation", "“/”", "引号可能未闭合。", "请检查直接引语或标题引用。", Severity.MEDIUM)

    if text.count("（") != text.count("）") or text.count("(") != text.count(")"):
        add("punctuation", "括号", "括号可能未闭合。", "请检查补充说明或英文括号。", Severity.MEDIUM)

    if re.search(r"(圆满成功|高度重视|热烈反响|深刻领会)", text):
        add("style", "", "存在较强宣传化或空泛表述。", "建议替换为具体事实或现场信息。")

    if article_type in {"meeting_news", "会议新闻"}:
        for keyword, label in [("月", "时间"), ("会议室", "地点"), ("参加", "参会人员")]:
            if keyword not in text:
                add("element", "", f"会议新闻可能缺少{label}信息。", f"建议补齐{label}。", Severity.MEDIUM)

    return issues
