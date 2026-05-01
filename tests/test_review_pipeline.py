from src.review.pipeline import build_review_result


def test_build_review_result_contains_required_fields():
    source = "4月28日上午，专题交流会在水产楼B205会议室召开。王运涛老师参加会议。"
    revised = "4月28日上午，专题交流会在水产楼 B205 会议室召开。王运涛老师参加会议。"
    result = build_review_result(source_text=source, revised_text=revised, article_type="meeting_news")
    assert result.version == "review_result_v1"
    assert result.revised_text
    assert result.edit_operations
    assert result.issues is not None
    assert result.sensitive_entities
    assert result.summary.needs_human_review is True
