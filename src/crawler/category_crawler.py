import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from src.crawler.polite_request import polite_get, get_response_text
from src.storage.jsonl_writer import write_jsonl

ARTICLE_RE = re.compile(r"/info/\d+/\d+\.htm")


def crawl_category_links(category_url: str, max_pages: int = 5) -> list[str]:
    links: set[str] = set()
    page_urls = [category_url]
    for i in range(2, max_pages + 1):
        if category_url.endswith(".htm"):
            page_urls.append(category_url.replace(".htm", f"/{i}.htm"))
    for page_url in page_urls:
        resp = polite_get(page_url)
        if not resp:
            continue
        soup = BeautifulSoup(get_response_text(resp), "lxml")
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            if ARTICLE_RE.search(href):
                links.add(urljoin(page_url, href))
    return sorted(links)


def save_category_links(category: str, links: list[str], path: str) -> None:
    rows = [{"category": category, "url": x} for x in links]
    write_jsonl(path, rows, append=False)
