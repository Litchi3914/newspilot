from __future__ import annotations
from typing import Any, Dict, List, Optional
from src.llm.base import BaseLLMClient
from src.llm.schemas import default_review_result

CANDIDATES = ['会议新闻','活动纪实','科研成果','人才培养','对外交流','人物通讯','通知公告','荣誉喜报','其他']

class MockLLMClient(BaseLLMClient):
    def classify_article_type(self, title: str, draft_text: str, candidate_types: Optional[List[str]] = None) -> Dict[str, Any]:
        types = candidate_types or CANDIDATES
        t = title + ' ' + draft_text
        if any(k in t for k in ['召开','会议','交流会','研讨会']):
            detected = '会议新闻'
        elif any(k in t for k in ['活动','开展','志愿']):
            detected = '活动纪实'
        elif any(k in t for k in ['研究','论文','成果']):
            detected = '科研成果'
        else:
            detected = types[-1]
        return {'detected_type': detected, 'confidence': 0.78, 'reason': 'mock rule'}

    def review_article(self, title: str, draft_text: str, article_type: str, references: Optional[List[Dict[str, Any]]] = None, rule_check_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        out = default_review_result(article_type)
        out['review_summary'] = {
            'overall_score': 82,
            'main_problems': ['导语信息不够完整','部分表述偏口语化'] if len(draft_text) < 400 else ['可进一步压缩背景介绍'],
            'overall_suggestion': '建议补充地点并压缩背景介绍。'
        }
        out['issues'] = [
            {
                'category': '新闻要素',
                'severity': 'medium',
                'paragraph_index': 0,
                'original_text': '',
                'problem': '导语中地点信息不够明确',
                'suggestion': '建议在导语中补充活动地点。'
            }
        ]
        out['fact_risks'] = [
            {'text': '人名/职务', 'risk': '关键信息需人工核实', 'action': 'manual_check'}
        ]
        return out

    def revise_article(self, title: str, draft_text: str, article_type: str, references: Optional[List[Dict[str, Any]]] = None, issues: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        out = default_review_result(article_type)
        out['revised_title'] = title.strip() or '【待补充】标题'
        extra = '' if '地点' in draft_text else '\n【待补充】请补充活动地点。'
        out['revised_text'] = f"【Mock 修订稿】{draft_text.strip()}{extra}"
        return out
