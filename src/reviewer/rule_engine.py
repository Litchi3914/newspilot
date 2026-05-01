from __future__ import annotations
import re
from src.labeling.article_type_rules import classify_article
from src.review.element_checker import ElementChecker

class ReviewRuleEngine:
    def __init__(self):
        self.checker = ElementChecker()
    def review(self, title: str, text: str, article_type: str | None = None) -> dict:
        pred = classify_article(title=title, category='', body_clean=text)
        detected = article_type or pred['article_type']
        e = self.checker.check(text=text, article_type=detected)
        language_issues=[]
        if re.search(r'[!！]{2,}', text):
            language_issues.append({'problem':'感叹号过多','suggestion':'建议减少宣传腔语气符号'})
        if len(text)>0 and max((len(x) for x in text.split('。') if x), default=0) > 120:
            language_issues.append({'problem':'句子过长','suggestion':'建议拆分长句，增强可读性'})
        structure_issues=[]
        lead=(text.split('\n')[0] if text.strip() else '')
        if len(lead)<80:
            structure_issues.append({'problem':'导语信息可能不足','suggestion':'建议补齐时间、地点、主体、主题'})
        fact_risks=[]
        if re.search(r'(\d+\.?\d*%|\d{4}年\d{1,2}月\d{1,2}日)', text):
            fact_risks.append({'risk':'含日期/数据，请人工复核事实准确性'})
        main_problems=[]
        for x in e['checks']:
            if not x['passed']:
                main_problems.append(f"缺少{x['element']}")
        main_problems += [x['problem'] for x in language_issues[:1]] + [x['problem'] for x in structure_issues[:1]]
        score = max(50, 100 - 5*len(main_problems))
        return {
            'detected_type': detected,
            'review_summary': {
                'overall_score': score,
                'main_problems': main_problems,
                'overall_suggestion': '建议先补齐缺失要素，再优化导语和长句表达。' if main_problems else '整体质量较好，可做轻度润色。'
            },
            'element_check': [
                {
                    'element': c['element'],
                    'status': 'present' if c['passed'] else 'missing',
                    'evidence': c.get('evidence',''),
                    'suggestion': c.get('suggestion','')
                } for c in e['checks']
            ],
            'language_issues': language_issues,
            'structure_issues': structure_issues,
            'fact_risks': fact_risks,
        }
