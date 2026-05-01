import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import argparse
from src.storage.jsonl_writer import read_jsonl, write_jsonl
from src.chunker.article_chunker import build_chunks
import csv

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--clean',default='data/clean_jsonl/articles_clean.jsonl')
    p.add_argument('--labels',default='data/structured/articles_labeled.csv')
    p.add_argument('--out',default='data/chunks/article_chunks.jsonl')
    p.add_argument('--report-csv',default='data/logs/chunk_quality_report.csv')
    p.add_argument('--report-md',default='data/logs/chunk_quality_report.md')
    a=p.parse_args()
    rows=read_jsonl(a.clean)
    type_map={}
    import pandas as pd
    if Path(a.labels).exists():
        df=pd.read_csv(a.labels); type_map={str(r['article_id']):str(r['article_type']) for _,r in df.iterrows()}
    out=[]
    for r in rows:
        out.extend(build_chunks(r, article_type=type_map.get(r.get('article_id',''),'')))
    write_jsonl(a.out,out,append=False)
    lens=[x.get('char_count',0) for x in out]
    short=sum(1 for x in lens if x<100); long=sum(1 for x in lens if x>1000)
    with open(a.report_csv,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f); w.writerow(['metric','value']); w.writerows([('chunk_total',len(out)),('short_lt_100',short),('long_gt_1000',long)])
    Path(a.report_md).write_text(f"# Chunk Quality\n\n- chunk_total: {len(out)}\n- short_lt_100: {short}\n- long_gt_1000: {long}\n",encoding='utf-8')

if __name__=='__main__': main()
