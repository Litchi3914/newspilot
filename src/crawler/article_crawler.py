from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from src.crawler.polite_request import polite_get, get_response_text
from src.utils.hash_utils import sha256_text
from src.utils.time_utils import now_iso


def crawl_article_html(url: str, category: str = "") -> dict | None:
    resp = polite_get(url)
    if not resp:
        return None
    html = get_response_text(resp)
    article_id = sha256_text(url)[:16]
    html_path = Path("data/raw_html") / f"{article_id}.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    soup = BeautifulSoup(html, "lxml")
    title = ""
    if soup.select_one("h1"):
        title = soup.select_one("h1").get_text(" ", strip=True)
    elif soup.title:
        title = soup.title.get_text(" ", strip=True)

    return {
        "article_id": article_id,
        "url": url,
        "source_site": urlparse(url).netloc,
        "category": category,
        "title": title,
        "publish_date": "",
        "html_path": str(html_path).replace("\\", "/"),
        "html_hash": sha256_text(html),
        "crawl_time": now_iso(),
        "status": "success",
    }
