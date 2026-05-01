from __future__ import annotations

from typing import Any

from src.review.models import Issue, ReviewSummary, Severity


def normalize_llm_summary(llm_result: dict[str, Any] | None) -> ReviewSummary:
    raw = (llm_result or {}).get("review_summary") or {}
    main = raw.get("main_changes") or raw.get("main_problems") or []
    if isinstance(main, str):
        main = [main]
    return ReviewSummary(
        overall_quality="medium",
        main_changes=[str(x) for x in main],
        needs_human_review=bool((llm_result or {}).get("fact_risks")),
    )


def normalize_llm_issues(llm_result: dict[str, Any] | None) -> list[Issue]:
    issues: list[Issue] = []
    for item in (llm_result or {}).get("issues") or []:
        if not isinstance(item, dict):
            continue
        issues.append(
            Issue(
                id=f"issue_llm_{len(issues) + 1:03d}",
                type=str(item.get("category") or item.get("type") or "style"),
                span=str(item.get("original_text") or item.get("span") or ""),
                problem=str(item.get("problem") or item.get("message") or "需进一步人工判断。"),
                suggestion=str(item.get("suggestion") or ""),
                severity=Severity(str(item.get("severity") or "medium")) if str(item.get("severity") or "medium") in {"low", "medium", "high"} else Severity.MEDIUM,
            )
        )
    return issues
