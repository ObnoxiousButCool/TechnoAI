# Techno-AI

Techno-AI is a FastAPI backend that implements a modular Retrieval-Augmented
Generation (RAG) workflow for answering questions strictly from website content.
Website ingestion is enabled by default, while file ingestion is available but
disabled unless explicitly configured.

## Setup

1. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` and `WEBSITE_URL`.
   Optionally set `WEBSITE_URLS` to a comma-separated list of fallback pages.
2. Install Python dependencies and Playwright browser binaries:

   ```bash
   pip install -r requirements.txt
   playwright install
   ```

3. Start the stack:

   ```bash
   docker compose up --build
   ```

3. The API will be available at `http://localhost:8000`.

## Endpoints

- `POST /ingest/run`
  Starts ingestion for every enabled source.

  ```bash
  curl -X POST http://localhost:8000/ingest/run
  ```

- `DELETE /ingest/vectors`
  Clears all previously ingested ChromaDB vector contents.

  ```bash
  curl -X DELETE http://localhost:8000/ingest/vectors
  ```

- `POST /chat`
  Answers a question using only retrieved website content. Optionally accepts a
  `session_id` to maintain conversational context across turns. If omitted, a new
  session is created automatically and returned in the response.

  ```bash
  # First turn — no session_id needed
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question":"What AI services does Technossus offer?"}'

  # Follow-up turn — pass back the session_id from the previous response
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question":"Tell me more about the healthcare case study","session_id":"<session_id>"}'
  ```

  Response shape:
  ```json
  { "answer": "...", "sources": [...], "session_id": "<uuid>" }
  ```

- `DELETE /chat/session/{session_id}`
  Clears chat memory for the given session (e.g. when the user starts a new conversation).

  ```bash
  curl -X DELETE http://localhost:8000/chat/session/<session_id>
  ```

- `GET /health`
  Basic health endpoint.

## Configuration

All runtime-tunable values are controlled via `.env`. Copy `.env.example` to `.env` to start.

### Switching Ollama models

Change `OLLAMA_MODEL` in `.env` and restart the backend — no code changes needed:

```
OLLAMA_MODEL=qwen2.5:7b-instruct
```

To point at a different Ollama server:

```
OLLAMA_BASE_URL=http://10.30.1.34:11434
```

### Tuning response generation

| Variable | Default | Effect |
|---|---|---|
| `OLLAMA_TEMPERATURE` | `0.2` | Lower = more deterministic answers |
| `OLLAMA_TOP_P` | `0.8` | Nucleus sampling threshold |
| `OLLAMA_NUM_PREDICT` | `180` | Max tokens per response (~130 words) |

### Tuning retrieval

| Variable | Default | Effect |
|---|---|---|
| `RETRIEVAL_TOP_K` | `5` | Number of chunks retrieved per query |
| `RETRIEVAL_MIN_SCORE` | `0.25` | Minimum similarity score to include a chunk |
| `CHUNK_SIZE_WORDS` | `700` | Ingestion chunk size (requires re-ingestion) |
| `CHUNK_OVERLAP_WORDS` | `100` | Overlap between chunks (requires re-ingestion) |

## Notes

- PostgreSQL uses the `pgvector` extension for similarity search.
- The vector store is abstracted behind `VectorStore` for future providers.
- Website ingestion tries `WEBSITE_URL/sitemap.xml` first. If the sitemap is
  missing, invalid, HTML, empty, or cannot be parsed, it falls back to
  `WEBSITE_URLS`; relative paths are resolved against `WEBSITE_URL`.
- The scheduler is a placeholder for future cron-based ingestion jobs.
