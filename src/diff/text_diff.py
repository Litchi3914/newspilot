from __future__ import annotations
import difflib

class TextDiffGenerator:
    def generate(self, original_text: str, revised_text: str, issues: list[dict] | None = None) -> list[dict]:
        ops=[]
        a=(original_text or '').split('\n')
        b=(revised_text or '').split('\n')
        sm=difflib.SequenceMatcher(a=a,b=b)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag=='equal':
                continue
            if tag=='replace':
                ops.append({'type':'replace','paragraph_index':i1,'original':'\n'.join(a[i1:i2]),'revised':'\n'.join(b[j1:j2]),'category':'语言规范','reason':'表达优化','severity':'low'})
            elif tag=='delete':
                ops.append({'type':'delete','paragraph_index':i1,'original':'\n'.join(a[i1:i2]),'revised':'','category':'结构','reason':'删除冗余内容','severity':'low'})
            elif tag=='insert':
                ops.append({'type':'insert','paragraph_index':i1,'original':'','revised':'\n'.join(b[j1:j2]),'category':'结构','reason':'补充必要信息','severity':'medium'})
        for it in (issues or [])[:3]:
            ops.append({'type':'comment','paragraph_index':0,'original':'','revised':'','category':it.get('type','新闻要素'),'reason':it.get('problem',''),'severity':it.get('severity','medium')})
        return ops
