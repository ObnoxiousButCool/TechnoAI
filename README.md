# Techno-AI

Techno-AI is a FastAPI backend that implements a modular Retrieval-Augmented
Generation (RAG) workflow for answering questions strictly from website content.
Website ingestion is enabled by default; file (PDF) ingestion is available but
disabled unless explicitly configured.

Vectors are stored in **PostgreSQL with the pgvector extension** — no additional
vector database is needed beyond the included Docker Compose service.

## Setup

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

| Variable | Example | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/techno_ai` | Use `@db:...` inside Docker |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server for LLM + embeddings |
| `WEBSITE_URL` | `https://www.technossus.com/` | Root URL to crawl |
| `WEBSITE_URLS` | `/,/about,/services` | Fallback pages if sitemap missing |

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install
```

### 3. Start the stack (Docker)

```bash
docker compose up --build
```

This starts PostgreSQL (with pgvector) and the FastAPI backend.  On first boot
the app creates the `vector` extension and the `document_chunks` table
automatically — no manual migrations needed.

### 4. Start locally (no Docker)

Ensure PostgreSQL with the pgvector extension is running, then:

```bash
# Set DATABASE_URL to your local Postgres instance in .env
uvicorn src.main:app --reload
```

## Database schema

The app manages its own schema via `PGVectorStore.initialize()`:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS document_chunks (
    id          TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id   TEXT NOT NULL,
    content     TEXT NOT NULL,
    metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding   VECTOR(768) NOT NULL,   -- nomic-embed-text dimension
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS document_chunks_source_id_idx   ON document_chunks (source_id);
CREATE INDEX IF NOT EXISTS document_chunks_source_type_idx ON document_chunks (source_type);
```

Similarity search uses the `<=>` cosine distance operator; scores are returned
as `1 - distance` so that 1.0 = identical and 0.0 = orthogonal.

## Ingestion

```bash
curl -X POST http://localhost:8000/ingest/run
```

To clear all vectors and re-ingest from scratch:

```bash
curl -X DELETE http://localhost:8000/ingest/vectors
curl -X POST  http://localhost:8000/ingest/run
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/ingest/run` | Ingest all enabled sources |
| `DELETE` | `/ingest/vectors` | Delete all vectors from the DB |
| `POST` | `/chat` | Ask a question; returns answer + sources |
| `DELETE` | `/chat/session/{id}` | Clear session memory |
| `GET` | `/health` | Health check |

### Example chat

```bash
# First turn
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What AI services does Technossus offer?"}'

# Follow-up — pass back the session_id from the previous response
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Tell me more about the healthcare case study","session_id":"<session_id>"}'
```

Response shape:

```json
{ "answer": "...", "sources": [...], "session_id": "<uuid>" }
```

## Configuration reference

### Vector store

| Variable | Default | Notes |
|---|---|---|
| `VECTOR_STORE_TYPE` | `pgvector` | Only `pgvector` is supported |
| `DATABASE_URL` | `postgresql://postgres:postgres@db:5432/techno_ai` | Standard libpq connection string |
| `EMBEDDING_DIMENSIONS` | `768` | Must match the embedding model output; nomic-embed-text = 768 |

### Ollama

| Variable | Default | Effect |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Shared base URL for LLM and embeddings |
| `OLLAMA_MODEL` | `qwen2.5:7b-instruct` | Chat/generation model |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model |
| `OLLAMA_TEMPERATURE` | `0.2` | Lower = more deterministic |
| `OLLAMA_TOP_P` | `0.8` | Nucleus sampling threshold |
| `OLLAMA_NUM_PREDICT` | `180` | Max tokens per response |

### Retrieval

| Variable | Default | Effect |
|---|---|---|
| `RETRIEVAL_TOP_K` | `5` | Number of chunks retrieved per query |
| `RETRIEVAL_MIN_SCORE` | `0.25` | Minimum cosine similarity to include a chunk |
| `CHUNK_SIZE_WORDS` | `700` | Ingestion chunk size (requires re-ingestion after change) |
| `CHUNK_OVERLAP_WORDS` | `100` | Overlap between consecutive chunks |

## Notes

- The vector store is abstracted behind `VectorStore` (see
  [src/services/vector_store/base.py](src/services/vector_store/base.py)) so
  alternative backends can be added without touching the RAG or ingestion logic.
- Website ingestion tries `WEBSITE_URL/sitemap.xml` first.  If the sitemap is
  missing, invalid, HTML, empty, or cannot be parsed it falls back to
  `WEBSITE_URLS`; relative paths are resolved against `WEBSITE_URL`.
- The scheduler (`src/jobs/scheduler.py`) is a placeholder for future
  cron-based ingestion jobs.
