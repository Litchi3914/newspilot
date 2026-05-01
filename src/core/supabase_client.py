from __future__ import annotations

import os
from functools import lru_cache
from typing import Any


class SupabaseConfigError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url:
        raise SupabaseConfigError("Missing SUPABASE_URL")
    if not key:
        raise SupabaseConfigError("Missing SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY")

    try:
        from supabase import create_client
    except ImportError as exc:
        raise SupabaseConfigError("Missing Python package: supabase") from exc

    return create_client(url, key)
