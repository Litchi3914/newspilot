from src.review.entity_extractor import extract_sensitive_entities


def test_extract_sensitive_entities_minimum():
    text = "4月28日上午，智芯辅导员工作室 AI 辅导员建设专题交流会在水产楼B205会议室召开。王运涛老师参加会议。"
    entities = extract_sensitive_entities(text)
    types = {item.type.value for item in entities}
    assert "time" in types
    assert "location" in types
    assert "meeting_name" in types
    assert "person_name" in types
