from src.review.models import DisplayMode, EditType
from src.review.semantic_diff import build_semantic_diff


def test_semantic_diff_marks_reorder():
    original = "AI辅导员建设专题交流会"
    revised = "AI辅导员专题建设交流会"
    edits = build_semantic_diff(original, revised)
    assert edits
    assert edits[0].type in {EditType.REORDER, EditType.WORDING}
    assert edits[0].display_mode in {DisplayMode.SEMANTIC_REPLACE, DisplayMode.REPLACE}


def test_semantic_diff_marks_punctuation():
    edits = build_semantic_diff("老师们同学们参加了会议。", "老师们、同学们参加了会议。")
    assert any(item.type == EditType.PUNCTUATION for item in edits)


def test_semantic_diff_add_delete():
    assert any(item.type == EditType.ADD for item in build_semantic_diff("会议召开。", "会议召开。王老师参加。"))
    assert any(item.type == EditType.DELETE for item in build_semantic_diff("会议召开，现场气氛热烈。", "会议召开。"))
