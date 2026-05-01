import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
from src.crawler.category_crawler import crawl_category_links, save_category_links
from src.crawler.article_crawler import crawl_article_html
from src.storage.jsonl_writer import write_jsonl

CATEGORY_MAP = {
    "学校要闻": "https://news.hzau.edu.cn/xxyw.htm",
    "院部新闻": "https://news.hzau.edu.cn/ybxw.htm",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="学校要闻")
    parser.add_argument("--max-pages", type=int, default=2)
    parser.add_argument("--max-articles", type=int, default=20)
    parser.add_argument("--save-html", action="store_true")
    args = parser.parse_args()

    url = CATEGORY_MAP.get(args.category, args.category)
    links = crawl_category_links(url, max_pages=args.max_pages)[: args.max_articles]
    save_category_links(args.category, links, "data/raw_jsonl/category_article_links.jsonl")

    if args.save_html:
        raws = []
        for link in links:
            row = crawl_article_html(link, category=args.category)
            if row:
                raws.append(row)
        write_jsonl("data/raw_jsonl/articles_raw.jsonl", raws, append=False)


if __name__ == "__main__":
    main()

