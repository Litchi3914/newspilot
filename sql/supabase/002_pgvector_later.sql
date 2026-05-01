-- Later stage only: prepare pgvector after the embedding model and dimension are confirmed.
-- Do not run this file during Supabase RAG stage 1.

create extension if not exists vector;

-- Example only. If the final embedding dimension is 1024, run this in a later stage:
-- alter table article_chunks
-- add column if not exists embedding vector(1024);

-- Later, choose an ivfflat or hnsw index after checking data size and query quality.
-- Do not create vector indexes blindly in stage 1.
