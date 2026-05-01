from src.labeling.article_type_rules import classify_article


def test_classifier_basic():
    r = classify_article("学校召开工作推进会", "学校要闻", "会上强调...与会人员...")
    assert r["article_type"] == "会议新闻"
