from typing import Any


def build_chunks(article: dict[str, Any], article_type: str = "") -> list[dict[str, Any]]:
    paragraphs = article.get("paragraphs", []) or []
    if not paragraphs and article.get("body_clean"):
        paragraphs = [article["body_clean"]]

    chunks: list[dict[str, Any]] = []
    i = 0
    chunk_index = 1
    while i < len(paragraphs):
        block = paragraphs[i:i + 3]
        text = "\n".join(block).strip()
        if len(text) < 120 and i + 3 < len(paragraphs):
            block = paragraphs[i:i + 4]
            text = "\n".join(block).strip()
            i += 4
        else:
            i += 3
        chunks.append({
            "chunk_id": f"{article['article_id']}_chunk_{chunk_index:03d}",
            "article_id": article["article_id"],
            "title": article.get("title", ""),
            "category": article.get("category", ""),
            "article_type": article_type,
            "publish_date": article.get("publish_date", ""),
            "chunk_index": chunk_index,
            "chunk_type": "body",
            "chunk_text": text,
            "url": article.get("url", ""),
        })
        chunk_index += 1

    return chunks
