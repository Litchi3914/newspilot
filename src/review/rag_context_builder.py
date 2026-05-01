from __future__ import annotations

from typing import Any

from src.review.models import RagReference


def normalize_rag_references(raw_refs: list[dict[str, Any]] | None) -> list[RagReference]:
    refs: list[RagReference] = []
    for i, item in enumerate(raw_refs or [], start=1):
        refs.append(
            RagReference(
                id=f"ref_{i:03d}",
                source=str(item.get("source") or item.get("source_site") or "history_article"),
                title=str(item.get("title") or ""),
                chunk=str(item.get("chunk") or item.get("chunk_text") or item.get("text") or ""),
                score=float(item.get("score") or 0.0),
            )
        )
    return refs
