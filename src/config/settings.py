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
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_embedding_dimensions: int = Field(
        default=1536,
        alias="OPENAI_EMBEDDING_DIMENSIONS",
    )
    openai_chat_model: str = Field(
        default="gpt-4.1-mini",
        alias="OPENAI_CHAT_MODEL",
    )
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
    pdf_directory: str = Field(default="./data/pdfs", alias="PDF_DIRECTORY")
    chunk_size_words: int = Field(default=700, alias="CHUNK_SIZE_WORDS")
    chunk_overlap_words: int = Field(default=100, alias="CHUNK_OVERLAP_WORDS")
    retrieval_top_k: int = Field(default=5, alias="RETRIEVAL_TOP_K")
    retrieval_min_score: float = Field(default=0.25, alias="RETRIEVAL_MIN_SCORE")
    request_timeout_seconds: int = 30
    user_agent: str = "Techno-AI/1.0"

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

    return Settings()
