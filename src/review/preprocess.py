from __future__ import annotations

import re


def normalize_text(text: str) -> str:
    text = (text or "").replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def split_paragraphs(text: str) -> list[str]:
    return [line.strip() for line in normalize_text(text).split("\n") if line.strip()]
