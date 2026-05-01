import argparse
from src.storage.jsonl_writer import read_jsonl
import csv
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--clean',default='data/clean_jsonl/articles_clean.jsonl')
    p.add_argument('--chunks',default='data/chunks/article_chunks.jsonl')
    p.add_argument('--labeled',default='data/structured/articles_labeled.csv')
    p.add_argument('--md-out',default='data/logs/quality_report.md')
    p.add_argument('--csv-out',default='data/logs/quality_report.csv')
    a=p.parse_args()
    clean=read_jsonl(a.clean); chunks=read_jsonl(a.chunks)
    metrics=[('article_total',len(clean)),('chunk_total',len(chunks))]
    Path(a.csv_out).parent.mkdir(parents=True,exist_ok=True)
    with open(a.csv_out,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['metric','value']); w.writerows(metrics)
    Path(a.md_out).write_text(f"# Quality\n\n- article_total: {len(clean)}\n- chunk_total: {len(chunks)}\n",encoding='utf-8')
if __name__=='__main__': main()
