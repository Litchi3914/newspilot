from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from src.core.supabase_client import get_supabase_client


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def clean_date(value: Any) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    text = text[:10]
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def upsert_articles(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = list(rows)
    if not payload:
        return []
    result = get_supabase_client().table("articles").upsert(payload, on_conflict="source_url").execute()
    return getattr(result, "data", None) or []


def upsert_article_chunks(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = list(rows)
    if not payload:
        return []
    result = (
        get_supabase_client()
        .table("article_chunks")
        .upsert(payload, on_conflict="source_url,chunk_index")
        .execute()
    )
    return getattr(result, "data", None) or []
