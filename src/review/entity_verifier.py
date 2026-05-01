from __future__ import annotations

from dataclasses import dataclass

from src.review.models import SensitiveEntityType, Severity


@dataclass
class EntityVerification:
    risk_level: Severity
    reason: str
    suggested_check: str


VERIFY_GUIDE = {
    SensitiveEntityType.PERSON_NAME: ("涉及人名或称谓，需人工核验。", "核对会议通知、签到表或官方人员信息。"),
    SensitiveEntityType.ORGANIZATION: ("正式机构名称需要核验，避免旧称或简称误写。", "核对学校官网或正式通知。"),
    SensitiveEntityType.DEPARTMENT: ("正式部门名称需要核验。", "核对学校官网部门名称或会议通知。"),
    SensitiveEntityType.TITLE_OR_POSITION: ("职务和称谓属于事实敏感项。", "核对官方职务、发文材料或活动名单。"),
    SensitiveEntityType.TIME: ("时间属于事实敏感项。", "核对活动通知、日程或现场记录。"),
    SensitiveEntityType.LOCATION: ("地点属于事实敏感项。", "核对会议通知或场地安排。"),
    SensitiveEntityType.NUMBER: ("数字、比例、届次等需要核验。", "核对原始统计、获奖文件或通知。"),
    SensitiveEntityType.MEETING_NAME: ("会议名称属于事实性名称，不应自动改写。", "核对会议通知或活动方案。"),
    SensitiveEntityType.ACTIVITY_NAME: ("活动名称属于事实性名称，不应自动改写。", "核对活动通知或宣传材料。"),
    SensitiveEntityType.QUOTE: ("直接引语需要确认是否为准确原话。", "核对采访记录或录音文字。"),
}


def verify_entity(entity: str, entity_type: SensitiveEntityType, article_type: str = "auto") -> EntityVerification:
    reason, suggested = VERIFY_GUIDE.get(
        entity_type,
        ("该内容可能涉及事实准确性，建议人工确认。", "核对原始材料或权威来源。"),
    )
    high_risk = {
        SensitiveEntityType.PERSON_NAME,
        SensitiveEntityType.TITLE_OR_POSITION,
        SensitiveEntityType.NUMBER,
        SensitiveEntityType.MEETING_NAME,
        SensitiveEntityType.ACTIVITY_NAME,
        SensitiveEntityType.QUOTE,
    }
    risk = Severity.HIGH if entity_type in high_risk else Severity.MEDIUM
    return EntityVerification(risk_level=risk, reason=reason, suggested_check=suggested)
