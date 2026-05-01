class BaseRetriever:
    def build(self, chunks: list[dict]):
        raise NotImplementedError
    def save(self, path: str):
        raise NotImplementedError
    def load(self, path: str):
        raise NotImplementedError
    def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]:
        raise NotImplementedError
