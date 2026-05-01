create table if not exists review_records (
  id uuid primary key default gen_random_uuid(),
  request_id text,
  title text,
  input_text text not null,
  revised_text text,
  issues jsonb,
  diff_result jsonb,
  raw_result jsonb,
  options jsonb,
  client_meta jsonb,
  created_at timestamptz default now()
);

create table if not exists articles (
  id uuid primary key default gen_random_uuid(),
  source_url text unique,
  title text not null,
  publish_date date,
  department text,
  category text,
  author text,
  content text,
  metadata jsonb,
  created_at timestamptz default now()
);

create table if not exists article_chunks (
  id uuid primary key default gen_random_uuid(),
  article_id uuid references articles(id) on delete cascade,
  source_url text,
  title text,
  publish_date date,
  category text,
  chunk_index int,
  chunk_text text not null,
  metadata jsonb,
  created_at timestamptz default now(),
  unique(source_url, chunk_index)
);

create index if not exists idx_articles_source_url on articles(source_url);
create index if not exists idx_articles_publish_date on articles(publish_date);
create index if not exists idx_article_chunks_source_url on article_chunks(source_url);
create index if not exists idx_article_chunks_title on article_chunks(title);
