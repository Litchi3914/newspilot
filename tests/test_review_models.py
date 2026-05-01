from src.review.models import ArticleType, ReviewRequest, ReviewResult


def test_review_request_contract():
    req = ReviewRequest(text="会议在水产楼 B205 召开。", article_type=ArticleType.MEETING_NEWS)
    assert req.article_type == ArticleType.MEETING_NEWS


def test_review_result_contract():
    result = ReviewResult(source_text="原文", revised_text="修订文")
    data = result.model_dump()
    assert data["version"] == "review_result_v1"
    assert "edit_operations" in data
    assert "sensitive_entities" in data
