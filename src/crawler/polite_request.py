import re
import random
import time
import requests
from loguru import logger

DEFAULT_HEADERS = {
    "User-Agent": "HZAU-News-KB-Research/0.1 (+for academic project)",
}

_MOJI_BAD = ["锘", "�", "瀛", "鏂", "鍗", "寮", "浼", "璁", "缁", "??"]


def _score_text(s: str) -> float:
    if not s:
        return -1e9
    cjk = sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")
    bad = sum(s.count(t) for t in _MOJI_BAD)
    ratio = cjk / max(len(s), 1)
    return cjk * 1.0 + ratio * 200 - bad * 30


def _decode_candidates(content: bytes, declared: str | None, apparent: str | None) -> str:
    cands = []
    for enc in [declared, apparent, "utf-8", "gb18030", "gbk", "gb2312", "big5"]:
        if not enc:
            continue
        try:
            txt = content.decode(enc, errors="replace")
            cands.append((enc, txt, _score_text(txt)))
        except Exception:
            continue
    # Repair common mojibake: utf-8 bytes decoded as gbk/latin1
    for enc in ["gbk", "gb18030", "latin1"]:
        try:
            tmp = content.decode(enc, errors="replace")
            repaired = tmp.encode(enc, errors="ignore").decode("utf-8", errors="ignore")
            cands.append((f"repair:{enc}->utf8", repaired, _score_text(repaired)))
        except Exception:
            continue
    if not cands:
        return content.decode("utf-8", errors="replace")
    cands.sort(key=lambda x: x[2], reverse=True)
    return cands[0][1]


def _decode_response(resp: requests.Response) -> str:
    declared = (resp.encoding or "").strip() or None
    apparent = (resp.apparent_encoding or "").strip() or None
    return _decode_candidates(resp.content, declared, apparent)


def polite_get(
    url: str,
    headers: dict | None = None,
    timeout: int = 10,
    interval: float = 1.5,
    max_retries: int = 3,
) -> requests.Response | None:
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    for idx in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=merged_headers, timeout=timeout)
            time.sleep(random.uniform(interval, interval + 0.8))
            if resp.status_code == 200:
                resp._decoded_text = _decode_response(resp)  # type: ignore[attr-defined]
                return resp
            logger.warning("Request failed status={} url={} try={}", resp.status_code, url, idx)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Request error url={} try={} err={}", url, idx, exc)
    return None


def get_response_text(resp: requests.Response) -> str:
    cached = getattr(resp, "_decoded_text", None)
    if isinstance(cached, str):
        return cached
    return _decode_response(resp)
