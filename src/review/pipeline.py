from __future__ import annotations

from typing import Any

from src.review.entity_extractor import extract_sensitive_entities
from src.review.llm_reviewer import normalize_llm_issues, normalize_llm_summary
from src.review.models import Issue, ReviewResult, Severity
from src.review.preprocess import normalize_text
from src.review.rag_context_builder import normalize_rag_references
from src.review.rule_checker import run_rule_checker
from src.review.semantic_diff import build_semantic_diff


def _merge_issues(rule_issues: list[Issue], llm_issues: list[Issue]) -> list[Issue]:
    out: list[Issue] = []
    for issue in [*rule_issues, *llm_issues]:
        out.append(issue.model_copy(update={"id": f"issue_{len(out) + 1:03d}"}))
    return out


def _fact_risk_issues(llm_result: dict[str, Any] | None) -> list[Issue]:
    issues: list[Issue] = []
    for item in (llm_result or {}).get("fact_risks") or []:
        if isinstance(item, dict):
            text = str(item.get("text") or "")
            risk = str(item.get("risk") or "事实项需人工核验。")
        else:
            text = str(item)
            risk = "事实项需人工核验。"
        issues.append(
            Issue(
                id=f"issue_fact_{len(issues) + 1:03d}",
                type="factual_risk",
                span=text,
                problem=risk,
                suggestion="请核对原始通知、会议材料或权威来源，AI 不应擅自替换该事实项。",
                severity=Severity.HIGH,
            )
        )
    return issues


def build_review_result(
    source_text: str,
    revised_text: str,
    article_type: str = "auto",
    rag_references: list[dict[str, Any]] | None = None,
    rule_check_result: dict[str, Any] | None = None,
    llm_result: dict[str, Any] | None = None,
) -> ReviewResult:
    normalized_source = normalize_text(source_text)
    normalized_revised = normalize_text(revised_text or source_text)
    rule_issues = run_rule_checker(normalized_source, article_type=article_type)
    llm_issues = normalize_llm_issues(llm_result)
    fact_issues = _fact_risk_issues(llm_result)
    sensitive_entities = extract_sensitive_entities(
        source_text=normalized_source,
        revised_text=normalized_revised,
        article_type=article_type,
    )
    summary = normalize_llm_summary(llm_result)
    if sensitive_entities:
        summary.needs_human_review = True
    if not summary.main_changes:
        summary.main_changes = ["完成基础规则审查、敏感事实项识别和语义修订对齐。"]

    return ReviewResult(
        source_text=normalized_source,
        revised_text=normalized_revised,
        summary=summary,
        edit_operations=build_semantic_diff(
            source_text=normalized_source,
            revised_text=normalized_revised,
            llm_edit_operations=(llm_result or {}).get("edit_operations") or [],
        ),
        issues=_merge_issues([*rule_issues, *fact_issues], llm_issues),
        sensitive_entities=sensitive_entities,
        rag_references=normalize_rag_references(rag_references),
    )
