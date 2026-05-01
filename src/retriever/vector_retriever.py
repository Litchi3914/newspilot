from src.retriever.base import BaseRetriever
class VectorRetriever(BaseRetriever):
    def build(self, chunks: list[dict]): self.chunks=chunks
    def save(self, path: str): pass
    def load(self, path: str): pass
    def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]: return []
