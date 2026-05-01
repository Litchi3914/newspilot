# 向量库接口预留设计

当前阶段采用 TF-IDF 检索，保证流程可运行。
后续可替换到：
- Chroma
- Qdrant
- PostgreSQL + pgvector

建议抽象：
- EmbeddingClient: embed_texts(texts)
- VectorStore: add_texts(...) / search(...)

在替换真实向量库时保持 scripts/08 与 scripts/10 输入输出协议不变。
