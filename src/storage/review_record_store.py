from __future__ import annotations

import os
from typing import Any

from src.core.supabase_client import SupabaseConfigError, get_supabase_client
from src.utils.logger import logger


def is_review_record_storage_enabled() -> bool:
    return os.getenv("ENABLE_REVIEW_RECORD_STORAGE", "false").strip().lower() == "true"


def save_review_record(
    *,
    request_id: str | None = None,
    title: str | None,
    input_text: str,
    revised_text: str | None,
    issues: list[Any] | dict[str, Any] | None,
    diff_result: list[Any] | dict[str, Any] | None,
    raw_result: dict[str, Any] | None,
    options: dict[str, Any] | None,
    client_meta: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if not is_review_record_storage_enabled():
        return None

    try:
        client = get_supabase_client()
    except SupabaseConfigError as exc:
        logger.warning(f"Review record storage skipped: {exc}")
        return None

    row = {
        "request_id": request_id,
        "title": title or "",
        "input_text": input_text,
        "revised_text": revised_text,
        "issues": issues,
        "diff_result": diff_result,
        "raw_result": raw_result,
        "options": options,
        "client_meta": client_meta or {},
    }

    try:
        result = client.table("review_records").insert(row).execute()
        data = getattr(result, "data", None)
        if data:
            return data[0]
        return {"inserted": True}
    except Exception as exc:
        logger.error(f"Failed to save review record: {exc}")
        return None
