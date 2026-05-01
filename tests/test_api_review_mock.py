from fastapi.testclient import TestClient
from src.api.app import app


def test_review_mock_response():
    c = TestClient(app)
    payload = {
        'title': '测试标题',
        'draft_text': '4月28日上午召开交流会。',
        'article_type': 'auto',
        'options': {
            'retriever': 'bm25',
            'llm_provider': 'mock',
            'enable_rule_check': True,
            'enable_retrieval': True,
            'enable_llm': True,
            'enable_diff': True
        }
    }
    r = c.post('/api/v1/review', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 'request_id' in data
    assert 'status' in data
    assert 'original_text' in data
    assert 'retrieval_results' in data
    assert 'llm_review_result' in data
    assert 'diff_ops' in data
