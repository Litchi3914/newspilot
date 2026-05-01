from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from src.api.schemas.errors import APIError

class ReviewOptions(BaseModel):
    retriever: Literal['bm25','tfidf','hybrid'] = 'bm25'
    llm_provider: Literal['mock','openai'] = 'openai'
    enable_rule_check: bool = True
    enable_retrieval: bool = True
    enable_llm: bool = True
    enable_diff: bool = True
    fast_mode: bool = True

class ReviewRequest(BaseModel):
    request_id: Optional[str] = None
    title: Optional[str] = None
    draft_text: Optional[str] = None
    content: Optional[str] = None
    source: str = 'web'
    review_mode: str = 'standard'
    article_type: str = 'auto'
    options: ReviewOptions = Field(default_factory=ReviewOptions)

    @model_validator(mode='after')
    def fill_text(self):
        if not (self.draft_text and self.draft_text.strip()):
            self.draft_text = (self.content or '').strip()
        if not self.title:
            self.title = ''
        return self

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        x = v.strip()
        if x and len(x) < 2:
            raise ValueError('title too short')
        if len(x) > 100:
            raise ValueError('title too long')
        return x

    @field_validator('draft_text')
    @classmethod
    def validate_draft_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        x = value.strip()
        if x and len(x) < 20:
            raise ValueError('draft_text too short')
        if len(x) > 10000:
            raise ValueError('draft_text too long')
        return x

class RetrievalResult(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    article_type: Optional[str] = None
    chunk_text: Optional[str] = None
    score: Optional[float] = None
    match_reason: Optional[str] = None

class DiffOp(BaseModel):
    type: Literal['insert','delete','replace','equal','comment','warning']
    paragraph_index: Optional[int] = None
    original: Optional[str] = None
    revised: Optional[str] = None
    comment: Optional[str] = None
    category: Optional[str] = None
    reason: Optional[str] = None
    severity: Optional[str] = None

class ReviewMetadata(BaseModel):
    retriever: str = 'bm25'
    llm_provider: str = 'openai'
    enable_rule_check: bool = True
    enable_retrieval: bool = True
    enable_llm: bool = True
    enable_diff: bool = True
    fast_mode: bool = True
    revision_effective: Optional[bool] = None
    input_char_count: Optional[int] = None
    output_char_count: Optional[int] = None
    latency_ms: Optional[int] = None

class ReviewData(BaseModel):
    original: Dict[str, str] = Field(default_factory=dict)
    revised: Dict[str, str] = Field(default_factory=dict)
    diff: List[DiffOp] = Field(default_factory=list)
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    edit_operations: List[Dict[str, Any]] = Field(default_factory=list)
    sensitive_entities: List[Dict[str, Any]] = Field(default_factory=list)
    rag_references: List[Dict[str, Any]] = Field(default_factory=list)

class ReviewResponse(BaseModel):
    request_id: str
    status: Literal['success','partial_success','failed','error']
    api_version: str = 'v1'
    pipeline_version: str = '0.1.0'

    detected_type: Optional[str] = None
    original_title: Optional[str] = None
    original_text: str
    revised_title: Optional[str] = None
    revised_text: Optional[str] = None

    rule_check_result: Dict[str, Any] = Field(default_factory=dict)
    retrieval_results: List[RetrievalResult] = Field(default_factory=list)
    llm_review_result: Dict[str, Any] = Field(default_factory=dict)
    diff_ops: List[DiffOp] = Field(default_factory=list)
    review_result: Dict[str, Any] = Field(default_factory=dict)
    edit_operations: List[Dict[str, Any]] = Field(default_factory=list)
    issues: List[Dict[str, Any]] = Field(default_factory=list)
    sensitive_entities: List[Dict[str, Any]] = Field(default_factory=list)
    rag_references: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)

    data: Optional[ReviewData] = None
    error: Optional[APIError] = None
    meta: Optional[ReviewMetadata] = None

    errors: List[APIError] = Field(default_factory=list)
    metadata: ReviewMetadata = Field(default_factory=ReviewMetadata)
