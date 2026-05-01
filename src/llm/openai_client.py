from __future__ import annotations
import json
import os
from typing import Any, Dict, List, Optional
from src.llm.base import BaseLLMClient
from src.llm.errors import MissingAPIKeyError, RealCallDisabledError
from src.llm.schemas import default_review_result


class OpenAILLMClient(BaseLLMClient):
    def __init__(
        self,
        model: str = 'gpt-4.1-mini',
        enable_real_call: bool = False,
        base_url: str = '',
        api_key_env: str = 'OPENAI_API_KEY',
        timeout_seconds: int = 60,
        max_retries: int = 2,
        temperature: float = 0.2,
    ):
        self.model = model
        self.enable_real_call = enable_real_call
        self.base_url = (base_url or '').strip()
        self.api_key_env = api_key_env
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.temperature = temperature

    def _guard(self) -> str:
        if not self.enable_real_call:
            raise RealCallDisabledError('LLM_ENABLE_REAL_CALL is false.')
        api_key = os.getenv(self.api_key_env, '').strip()
        if not api_key:
            raise MissingAPIKeyError(f'{self.api_key_env} is missing.')
        return api_key

    def _parse_json(self, text: str, fallback: dict) -> dict:
        if not text:
            return fallback
        text = text.strip()
        try:
            return json.loads(text)
        except Exception:
            # try extract fenced json
            if '```' in text:
                parts = text.split('```')
                for part in parts:
                    part = part.strip()
                    if part.startswith('json'):
                        part = part[4:].strip()
                    try:
                        return json.loads(part)
                    except Exception:
                        pass
            return fallback

    def _chat_completion(self, prompt: str, fallback: dict) -> dict:
        api_key = self._guard()
        try:
            from openai import OpenAI  # type: ignore
            kwargs = {'api_key': api_key}
            if self.base_url:
                kwargs['base_url'] = self.base_url
            client = OpenAI(**kwargs)

            resp = client.chat.completions.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': 'You are a strict JSON generator. Return only JSON object.'},
                    {'role': 'user', 'content': prompt},
                ],
                temperature=self.temperature,
                timeout=self.timeout_seconds,
            )
            txt = ''
            if resp and resp.choices:
                msg = resp.choices[0].message
                txt = getattr(msg, 'content', '') or ''
            return self._parse_json(txt, fallback)
        except Exception as exc:  # noqa: BLE001
            return {
                'success': False,
                'error_type': type(exc).__name__,
                'error_message': str(exc),
                'fallback_used': True,
                **fallback,
            }

    def classify_article_type(self, title: str, draft_text: str, candidate_types: Optional[List[str]] = None) -> Dict[str, Any]:
        fb = {'detected_type': '其他', 'confidence': 0.0, 'reason': 'fallback'}
        prompt = f"Classify article type and return JSON: {{detected_type, confidence, reason}}. title={title} text={draft_text[:2000]}"
        return self._chat_completion(prompt, fb)

    def review_article(self, title: str, draft_text: str, article_type: str, references: Optional[List[Dict[str, Any]]] = None, rule_check_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        fb = default_review_result(article_type)
        prompt = (
            '你是高校新闻稿审稿助手。只输出合法 JSON 对象，不要输出 Markdown。'
            '字段必须兼容 default_review_result: detected_type, review_summary, issues, revised_title, revised_text, fact_risks。'
            '不得擅自修改人名、单位、职务、时间、地点、会议名称、活动名称、数字、奖项、引用语。'
            '发现事实风险时写入 fact_risks 并建议人工核验。'
            f'type={article_type} title={title} text={draft_text[:3500]} references={references} rules={rule_check_result}'
        )
        return self._chat_completion(prompt, fb)

    def revise_article(self, title: str, draft_text: str, article_type: str, references: Optional[List[Dict[str, Any]]] = None, issues: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        fb = default_review_result(article_type)
        fb['revised_title'] = title
        fb['revised_text'] = draft_text + '\n【待补充】'
        prompt = (
            '请在不改变事实项的前提下修订高校新闻稿，并只输出合法 JSON。'
            '必须包含 revised_title、revised_text、issues、fact_risks。'
            '人名、单位、职务、时间、地点、会议/活动名称、数字、奖项、引用语不得凭空替换。'
            f'type={article_type} title={title} text={draft_text[:3500]} issues={issues} references={references}'
        )
        return self._chat_completion(prompt, fb)
