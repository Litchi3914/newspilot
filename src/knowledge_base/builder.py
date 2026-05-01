from src.knowledge_base.base import KnowledgeBase
from src.retriever.tfidf_retriever import TfidfRetriever
from src.retriever.bm25_retriever import BM25Retriever
from src.retriever.vector_retriever import VectorRetriever
from src.retriever.hybrid_retriever import HybridRetriever
from src.storage.jsonl_writer import read_jsonl

class NewsKnowledgeBase(KnowledgeBase):
    def __init__(self, retriever_name: str = 'bm25'):
        self.retriever_name=retriever_name
        self.retriever=self._make(retriever_name)
    def _make(self,name:str):
        if name=='tfidf': return TfidfRetriever()
        if name=='bm25': return BM25Retriever()
        if name=='vector': return VectorRetriever()
        if name=='hybrid': return HybridRetriever(BM25Retriever(),VectorRetriever())
        return BM25Retriever()
    def build(self,chunks_path:str): self.retriever.build(read_jsonl(chunks_path))
    def save(self,index_path:str): self.retriever.save(index_path)
    def load(self,index_path:str): self.retriever.load(index_path)
    def search(self,query:str,top_k:int=5,filters:dict|None=None): return self.retriever.search(query,top_k=top_k,filters=filters)

