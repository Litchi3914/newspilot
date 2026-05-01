from __future__ import annotations

import re

from src.review.models import SensitiveEntity, SensitiveEntityType
from src.review.entity_verifier import verify_entity
from src.review.preprocess import normalize_text


PATTERNS: list[tuple[SensitiveEntityType, re.Pattern[str]]] = [
    (SensitiveEntityType.TIME, re.compile(r"(\d{4}年)?\d{1,2}月\d{1,2}日?(上午|下午|晚上)?|近日|当天|日前")),
    (SensitiveEntityType.LOCATION, re.compile(r"[\u4e00-\u9fa5A-Za-z0-9]+(?:楼|会议室|报告厅|教室|校区|馆|中心)[A-Za-z0-9\-]*")),
    (SensitiveEntityType.NUMBER, re.compile(r"\d+(?:\.\d+)?%?|\d+人|\d+项|第[一二三四五六七八九十\d]+届")),
    (SensitiveEntityType.MEETING_NAME, re.compile(r"[\u4e00-\u9fa5A-Za-z0-9 ]{4,40}(?:会议|交流会|座谈会|研讨会|推进会|培训会)")),
    (SensitiveEntityType.ACTIVITY_NAME, re.compile(r"[\u4e00-\u9fa5A-Za-z0-9 ]{4,40}(?:活动|比赛|赛事|讲座|仪式)")),
    (SensitiveEntityType.DEPARTMENT, re.compile(r"[\u4e00-\u9fa5]{2,30}(?:学院|处|中心|办公室|工作室|委员会|团委|学生会|本科生院|研究生院)")),
    (SensitiveEntityType.TITLE_OR_POSITION, re.compile(r"(书记|院长|副院长|主任|副主任|老师|辅导员|负责人|部长|主席)")),
    (SensitiveEntityType.PERSON_NAME, re.compile(r"[\u4e00-\u9fa5]{2,4}(?:老师|书记|院长|主任|辅导员)")),
    (SensitiveEntityType.QUOTE, re.compile(r"“[^”]{4,120}”")),
]


def _span_context(text: str, start: int, end: int, width: int = 16) -> str:
    return text[max(0, start - width) : min(len(text), end + width)]


def extract_sensitive_entities(
    source_text: str,
    revised_text: str = "",
    article_type: str = "auto",
) -> list[SensitiveEntity]:
    combined = normalize_text("\n".join(x for x in [source_text or "", revised_text or ""] if x))
    seen: set[tuple[str, SensitiveEntityType]] = set()
    entities: list[SensitiveEntity] = []

    for entity_type, pattern in PATTERNS:
        for match in pattern.finditer(combined):
            entity = match.group(0).strip()
            if not entity or (entity, entity_type) in seen:
                continue
            seen.add((entity, entity_type))
            verified = verify_entity(entity=entity, entity_type=entity_type, article_type=article_type)
            entities.append(
                SensitiveEntity(
                    id=f"entity_{len(entities) + 1:03d}",
                    entity=entity,
                    type=entity_type,
                    span=_span_context(combined, match.start(), match.end()),
                    risk_level=verified.risk_level,
                    reason=verified.reason,
                    suggested_check=verified.suggested_check,
                )
            )

    return entities
