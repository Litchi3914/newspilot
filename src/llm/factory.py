from __future__ import annotations
import os
from pathlib import Path
from src.llm.base import BaseLLMClient
from src.llm.mock_client import MockLLMClient
from src.llm.openai_client import OpenAILLMClient


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.lower() in {'1', 'true', 'yes', 'on'}


def load_llm_config(config_path: str = 'configs/llm.yaml') -> dict:
    cfg = {
        'provider': 'mock',
        'enable_real_call': False,
        'openai': {
            'model': 'gpt-4.1-mini',
            'base_url': '',
            'api_key_env': 'OPENAI_API_KEY',
            'timeout_seconds': 60,
            'max_retries': 2,
            'temperature': 0.2,
        },
        'logging': {'enabled': True, 'log_path': 'data/logs/llm_call_log.csv'},
    }
    p = Path(config_path)
    if p.exists():
        try:
            import yaml  # type: ignore
            y = yaml.safe_load(p.read_text(encoding='utf-8')) or {}
            cfg.update({k: v for k, v in y.items() if k in cfg and k not in {'openai', 'logging'}})
            if isinstance(y.get('openai'), dict):
                cfg['openai'].update(y['openai'])
            if isinstance(y.get('logging'), dict):
                cfg['logging'].update(y['logging'])
        except Exception:
            pass

    cfg['provider'] = os.getenv('LLM_PROVIDER', cfg['provider'])
    cfg['enable_real_call'] = _bool_env('LLM_ENABLE_REAL_CALL', cfg['enable_real_call'])
    cfg['openai']['model'] = os.getenv('OPENAI_MODEL', cfg['openai']['model'])
    cfg['openai']['base_url'] = os.getenv('OPENAI_BASE_URL', cfg['openai'].get('base_url', ''))
    cfg['openai']['api_key_env'] = os.getenv('LLM_API_KEY_ENV', cfg['openai'].get('api_key_env', 'OPENAI_API_KEY'))
    cfg['openai']['timeout_seconds'] = int(os.getenv('LLM_TIMEOUT_SECONDS', cfg['openai']['timeout_seconds']))
    cfg['openai']['max_retries'] = int(os.getenv('LLM_MAX_RETRIES', cfg['openai']['max_retries']))
    cfg['openai']['temperature'] = float(os.getenv('LLM_TEMPERATURE', cfg['openai']['temperature']))
    cfg['logging']['log_path'] = os.getenv('LLM_LOG_PATH', cfg['logging']['log_path'])
    return cfg


def create_llm_client(config: dict) -> BaseLLMClient:
    provider = (config.get('provider') or 'mock').lower()
    if provider == 'mock':
        return MockLLMClient()
    if provider == 'openai':
        if not config.get('enable_real_call', False):
            return MockLLMClient()
        ocfg = config.get('openai', {})
        return OpenAILLMClient(
            model=ocfg.get('model', 'gpt-4.1-mini'),
            enable_real_call=True,
            base_url=ocfg.get('base_url', ''),
            api_key_env=ocfg.get('api_key_env', 'OPENAI_API_KEY'),
            timeout_seconds=int(ocfg.get('timeout_seconds', 60)),
            max_retries=int(ocfg.get('max_retries', 2)),
            temperature=float(ocfg.get('temperature', 0.2)),
        )
    return MockLLMClient()
