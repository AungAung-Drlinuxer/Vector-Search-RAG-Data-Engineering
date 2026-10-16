-- Vector Search & RAG Data Engineering Course
-- Initial PostgreSQL + pgvector Schema

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Chunks Table with vector, jsonb metadata, and full-text search tsvector
CREATE TABLE IF NOT EXISTS chunks (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    doc_id     text NOT NULL,
    content    text NOT NULL,
    metadata   jsonb NOT NULL DEFAULT '{}'::jsonb,
    fts        tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding  vector(768)
);

-- Indexes
CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx 
    ON chunks USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS chunks_metadata_gin_idx 
    ON chunks USING gin (metadata jsonb_path_ops);

CREATE INDEX IF NOT EXISTS chunks_fts_gin_idx 
    ON chunks USING gin (fts);

-- Documents Table with Row-Level Security (RLS) for Module 12 Lab
CREATE TABLE IF NOT EXISTS documents (
    id         integer PRIMARY KEY,
    content    text NOT NULL,
    owner      text NOT NULL,
    embedding  vector(4)
);

ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'documents' AND policyname = 'docs_owner_isolation'
    ) THEN
        CREATE POLICY docs_owner_isolation ON documents
            FOR SELECT
            USING (owner = current_user);
    END IF;
END $$;

-- Sample Seed Data for Testing
INSERT INTO documents (id, content, owner, embedding)
VALUES 
    (1, 'Secret project blueprint', 'alice', '[1.0, 0.0, 0.0, 0.0]'),
    (2, 'Quarterly financial summary', 'bob', '[0.9, 0.1, 0.0, 0.0]'),
    (3, 'Public technical manual', 'alice', '[0.5, 0.5, 0.0, 0.0]')
ON CONFLICT (id) DO NOTHING;
