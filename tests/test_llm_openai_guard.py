import os
import pytest
from src.llm.openai_client import OpenAILLMClient
from src.llm.errors import RealCallDisabledError, MissingAPIKeyError


def test_guard_block_when_disabled():
    c = OpenAILLMClient(enable_real_call=False)
    with pytest.raises(RealCallDisabledError):
        c._guard()


def test_guard_block_when_missing_key(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    c = OpenAILLMClient(enable_real_call=True)
    with pytest.raises(MissingAPIKeyError):
        c._guard()
