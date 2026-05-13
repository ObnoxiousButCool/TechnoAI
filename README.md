# Techno-AI

Techno-AI is a FastAPI backend that implements a modular Retrieval-Augmented
Generation (RAG) workflow for answering questions strictly from website content.
Website ingestion is enabled by default, while file ingestion is available but
disabled unless explicitly configured.

## Setup

1. Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` and `WEBSITE_URL`.
2. Start the stack:

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
  Answers a question using only retrieved website content.

  ```bash
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"question":"What services does the company offer?"}'
  ```

- `GET /health`
  Basic health endpoint.

## Notes

- PostgreSQL uses the `pgvector` extension for similarity search.
- The vector store is abstracted behind `VectorStore` for future providers.
- The scheduler is a placeholder for future cron-based ingestion jobs.
