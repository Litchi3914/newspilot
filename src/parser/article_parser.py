import re
from pathlib import Path
from bs4 import BeautifulSoup

from src.parser.clean_text import clean_text
from src.utils.time_utils import now_iso


def _extract_publish_date(text: str) -> str:
    m = re.search(r"(20\d{2}[-年/.]\d{1,2}[-月/.]\d{1,2})", text)
    if not m:
        return ""
    d = m.group(1).replace("年", "-").replace("月", "-").replace(".", "-").replace("/", "-").replace("日", "")
    parts = [p for p in d.split("-") if p]
    if len(parts) == 3:
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    return ""


def _extract_meta(meta_text: str, label: str) -> str:
    m = re.search(label + r"[:：]\s*([^\s，。；;|]+)", meta_text)
    return m.group(1).strip() if m else ""


def _pick_title(soup: BeautifulSoup) -> str:
    for sel in ["h1", ".arti_title", ".article-title", ".v_news_content h1"]:
        node = soup.select_one(sel)
        if node:
            txt = clean_text(node.get_text(" ", strip=True))
            if txt:
                return txt
    if soup.title:
        return clean_text(soup.title.get_text(" ", strip=True).split("-")[0])
    return ""


def parse_article_html(raw: dict) -> dict:
    html = Path(raw["html_path"]).read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")

    title = _pick_title(soup)

    body_node = (
        soup.select_one("#vsb_content")
        or soup.select_one(".v_news_content")
        or soup.select_one(".article-content")
        or soup.select_one("article")
        or soup.body
    )

    paragraphs = []
    if body_node:
        for p in body_node.select("p"):
            txt = clean_text(p.get_text(" ", strip=True))
            if txt and len(txt) >= 8 and txt not in {"上一篇", "下一篇"}:
                paragraphs.append(txt)

    if not paragraphs and body_node:
        text = clean_text(body_node.get_text("\n", strip=True))
        paragraphs = [x.strip() for x in text.split("\n") if len(x.strip()) >= 8]

    full_text = "\n".join(paragraphs)
    page_text = soup.get_text(" ", strip=True)
    publish_date = _extract_publish_date(page_text)

    clean = {
        "article_id": raw["article_id"],
        "url": raw["url"],
        "source_site": raw.get("source_site", ""),
        "category": raw.get("category", ""),
        "title": title,
        "publish_date": publish_date,
        "editor": _extract_meta(page_text, "编辑"),
        "reporter": _extract_meta(page_text, "记者"),
        "correspondent": _extract_meta(page_text, "通讯员"),
        "reviewer": _extract_meta(page_text, "审核"),
        "body_raw": full_text,
        "body_clean": clean_text(full_text),
        "paragraphs": paragraphs,
        "image_captions": [clean_text(x.get_text(" ", strip=True)) for x in body_node.select("figcaption")][:10] if body_node else [],
        "crawl_time": raw.get("crawl_time", ""),
        "parse_time": now_iso(),
        "status": "parsed",
    }

    if not clean["title"] or len(clean["body_clean"]) < 80 or not clean["url"]:
        clean["status"] = "parse_failed"
    return clean
