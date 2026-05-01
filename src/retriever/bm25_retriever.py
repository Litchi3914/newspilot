from __future__ import annotations
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
import json
from src.retriever.base import BaseRetriever

def _tok(t: str) -> list[str]:
    zh = [c for c in (t or "") if "\u4e00" <= c <= "\u9fff"]
    en = re.findall(r"[A-Za-z0-9_]+", (t or "").lower())
    return en + zh

class BM25Retriever(BaseRetriever):
    def __init__(self, k1: float = 1.5, b: float = 0.75, title_weight: float = 1.3):
        self.k1=k1; self.b=b; self.title_weight=title_weight
        self.chunks=[]; self.docs=[]; self.df=defaultdict(int); self.avgdl=1.0
    def build(self, chunks: list[dict]):
        self.chunks=chunks; self.docs=[]; self.df=defaultdict(int)
        for c in chunks:
            text=((c.get('title','')+' ')*int(self.title_weight*1))+c.get('chunk_text','')
            toks=_tok(text); self.docs.append(toks)
            for t in set(toks): self.df[t]+=1
        self.avgdl=sum(len(d) for d in self.docs)/max(len(self.docs),1)
    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.chunks, ensure_ascii=False), encoding='utf-8')
    def load(self, path: str):
        self.chunks=json.loads(Path(path).read_text(encoding='utf-8')); self.build(self.chunks)
    def _idf(self, t: str)->float:
        n=len(self.docs); df=self.df.get(t,0)
        return math.log((n-df+0.5)/(df+0.5)+1)
    def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]:
        q=_tok(query); out=[]
        for i,c in enumerate(self.chunks):
            if filters and filters.get('article_type') and c.get('article_type')!=filters['article_type']:
                continue
            tf=Counter(self.docs[i]); dl=len(self.docs[i]); s=0.0
            for t in q:
                f=tf.get(t,0)
                if not f: continue
                s += self._idf(t) * (f*(self.k1+1)) / (f + self.k1*(1-self.b+self.b*dl/self.avgdl))
            out.append({**c,'score':round(float(s),6),'match_reason':'BM25关键词相关'})
        out.sort(key=lambda x:x['score'], reverse=True)
        return out[:top_k]
