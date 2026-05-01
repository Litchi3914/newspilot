from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class ArticleType(str, Enum):
    AUTO = "auto"
    MEETING_NEWS = "meeting_news"
    ACTIVITY_NEWS = "activity_news"
    ACHIEVEMENT_NEWS = "achievement_news"
    PROFILE_NEWS = "profile_news"
    NOTICE_NEWS = "notice_news"
    NEW_MEDIA_POST = "new_media_post"


class ReviewMode(str, Enum):
    LIGHT = "light"
    STANDARD = "standard"
    STRICT = "strict"


class EditType(str, Enum):
    PUNCTUATION = "punctuation"
    WORDING = "wording"
    GRAMMAR = "grammar"
    REORDER = "reorder"
    DELETE = "delete"
    ADD = "add"
    STYLE = "style"
    STRUCTURE = "structure"
    TITLE = "title"
    FACTUAL_KEEP = "factual_keep"
    FACTUAL_RISK = "factual_risk"


class DisplayMode(str, Enum):
    REPLACE = "replace"
    INSERT = "insert"
    DELETE = "delete"
    SEMANTIC_REPLACE = "semantic_replace"
    COMMENT_ONLY = "comment_only"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SensitiveEntityType(str, Enum):
    PERSON_NAME = "person_name"
    ORGANIZATION = "organization"
    DEPARTMENT = "department"
    TITLE_OR_POSITION = "title_or_position"
    TIME = "time"
    LOCATION = "location"
    NUMBER = "number"
    MEETING_NAME = "meeting_name"
    ACTIVITY_NAME = "activity_name"
    AWARD_NAME = "award_name"
    POLICY_DOCUMENT = "policy_document"
    QUOTE = "quote"
    LEADER_ORDER = "leader_order"
    OTHER = "other"


class ReviewRequest(BaseModel):
    text: str
    article_type: ArticleType = ArticleType.AUTO
    review_mode: ReviewMode = ReviewMode.STANDARD
    enable_rag: bool = True
    enable_sensitive_check: bool = True
    enable_semantic_diff: bool = True
    metadata: Optional[dict[str, Any]] = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("text is required")
        return text


class ReviewSummary(BaseModel):
    overall_quality: str = "medium"
    main_changes: list[str] = Field(default_factory=list)
    needs_human_review: bool = False


class EditOperation(BaseModel):
    id: str
    type: EditType
    source_text: str = ""
    target_text: str = ""
    reason: str = ""
    confidence: float = 0.0
    display_mode: DisplayMode = DisplayMode.REPLACE
    risk_level: Severity = Severity.LOW
    start_char: Optional[int] = None
    end_char: Optional[int] = None


class Issue(BaseModel):
    id: str
    type: str
    span: str = ""
    problem: str
    suggestion: str = ""
    severity: Severity = Severity.MEDIUM


class SensitiveEntity(BaseModel):
    id: str
    entity: str
    type: SensitiveEntityType
    span: str = ""
    risk_level: Severity = Severity.MEDIUM
    reason: str
    suggested_check: str = ""


class RagReference(BaseModel):
    id: str
    source: str = "history_article"
    title: str = ""
    chunk: str = ""
    score: float = 0.0


class ReviewResult(BaseModel):
    version: str = "review_result_v1"
    source_text: str
    revised_text: str
    summary: ReviewSummary = Field(default_factory=ReviewSummary)
    edit_operations: list[EditOperation] = Field(default_factory=list)
    issues: list[Issue] = Field(default_factory=list)
    sensitive_entities: list[SensitiveEntity] = Field(default_factory=list)
    rag_references: list[RagReference] = Field(default_factory=list)
