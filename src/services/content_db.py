"""Content database service for Case Studies and Insights using Neon DB (PostgreSQL)."""

from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from typing import Iterator, Optional

from psycopg import connect
from psycopg.rows import dict_row

from src.config.settings import get_settings

LOGGER = logging.getLogger(__name__)

SHARED_ASSETS_PATH = "/assets/shared"


class ContentDBService:
    """Manages Case Studies and Insights in Neon DB (PostgreSQL)."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        self._database_url = database_url or get_settings().database_url

    @contextmanager
    def _connection(self) -> Iterator:
        connection = connect(self._database_url, row_factory=dict_row)
        try:
            yield connection
        finally:
            connection.close()

    # ─── Schema initialization ─────────────────────────────────────────────────

    def initialize(self) -> None:
        """Create required tables if they don't exist."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                # Create new case_studies table with JSON-based schema
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS case_studies (
                        id SERIAL PRIMARY KEY,
                        page TEXT UNIQUE NOT NULL,
                        slug TEXT,
                        version INTEGER NOT NULL DEFAULT 1,
                        tags TEXT,
                        industry TEXT,
                        service TEXT,
                        tag_line TEXT,
                        meta JSONB NOT NULL,
                        sections JSONB NOT NULL DEFAULT '[]'::jsonb,
                        is_published BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)
                
                # Add columns if they don't exist (for migration)
                cur.execute("""
                    ALTER TABLE case_studies ADD COLUMN IF NOT EXISTS slug TEXT;
                """)
                cur.execute("""
                    ALTER TABLE case_studies ADD COLUMN IF NOT EXISTS tags TEXT;
                """)
                cur.execute("""
                    ALTER TABLE case_studies ADD COLUMN IF NOT EXISTS industry TEXT;
                """)
                cur.execute("""
                    ALTER TABLE case_studies ADD COLUMN IF NOT EXISTS service TEXT;
                """)
                cur.execute("""
                    ALTER TABLE case_studies ADD COLUMN IF NOT EXISTS tag_line TEXT;
                """)
                
                # Drop deprecated columns (meta_title and meta_description moved to meta JSONB)
                cur.execute("""
                    ALTER TABLE case_studies DROP COLUMN IF EXISTS meta_title;
                """)
                cur.execute("""
                    ALTER TABLE case_studies DROP COLUMN IF EXISTS meta_description;
                """)

                # Create indexes for new case_studies table
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_case_studies_page
                    ON case_studies (page);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_case_studies_slug
                    ON case_studies (slug);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_case_studies_published
                    ON case_studies (is_published, created_at DESC);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_case_studies_industry
                    ON case_studies (industry);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_case_studies_service
                    ON case_studies (service);
                """)

                # Create insights table with JSON-based schema
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS insights (
                        id SERIAL PRIMARY KEY,
                        page TEXT UNIQUE NOT NULL,
                        slug TEXT,
                        version INTEGER NOT NULL DEFAULT 1,
                        tags TEXT,
                        industry TEXT,
                        service TEXT,
                        meta JSONB NOT NULL,
                        sections JSONB NOT NULL DEFAULT '[]'::jsonb,
                        is_published BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)

                # Create indexes for insights table
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_insights_page
                    ON insights (page);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_insights_slug
                    ON insights (slug);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_insights_published
                    ON insights (is_published, created_at DESC);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_insights_industry
                    ON insights (industry);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_insights_service
                    ON insights (service);
                """)

                conn.commit()
        LOGGER.info("Content DB tables initialized.")

    # ─── Case Studies CRUD ────────────────────────────

    def list_case_studies(
        self,
        published_only: bool = True,
        industry: Optional[str] = None,
        service: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """List case studies, optionally filtered."""

        conditions = []
        params: list = []

        if published_only:
            conditions.append("is_published = TRUE")
        if industry:
            conditions.append("industry = %s")
            params.append(industry)
        if service:
            conditions.append("service = %s")
            params.append(service)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT * FROM case_studies
            {where}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def get_case_study_by_page(self, page: str) -> Optional[dict]:
        """Get a single case study by page identifier."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM case_studies WHERE page = %s", [page])
                return cur.fetchone()

    def get_case_study_by_slug(self, slug: str) -> Optional[dict]:
        """Get a single case study by slug."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM case_studies WHERE slug = %s", [slug])
                return cur.fetchone()

    def get_case_study_by_id(self, case_study_id: int) -> Optional[dict]:
        """Get a single case study by ID."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM case_studies WHERE id = %s", [case_study_id])
                return cur.fetchone()

    def create_case_study(self, data: dict) -> dict:
        """Insert a new case study. Returns the created record."""

        # Serialize JSONB fields
        if "meta" in data and not isinstance(data["meta"], str):
            data["meta"] = json.dumps(data["meta"])
        if "sections" in data and not isinstance(data["sections"], str):
            data["sections"] = json.dumps(data["sections"])

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO case_studies (
                        page, slug, version, tags, industry, service, 
                        tag_line, meta, sections, is_published
                    ) VALUES (
                        %(page)s, %(slug)s, %(version)s, %(tags)s, %(industry)s, %(service)s,
                        %(tag_line)s, %(meta)s, %(sections)s, %(is_published)s
                    )
                    RETURNING *
                    """,
                    data,
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def update_case_study(self, page: str, data: dict) -> Optional[dict]:
        """Update an existing case study by page. Only updates provided fields."""

        data = {k: v for k, v in data.items() if v is not None}
        if not data:
            return self.get_case_study_by_page(page)

        # Serialize JSONB fields
        if "meta" in data and not isinstance(data["meta"], str):
            data["meta"] = json.dumps(data["meta"])
        if "sections" in data and not isinstance(data["sections"], str):
            data["sections"] = json.dumps(data["sections"])

        set_clauses = [f"{key} = %({key})s" for key in data]
        set_clauses.append("updated_at = NOW()")
        data["_page"] = page

        query = f"""
            UPDATE case_studies
            SET {', '.join(set_clauses)}
            WHERE page = %(_page)s
            RETURNING *
        """

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, data)
                result = cur.fetchone()
                conn.commit()
                return result

    def delete_case_study(self, page: str) -> bool:
        """Delete a case study by page. Returns True if deleted."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM case_studies WHERE page = %s RETURNING id", [page]
                )
                result = cur.fetchone()
                conn.commit()
                return result is not None

    def upsert_case_study(self, data: dict) -> dict:
        """Insert or update based on page (idempotent seed)."""

        defaults = {
            "version": 1,
            "is_published": False,
            "slug": None,
            "tags": None,
            "industry": None,
            "service": None,
            "tag_line": None,
        }
        data = {**defaults, **data}

        # Serialize JSONB fields
        if "meta" in data and not isinstance(data["meta"], str):
            data["meta"] = json.dumps(data["meta"])
        if "sections" in data and not isinstance(data["sections"], str):
            data["sections"] = json.dumps(data["sections"])

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO case_studies (
                        page, slug, version, tags, industry, service,
                        tag_line, meta, sections, is_published
                    ) VALUES (
                        %(page)s, %(slug)s, %(version)s, %(tags)s, %(industry)s, %(service)s,
                        %(tag_line)s, %(meta)s, %(sections)s, %(is_published)s
                    )
                    ON CONFLICT (page) DO UPDATE SET
                        slug = EXCLUDED.slug,
                        version = EXCLUDED.version,
                        tags = EXCLUDED.tags,
                        industry = EXCLUDED.industry,
                        service = EXCLUDED.service,
                        tag_line = EXCLUDED.tag_line,
                        meta = EXCLUDED.meta,
                        sections = EXCLUDED.sections,
                        is_published = EXCLUDED.is_published,
                        updated_at = NOW()
                    RETURNING *
                    """,
                    data,
                )
                result = cur.fetchone()
                conn.commit()
                return result

    # ─── Insights CRUD ────────────────────────────────────────────────────────

    def list_insights(
        self,
        published_only: bool = True,
        industry: Optional[str] = None,
        service: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        """List insights, optionally filtered."""

        conditions = []
        params: list = []

        if published_only:
            conditions.append("is_published = TRUE")
        if industry:
            conditions.append("industry = %s")
            params.append(industry)
        if service:
            conditions.append("service = %s")
            params.append(service)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT * FROM insights
            {where}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def get_insight_by_page(self, page: str) -> Optional[dict]:
        """Get a single insight by page identifier."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM insights WHERE page = %s", [page])
                return cur.fetchone()

    def get_insight_by_slug(self, slug: str) -> Optional[dict]:
        """Get a single insight by slug."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM insights WHERE slug = %s", [slug])
                return cur.fetchone()

    def get_insight_by_id(self, insight_id: int) -> Optional[dict]:
        """Get a single insight by ID."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM insights WHERE id = %s", [insight_id])
                return cur.fetchone()

    def create_insight(self, data: dict) -> dict:
        """Insert a new insight with JSON-based schema. Returns the created record."""

        # Serialize JSONB fields
        if "meta" in data and not isinstance(data["meta"], str):
            data["meta"] = json.dumps(data["meta"])
        if "sections" in data and not isinstance(data["sections"], str):
            data["sections"] = json.dumps(data["sections"])

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO insights (
                        page, slug, version, tags, industry, service, 
                        meta, sections, is_published
                    ) VALUES (
                        %(page)s, %(slug)s, %(version)s, %(tags)s, %(industry)s, %(service)s,
                        %(meta)s, %(sections)s, %(is_published)s
                    )
                    RETURNING *
                    """,
                    data,
                )
                result = cur.fetchone()
                conn.commit()
                return result

    def update_insight(self, page: str, data: dict) -> Optional[dict]:
        """Update an existing insight by page. Only updates provided fields."""

        data = {k: v for k, v in data.items() if v is not None}
        if not data:
            return self.get_insight_by_page(page)

        # Serialize JSONB fields
        if "meta" in data and not isinstance(data["meta"], str):
            data["meta"] = json.dumps(data["meta"])
        if "sections" in data and not isinstance(data["sections"], str):
            data["sections"] = json.dumps(data["sections"])

        set_clauses = [f"{key} = %({key})s" for key in data]
        set_clauses.append("updated_at = NOW()")
        data["_page"] = page

        query = f"""
            UPDATE insights
            SET {', '.join(set_clauses)}
            WHERE page = %(_page)s
            RETURNING *
        """

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, data)
                result = cur.fetchone()
                conn.commit()
                return result

    def delete_insight(self, page: str) -> bool:
        """Delete an insight by page. Returns True if deleted."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM insights WHERE page = %s RETURNING id", [page]
                )
                result = cur.fetchone()
                conn.commit()
                return result is not None

    def upsert_insight(self, data: dict) -> dict:
        """Insert or update based on page (idempotent seed)."""

        defaults = {
            "version": 1,
            "is_published": False,
            "slug": None,
            "tags": None,
            "industry": None,
            "service": None,
        }
        data = {**defaults, **data}

        # Serialize JSONB fields
        if "meta" in data and not isinstance(data["meta"], str):
            data["meta"] = json.dumps(data["meta"])
        if "sections" in data and not isinstance(data["sections"], str):
            data["sections"] = json.dumps(data["sections"])

        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO insights (
                        page, slug, version, tags, industry, service,
                        meta, sections, is_published
                    ) VALUES (
                        %(page)s, %(slug)s, %(version)s, %(tags)s, %(industry)s, %(service)s,
                        %(meta)s, %(sections)s, %(is_published)s
                    )
                    ON CONFLICT (page) DO UPDATE SET
                        slug = EXCLUDED.slug,
                        version = EXCLUDED.version,
                        tags = EXCLUDED.tags,
                        industry = EXCLUDED.industry,
                        service = EXCLUDED.service,
                        meta = EXCLUDED.meta,
                        sections = EXCLUDED.sections,
                        is_published = EXCLUDED.is_published,
                        updated_at = NOW()
                    RETURNING *
                    """,
                    data,
                )
                result = cur.fetchone()
                conn.commit()
                return result

    # ─── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def normalize_hero_image_path(image_path: str) -> str:
        """Normalize image path to use the shared assets location.

        Stores only the relative reference under the shared upload location.
        """

        if not image_path:
            return ""
        # If already in shared path, return as-is
        if image_path.startswith(SHARED_ASSETS_PATH):
            return image_path
        # Extract filename from path (e.g. /assets/abc123.png -> abc123.png)
        filename = image_path.rsplit("/", 1)[-1] if "/" in image_path else image_path
        return f"{SHARED_ASSETS_PATH}/{filename}"


def get_content_db_service() -> ContentDBService:
    """Factory for ContentDBService."""

    return ContentDBService()
