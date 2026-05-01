import re

NOISE_PATTERNS = [
    r"上一篇", r"下一篇", r"友情链接", r"版权所有", r"点击量", r"打印", r"关闭",
]


def clean_text(text: str) -> str:
    t = text.replace("\u3000", " ")
    t = re.sub(r"[\x00-\x1f\x7f]", "", t)
    for p in NOISE_PATTERNS:
        t = re.sub(p, "", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{2,}", "\n", t)
    t = re.sub(r"\s+([，。！？；：])", r"\1", t)
    return t.strip()
