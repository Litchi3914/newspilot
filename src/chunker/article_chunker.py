from __future__ import annotations
from typing import Any


def _split_long_text(text: str, max_len: int = 800) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    start = 0
    while start < len(text):
        end = min(start + max_len, len(text))
        parts.append(text[start:end])
        start = end
    return parts


def build_chunks(article: dict[str, Any], article_type: str = "", min_len: int = 100, target_max: int = 800, hard_max: int = 1000) -> list[dict[str, Any]]:
    paras = [p.strip() for p in (article.get("paragraphs") or []) if p and p.strip()]
    if not paras:
        body = (article.get("body_clean") or "").strip()
        paras = [body] if body else []

    chunks: list[str] = []
    buf = ""
    for p in paras:
        if not buf:
            buf = p
            continue
        if len(buf) < min_len or len(buf) + 1 + len(p) <= target_max:
            buf += "\n" + p
        else:
            chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)

    normalized: list[str] = []
    for ch in chunks:
        if len(ch) > hard_max:
            normalized.extend(_split_long_text(ch, target_max))
        else:
            normalized.append(ch)

    out = []
    for i, ch in enumerate(normalized, start=1):
        out.append({
            "chunk_id": f"{article.get('article_id','unknown')}_chunk_{i:03d}",
            "article_id": article.get("article_id", ""),
            "title": article.get("title", ""),
            "article_type": article_type,
            "url": article.get("url", ""),
            "publish_time": article.get("publish_date", ""),
            "chunk_text": ch,
            "chunk_index": i,
            "char_count": len(ch),
            "metadata": {
                "source_site": article.get("source_site", ""),
                "column": article.get("category", ""),
            },
            "category": article.get("category", ""),
            "publish_date": article.get("publish_date", ""),
        })
    return out
