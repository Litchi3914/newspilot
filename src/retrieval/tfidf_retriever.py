from __future__ import annotations

from collections import Counter
import math
import re
from typing import Any


def _simple_tokens(text: str) -> list[str]:
    text = text or ""
    zh_chars = [c for c in text if "\u4e00" <= c <= "\u9fff"]
    words = re.findall(r"[A-Za-z0-9_]+", text.lower())
    return words + zh_chars


def _cosine_counter(a: Counter[str], b: Counter[str]) -> float:
    keys = set(a) | set(b)
    dot = sum(a[k] * b[k] for k in keys)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _match_reason(query: str, item: dict[str, Any]) -> str:
    q_tokens = set(_simple_tokens(query))
    t_tokens = _simple_tokens(item.get("chunk_text", ""))
    overlap = [x for x in t_tokens if x in q_tokens]
    top_overlap = ",".join(list(dict.fromkeys(overlap))[:6]) if overlap else "关键词匹配较弱"
    atype = item.get("article_type", "未知类型")
    return f"同属{atype}候选，命中关键词：{top_overlap}。"


class TfidfRetriever:
    def __init__(self, chunks: list[dict[str, Any]]):
        self.chunks = chunks
        self._use_sklearn = False
        self._matrix = None
        self._vectorizer = None
        self._fallback_vecs: list[Counter[str]] = []

        docs = [c.get("chunk_text", "") for c in chunks]
        try:
            import jieba  # type: ignore
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore

            def jieba_tokenize(text: str) -> list[str]:
                segs = [w.strip() for w in jieba.cut(text or "") if w.strip()]
                return segs or _simple_tokens(text)

            self._vectorizer = TfidfVectorizer(tokenizer=jieba_tokenize, lowercase=False)
            self._matrix = self._vectorizer.fit_transform(docs)
            self._use_sklearn = True
        except Exception:
            self._fallback_vecs = [Counter(_simple_tokens(x)) for x in docs]

    def search(self, query: str, top_k: int = 5, dedupe_article: bool = True) -> list[dict[str, Any]]:
        scored: list[tuple[float, dict[str, Any]]] = []

        if self._use_sklearn and self._vectorizer is not None and self._matrix is not None:
            qv = self._vectorizer.transform([query])
            sims = (self._matrix @ qv.T).toarray().reshape(-1)
            for idx, s in enumerate(sims):
                scored.append((float(s), self.chunks[idx]))
        else:
            q = Counter(_simple_tokens(query))
            for idx, c in enumerate(self.chunks):
                s = _cosine_counter(q, self._fallback_vecs[idx])
                scored.append((s, c))

        scored.sort(key=lambda x: x[0], reverse=True)

        results: list[dict[str, Any]] = []
        seen_articles: set[str] = set()
        rank = 1
        for score, item in scored:
            if dedupe_article:
                aid = item.get("article_id", "")
                if aid in seen_articles:
                    continue
                seen_articles.add(aid)
            row = {
                "rank": rank,
                "score": round(float(score), 6),
                "chunk_id": item.get("chunk_id", ""),
                "article_id": item.get("article_id", ""),
                "title": item.get("title", ""),
                "category": item.get("category", ""),
                "article_type": item.get("article_type", ""),
                "publish_date": item.get("publish_date", ""),
                "url": item.get("url", ""),
                "chunk_text": item.get("chunk_text", ""),
                "match_reason": _match_reason(query, item),
            }
            results.append(row)
            rank += 1
            if len(results) >= top_k:
                break
        return results
