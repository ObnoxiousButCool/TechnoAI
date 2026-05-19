"""Application settings loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application configuration."""

    app_name: str = "Techno-AI"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    admin_api_key: str = Field(
    default="dev-key",
    alias="ADMIN_API_KEY",
)
    allowed_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="ALLOWED_ORIGINS",
    )
    # Active vector store: "pgvector" (default) or "chroma"
    vector_store_type: str = Field(default="pgvector", alias="VECTOR_STORE_TYPE")

    # Embedding output dimension — nomic-embed-text produces 768-dim vectors
    embedding_dimensions: int = Field(default=768, alias="EMBEDDING_DIMENSIONS")

    database_url: str = Field(
        default="postgresql://postgres:postgres@db:5432/techno_ai",
        alias="DATABASE_URL",
    )
    enable_website_ingest: bool = Field(
        default=True,
        alias="ENABLE_WEBSITE_INGEST",
    )
    enable_file_ingest: bool = Field(
        default=False,
        alias="ENABLE_FILE_INGEST",
    )
    website_url: str = Field(default="", alias="WEBSITE_URL")
    website_urls: str = Field(default="", alias="WEBSITE_URLS")
    pdf_directory: str = Field(default="./data/pdfs", alias="PDF_DIRECTORY")
    chunk_size_words: int = Field(default=700, alias="CHUNK_SIZE_WORDS")
    chunk_overlap_words: int = Field(default=100, alias="CHUNK_OVERLAP_WORDS")
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    retrieval_min_score: float = Field(default=0.42, alias="RETRIEVAL_MIN_SCORE")
    request_timeout_seconds: int = 30
    user_agent: str = "Techno-AI/1.0"

    # Ollama — shared base URL for both LLM and embedding calls
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        alias="OLLAMA_BASE_URL",
    )
    ollama_model: str = Field(default="llama3.2:8b", alias="OLLAMA_MODEL")
    ollama_rewrite_model: str = Field(
        default="gemma3:1b",
        alias="OLLAMA_REWRITE_MODEL",
    )
    ollama_embedding_model: str = Field(
        default="nomic-embed-text",
        alias="OLLAMA_EMBEDDING_MODEL",
    )
    ollama_temperature: float = Field(default=0.2, alias="OLLAMA_TEMPERATURE")
    ollama_top_p: float = Field(default=0.8, alias="OLLAMA_TOP_P")
    ollama_num_predict: int = Field(default=180, alias="OLLAMA_NUM_PREDICT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()  # type: ignore[call-arg]
