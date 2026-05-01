from src.llm.mock_client import MockLLMClient
from src.llm.schemas import validate_or_fallback, default_review_result


def test_mock_client_outputs():
    c = MockLLMClient()
    t = '4月28日上午召开交流会'
    x = c.classify_article_type('标题', t)
    assert isinstance(x, dict)
    at = x.get('detected_type', '其他')
    r = c.review_article('标题', t, at)
    v = c.revise_article('标题', t, at)
    merged = {**default_review_result(at), **r, **v}
    out, ok, _ = validate_or_fallback(merged, default_review_result(at))
    assert ok
    assert out.get('revised_text', '')
