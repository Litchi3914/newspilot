# Supabase RAG Stage 1

This stage adds basic Supabase storage for NewsPilot. It does not switch retrieval to Supabase, does not generate embeddings, and does not enable pgvector search.

## Goal

- Save review records from the backend into `review_records`.
- Import cleaned article metadata/content into `articles`.
- Import local text chunks into `article_chunks`.
- Keep the existing BM25, TF-IDF, and hybrid retrieval logic as the default.

## SQL To Run In Supabase

Open the Supabase SQL Editor and run:

```text
sql/supabase/001_basic_tables.sql
```

This creates:

- `review_records`
- `articles`
- `article_chunks`

Do not run `sql/supabase/002_pgvector_later.sql` yet. That file is only a later-stage reference for pgvector.

## Local Environment

Copy the Supabase values into local `.env`:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SECRET_KEY=your-supabase-secret-key
ENABLE_REVIEW_RECORD_STORAGE=true
ENABLE_SUPABASE_RAG=false
```

If you are using the older service role key, set:

```env
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Never put these keys in `frontend/.env` and never add a `VITE_` prefix.

## Railway Variables

Configure these only in the Railway backend service:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SECRET_KEY=your-supabase-secret-key
ENABLE_REVIEW_RECORD_STORAGE=true
ENABLE_SUPABASE_RAG=false
```

Use `SUPABASE_SERVICE_ROLE_KEY` only if your Supabase project still uses the older key style.

## Preflight

After installing dependencies and running the SQL:

```bash
pip install -r requirements.txt
python scripts/20_supabase_preflight.py
```

Expected result:

```json
{
  "ready": true
}
```

## Import Articles

Dry run:

```bash
python scripts/21_import_articles_to_supabase.py --input data/structured/articles_structured.csv --limit 20 --dry-run
```

Import:

```bash
python scripts/21_import_articles_to_supabase.py --input data/structured/articles_structured.csv --limit 20
```

Field mapping:

- `url` -> `source_url`
- `title` -> `title`
- `publish_date` -> `publish_date`
- `body_clean` -> `content`
- `editor`, `reporter`, `correspondent`, and related fields -> `metadata`

## Import Chunks

Dry run:

```bash
python scripts/22_import_chunks_to_supabase.py --input data/chunks/article_chunks.jsonl --limit 50 --dry-run
```

Import:

```bash
python scripts/22_import_chunks_to_supabase.py --input data/chunks/article_chunks.jsonl --limit 50 --batch-size 20
```

Field mapping:

- `url` -> `source_url`
- `chunk_index` -> `chunk_index`
- `chunk_text` -> `chunk_text`
- `title`, `publish_date`, `category` -> same table fields
- `chunk_id`, `article_id`, `article_type`, `char_count` -> `metadata`

## Enable Review Record Storage

Review record storage is off by default. To enable it:

```env
ENABLE_REVIEW_RECORD_STORAGE=true
```

Then call:

```bash
uvicorn src.api.app:app --reload --host 127.0.0.1 --port 8000
```

Submit a review request and check the `review_records` table in Supabase.

If the Supabase write fails, the review API still returns the review result. The backend logs the storage failure instead of failing the user request.

## Not In This Stage

- No frontend Supabase client.
- No Supabase keys in GitHub Pages.
- No login or user permission tables.
- No embedding generation.
- No pgvector index.
- No switch from local BM25/TF-IDF/hybrid retrieval to Supabase retrieval.

## Next Stage

After this foundation works, the next stage can:

- choose an embedding model,
- confirm embedding dimension,
- add an `embedding` column to `article_chunks`,
- import a small embedding sample,
- create a match RPC or SQL query,
- add a Supabase vector retriever,
- compare retrieval quality with the existing local retrievers.
