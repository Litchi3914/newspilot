from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from src.core.supabase_client import SupabaseConfigError, get_supabase_client


def check_table(client, table_name: str) -> tuple[bool, str | None]:
    try:
        client.table(table_name).select("id").limit(1).execute()
        return True, None
    except Exception as exc:
        return False, f"Cannot access table {table_name}: {exc}"


def main() -> int:
    load_dotenv(ROOT / ".env")
    checks: dict[str, bool] = {
        "env": False,
        "client": False,
        "review_records_table": False,
        "articles_table": False,
        "article_chunks_table": False,
    }
    errors: list[str] = []

    try:
        client = get_supabase_client()
        checks["env"] = True
        checks["client"] = True
    except SupabaseConfigError as exc:
        errors.append(str(exc))
        print(json.dumps({"ready": False, "checks": checks, "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    for table_name, check_name in [
        ("review_records", "review_records_table"),
        ("articles", "articles_table"),
        ("article_chunks", "article_chunks_table"),
    ]:
        ok, error = check_table(client, table_name)
        checks[check_name] = ok
        if error:
            errors.append(error)

    ready = all(checks.values())
    print(json.dumps({"ready": ready, "checks": checks, "errors": errors}, ensure_ascii=False, indent=2))
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
