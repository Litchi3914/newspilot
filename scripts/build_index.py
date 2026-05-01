import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
import argparse
from src.knowledge_base.builder import NewsKnowledgeBase

def main():
    p=argparse.ArgumentParser(); p.add_argument('--retriever',default='bm25'); p.add_argument('--chunks',default='data/chunks/article_chunks.jsonl'); p.add_argument('--out',default='data/indexes/index.json')
    a=p.parse_args(); kb=NewsKnowledgeBase(retriever_name=a.retriever); kb.build(a.chunks); kb.save(a.out); print('index_saved',a.out)
if __name__=='__main__': main()
