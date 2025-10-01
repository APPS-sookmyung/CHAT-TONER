-- Enable extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- Style profile index (384 dims for local embedder)
CREATE TABLE IF NOT EXISTS style_profile_index (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id text NOT NULL,
  user_id text NOT NULL,
  text text NOT NULL,
  features jsonb NOT NULL,
  traits jsonb NOT NULL,
  embedding vector(384) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_style_profile_tenant ON style_profile_index(tenant_id);
CREATE INDEX IF NOT EXISTS idx_style_profile_embed ON style_profile_index USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_style_profile_traits ON style_profile_index USING GIN (traits);

-- Knowledge index (documents)
CREATE TABLE IF NOT EXISTS knowledge_index (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id text NOT NULL,
  doc_id text NOT NULL,
  chunk_ord int NOT NULL,
  title text,
  category text,
  source text,
  text text NOT NULL,
  traits jsonb NOT NULL,
  tags text[] NOT NULL,
  acl jsonb,
  embedding vector(384) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, doc_id, chunk_ord)
);
CREATE INDEX IF NOT EXISTS idx_kn_tenant ON knowledge_index(tenant_id);
CREATE INDEX IF NOT EXISTS idx_kn_tags ON knowledge_index USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_kn_traits ON knowledge_index USING GIN (traits);
CREATE INDEX IF NOT EXISTS idx_kn_embed ON knowledge_index USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Final outputs index
CREATE TABLE IF NOT EXISTS final_output_index (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id text NOT NULL,
  user_id text NOT NULL,
  text text NOT NULL,
  traits jsonb NOT NULL,
  context jsonb NOT NULL,
  embedding vector(384) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_final_output_tenant ON final_output_index(tenant_id);
CREATE INDEX IF NOT EXISTS idx_final_output_embed ON final_output_index USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

