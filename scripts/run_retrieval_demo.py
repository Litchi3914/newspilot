import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import argparse, json
from src.knowledge_base.builder import NewsKnowledgeBase

def main():
    p=argparse.ArgumentParser(); p.add_argument('--query',default='信息学院召开人工智能专题交流会'); p.add_argument('--top_k',type=int,default=5); p.add_argument('--retriever',default='bm25'); p.add_argument('--chunks',default='data/chunks/article_chunks.jsonl')
    a=p.parse_args(); kb=NewsKnowledgeBase(retriever_name=a.retriever); kb.build(a.chunks); rs=kb.search(a.query,top_k=a.top_k)
    Path('outputs').mkdir(exist_ok=True)
    Path('outputs/retrieval_result.json').write_text(json.dumps({'query':a.query,'results':rs},ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# Retrieval Result','',f"query: {a.query}", '']
    for i,r in enumerate(rs,1): md.append(f"{i}. {r.get('title','')} | {r.get('score',0)} | {r.get('url','')}")
    Path('outputs/retrieval_result.md').write_text('\n'.join(md),encoding='utf-8')
if __name__=='__main__': main()
