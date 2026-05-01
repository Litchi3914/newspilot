class KnowledgeBase:
    def build(self, chunks_path: str):
        raise NotImplementedError

    def save(self, index_path: str):
        raise NotImplementedError

    def load(self, index_path: str):
        raise NotImplementedError

    def search(self, query: str, top_k: int = 5, filters: dict | None = None):
        raise NotImplementedError
