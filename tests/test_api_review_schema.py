import pytest
from pydantic import ValidationError
from src.api.schemas.review import ReviewRequest, ReviewResponse, DiffOp


def test_review_request_ok():
    x = ReviewRequest(draft_text='正文', options={'retriever':'bm25','llm_provider':'mock'})
    assert x.draft_text == '正文'


def test_review_request_empty_fail():
    with pytest.raises(ValidationError):
        ReviewRequest(draft_text='   ')


def test_retriever_invalid_fail():
    with pytest.raises(ValidationError):
        ReviewRequest(draft_text='正文', options={'retriever':'abc'})


def test_llm_provider_invalid_fail():
    with pytest.raises(ValidationError):
        ReviewRequest(draft_text='正文', options={'llm_provider':'xxx'})


def test_review_response_construct():
    r = ReviewResponse(request_id='x', status='success', original_text='a')
    assert r.request_id == 'x'


def test_diff_type_invalid_fail():
    with pytest.raises(ValidationError):
        DiffOp(type='bad')
