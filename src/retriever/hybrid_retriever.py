from src.retriever.base import BaseRetriever
class HybridRetriever(BaseRetriever):
    def __init__(self,bm25,vector,bm25_weight:float=0.7,vector_weight:float=0.3):
        self.bm25=bm25; self.vector=vector; self.bm25_weight=bm25_weight; self.vector_weight=vector_weight
    def build(self,chunks:list[dict]): self.bm25.build(chunks); self.vector.build(chunks)
    def save(self,path:str): self.bm25.save(path)
    def load(self,path:str): self.bm25.load(path)
    def search(self,query:str,top_k:int=5,filters:dict|None=None)->list[dict]:
        a=self.bm25.search(query,top_k=top_k*3,filters=filters); b=self.vector.search(query,top_k=top_k*3,filters=filters)
        m={}
        for x in a: m[x['chunk_id']]={**x,'score':x.get('score',0.0)*self.bm25_weight}
        for x in b:
            cid=x['chunk_id']
            if cid in m: m[cid]['score']+=x.get('score',0.0)*self.vector_weight
            else: m[cid]={**x,'score':x.get('score',0.0)*self.vector_weight}
        out=list(m.values()); out.sort(key=lambda x:x.get('score',0.0),reverse=True)
        return out[:top_k]
