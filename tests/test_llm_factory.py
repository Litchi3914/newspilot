from src.llm.factory import create_llm_client
from src.llm.mock_client import MockLLMClient
from src.llm.openai_client import OpenAILLMClient


def test_factory_mock():
    c = create_llm_client({'provider': 'mock', 'enable_real_call': False})
    assert isinstance(c, MockLLMClient)


def test_factory_openai_guard_returns_mock_when_disabled():
    c = create_llm_client({'provider': 'openai', 'enable_real_call': False, 'openai': {}})
    assert isinstance(c, MockLLMClient)


def test_factory_openai_when_enabled():
    c = create_llm_client({'provider': 'openai', 'enable_real_call': True, 'openai': {'model': 'gpt-4.1-mini'}})
    assert isinstance(c, OpenAILLMClient)
