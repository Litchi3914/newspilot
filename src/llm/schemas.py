from __future__ import annotations
from typing import Any, List
from pydantic import BaseModel


class ReviewSummary(BaseModel):
    overall_score: int
    main_problems: List[str]
    overall_suggestion: str


class ReviewIssue(BaseModel):
    category: str
    severity: str
    paragraph_index: int
    original_text: str
    problem: str
    suggestion: str


class FactRisk(BaseModel):
    text: str
    risk: str
    action: str


class LLMReviewResult(BaseModel):
    detected_type: str
    review_summary: ReviewSummary
    issues: List[ReviewIssue]
    revised_title: str
    revised_text: str
    fact_risks: List[FactRisk]


def default_review_result(article_type: str = '其他') -> dict:
    return {
        'detected_type': article_type,
        'review_summary': {
            'overall_score': 75,
            'main_problems': [],
            'overall_suggestion': '建议结合规则检查结果进一步人工复核。'
        },
        'issues': [],
        'revised_title': '',
        'revised_text': '',
        'fact_risks': [],
    }


def _normalize_issues(raw_issues: Any) -> list[dict]:
    if not isinstance(raw_issues, list):
        return []
    normalized: list[dict] = []
    for i, item in enumerate(raw_issues):
        if isinstance(item, dict):
            normalized.append({
                'category': str(item.get('category') or '语言表达'),
                'severity': str(item.get('severity') or 'medium'),
                'paragraph_index': int(item.get('paragraph_index') or 0),
                'original_text': str(item.get('original_text') or ''),
                'problem': str(item.get('problem') or item.get('issue') or ''),
                'suggestion': str(item.get('suggestion') or item.get('advice') or ''),
            })
        elif isinstance(item, str):
            normalized.append({
                'category': '语言表达',
                'severity': 'medium',
                'paragraph_index': i,
                'original_text': '',
                'problem': item,
                'suggestion': '请根据问题描述进行针对性修订。',
            })
    return normalized


def _normalize_fact_risks(raw: Any) -> list[dict]:
    if not isinstance(raw, list):
        return []
    out: list[dict] = []
    for item in raw:
        if isinstance(item, dict):
            out.append({
                'text': str(item.get('text') or ''),
                'risk': str(item.get('risk') or '待核实'),
                'action': str(item.get('action') or 'manual_check'),
            })
        elif isinstance(item, str):
            out.append({'text': item, 'risk': '待核实', 'action': 'manual_check'})
    return out


def _normalize_data(data: dict, fallback: dict) -> dict:
    result = {**fallback, **(data or {})}

    summary = result.get('review_summary')
    if not isinstance(summary, dict):
        summary = {}
    main_problems = summary.get('main_problems')
    if isinstance(main_problems, str):
        main_problems = [main_problems]
    if not isinstance(main_problems, list):
        main_problems = []
    result['review_summary'] = {
        'overall_score': int(summary.get('overall_score') or fallback['review_summary']['overall_score']),
        'main_problems': [str(x) for x in main_problems],
        'overall_suggestion': str(summary.get('overall_suggestion') or fallback['review_summary']['overall_suggestion']),
    }

    result['issues'] = _normalize_issues(result.get('issues'))
    result['fact_risks'] = _normalize_fact_risks(result.get('fact_risks'))
    result['detected_type'] = str(result.get('detected_type') or fallback.get('detected_type') or '其他')
    result['revised_title'] = str(result.get('revised_title') or '')
    result['revised_text'] = str(result.get('revised_text') or '')
    return result


def validate_or_fallback(data: dict, fallback: dict) -> tuple[dict, bool, str]:
    try:
        normalized = _normalize_data(data, fallback)
        obj = LLMReviewResult.model_validate(normalized)
        return obj.model_dump(), True, ''
    except Exception as exc:  # noqa: BLE001
        return fallback, False, str(exc)
