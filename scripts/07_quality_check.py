import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import argparse
import csv
from collections import Counter, defaultdict

from src.storage.jsonl_writer import read_jsonl


def safe_len(text: str) -> int:
    return len((text or "").strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", default="data/clean_jsonl/articles_clean.jsonl")
    parser.add_argument("--chunks", default="data/chunks/article_chunks.jsonl")
    parser.add_argument("--labeled", default="data/structured/articles_labeled.csv")
    parser.add_argument("--md-out", default="data/logs/quality_report.md")
    parser.add_argument("--csv-out", default="data/logs/quality_report.csv")
    args = parser.parse_args()

    clean_rows = read_jsonl(args.clean)
    chunk_rows = read_jsonl(args.chunks)

    article_total = len(clean_rows)
    parsed_success = sum(1 for r in clean_rows if r.get("status") == "parsed")
    parsed_failed = article_total - parsed_success

    body_lens = [safe_len(r.get("body_clean", "")) for r in clean_rows]
    para_counts = [len(r.get("paragraphs", []) or []) for r in clean_rows]

    avg_body = (sum(body_lens) / article_total) if article_total else 0
    min_body = min(body_lens) if body_lens else 0
    max_body = max(body_lens) if body_lens else 0
    avg_paras = (sum(para_counts) / article_total) if article_total else 0

    chunks_per_article = defaultdict(int)
    chunk_lens = []
    for c in chunk_rows:
        aid = c.get("article_id", "")
        if aid:
            chunks_per_article[aid] += 1
        chunk_lens.append(safe_len(c.get("chunk_text", "")))

    avg_chunks = (sum(chunks_per_article.values()) / article_total) if article_total else 0
    short_chunks = sum(1 for x in chunk_lens if x < 100)
    long_chunks = sum(1 for x in chunk_lens if x > 1000)

    missing = {
        "title_missing": sum(1 for r in clean_rows if not (r.get("title") or "").strip()),
        "body_missing": sum(1 for r in clean_rows if not (r.get("body_clean") or "").strip()),
        "publish_date_missing": sum(1 for r in clean_rows if not (r.get("publish_date") or "").strip()),
        "url_missing": sum(1 for r in clean_rows if not (r.get("url") or "").strip()),
        "source_site_missing": sum(1 for r in clean_rows if not (r.get("source_site") or "").strip()),
    }
    body_lt_100 = sum(1 for x in body_lens if x < 100)

    type_counter = Counter()
    labeled_path = Path(args.labeled)
    if labeled_path.exists():
        with labeled_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                t = (row.get("article_type") or "").strip() or "UNKNOWN"
                type_counter[t] += 1

    success_rate = (parsed_success / article_total * 100) if article_total else 0

    lines = [
        "# 质量验收报告",
        "",
        "## 总览",
        f"- 文章总数：{article_total}",
        f"- 解析成功数：{parsed_success}",
        f"- 解析失败数：{parsed_failed}",
        f"- 解析成功率：{success_rate:.2f}%",
        "",
        "## 正文统计",
        f"- 平均正文字数：{avg_body:.2f}",
        f"- 最短正文字数：{min_body}",
        f"- 最长正文字数：{max_body}",
        f"- 正文小于 100 字：{body_lt_100}",
        f"- 平均段落数：{avg_paras:.2f}",
        "",
        "## Chunk 统计",
        f"- 平均 chunk 数：{avg_chunks:.2f}",
        f"- 过短 chunk 数（<100字）：{short_chunks}",
        f"- 过长 chunk 数（>1000字）：{long_chunks}",
        "",
        "## 字段缺失统计",
        f"- 标题缺失：{missing['title_missing']}",
        f"- 正文缺失：{missing['body_missing']}",
        f"- 发布时间缺失：{missing['publish_date_missing']}",
        f"- URL 缺失：{missing['url_missing']}",
        f"- source_site 缺失：{missing['source_site_missing']}",
        "",
        "## 稿件类型分布",
    ]
    if type_counter:
        total_labeled = sum(type_counter.values())
        for k, v in type_counter.most_common():
            lines.append(f"- {k}: {v} ({(v/total_labeled*100):.2f}%)")
    else:
        lines.append("- 无 labeled 数据")

    md_out = Path(args.md_out)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    metrics = [
        ("article_total", article_total),
        ("parsed_success", parsed_success),
        ("parsed_failed", parsed_failed),
        ("parse_success_rate_pct", round(success_rate, 2)),
        ("avg_body_len", round(avg_body, 2)),
        ("min_body_len", min_body),
        ("max_body_len", max_body),
        ("body_lt_100", body_lt_100),
        ("avg_paragraph_count", round(avg_paras, 2)),
        ("avg_chunks_per_article", round(avg_chunks, 2)),
        ("short_chunks_lt_100", short_chunks),
        ("long_chunks_gt_1000", long_chunks),
        ("title_missing", missing["title_missing"]),
        ("body_missing", missing["body_missing"]),
        ("publish_date_missing", missing["publish_date_missing"]),
        ("url_missing", missing["url_missing"]),
        ("source_site_missing", missing["source_site_missing"]),
    ]
    for t, v in type_counter.items():
        metrics.append((f"article_type_{t}", v))

    csv_out = Path(args.csv_out)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerows(metrics)


if __name__ == "__main__":
    main()
