"""Content service for case studies and insights stored in Neon DB (PostgreSQL)."""

from __future__ import annotations

import logging
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from psycopg import connect
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

LOGGER = logging.getLogger(__name__)

_JSONB_FIELDS_CASE_STUDY = (
    "solution_capabilities",
    "impact_cards",
    "industry_stats",
    "related_case_studies",
)


class ContentService:
    """Manages case studies and insights stored in PostgreSQL (Neon DB)."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    @contextmanager
    def _connection(self) -> Iterator:
        connection = connect(self._database_url, row_factory=dict_row)
        try:
            yield connection
        finally:
            connection.close()

    # ── Schema initialization ──────────────────────────────────────────────────

    def initialize(self) -> None:
        """Create content tables if they do not already exist."""

        with self._connection() as conn:
            with conn.cursor() as cur:
                # ── case_studies ───────────────────────────────────────────────
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS case_studies (
                        id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                        slug            VARCHAR(255) UNIQUE NOT NULL,
                        tags            TEXT        NOT NULL DEFAULT '',
                        industry        VARCHAR(100) NOT NULL DEFAULT '',
                        service         VARCHAR(100) NOT NULL DEFAULT '',
                        title           TEXT        NOT NULL,
                        excerpt         TEXT        NOT NULL DEFAULT '',
                        image_url       TEXT        NOT NULL DEFAULT '',
                        is_published    BOOLEAN     NOT NULL DEFAULT FALSE,
                        published_date  TIMESTAMPTZ,
                        meta_title      VARCHAR(255) NOT NULL DEFAULT '',
                        meta_description TEXT        NOT NULL DEFAULT '',
                        -- Detail-page fields
                        tag_line        TEXT        NOT NULL DEFAULT '',
                        hero_image      TEXT        NOT NULL DEFAULT '',
                        client_name     TEXT        NOT NULL DEFAULT '',
                        client_description TEXT     NOT NULL DEFAULT '',
                        challenge_heading  TEXT     NOT NULL DEFAULT '',
                        challenge_body     TEXT     NOT NULL DEFAULT '',
                        solution_heading   TEXT     NOT NULL DEFAULT '',
                        solution_body      TEXT     NOT NULL DEFAULT '',
                        solution_capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
                        impact_heading     TEXT     NOT NULL DEFAULT '',
                        impact_description TEXT     NOT NULL DEFAULT '',
                        impact_context_label TEXT,
                        impact_context_body  TEXT,
                        impact_cards       JSONB    NOT NULL DEFAULT '[]'::jsonb,
                        industry_stats     JSONB    NOT NULL DEFAULT '[]'::jsonb,
                        related_case_studies JSONB  NOT NULL DEFAULT '[]'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS case_studies_is_published_idx
                        ON case_studies (is_published);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS case_studies_industry_idx
                        ON case_studies (industry);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS case_studies_service_idx
                        ON case_studies (service);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS case_studies_published_date_idx
                        ON case_studies (published_date DESC NULLS LAST);
                """)

                # ── insights ───────────────────────────────────────────────────
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS insights (
                        id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
                        slug            VARCHAR(255) UNIQUE NOT NULL,
                        tags            TEXT        NOT NULL DEFAULT '',
                        industry        VARCHAR(100) NOT NULL DEFAULT '',
                        service         VARCHAR(100) NOT NULL DEFAULT '',
                        title           TEXT        NOT NULL,
                        excerpt         TEXT        NOT NULL DEFAULT '',
                        image_url       TEXT        NOT NULL DEFAULT '',
                        is_published    BOOLEAN     NOT NULL DEFAULT FALSE,
                        published_date  TIMESTAMPTZ,
                        meta_title      VARCHAR(255) NOT NULL DEFAULT '',
                        meta_description TEXT        NOT NULL DEFAULT '',
                        content         TEXT        NOT NULL DEFAULT '',
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS insights_is_published_idx
                        ON insights (is_published);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS insights_industry_idx
                        ON insights (industry);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS insights_service_idx
                        ON insights (service);
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS insights_published_date_idx
                        ON insights (published_date DESC NULLS LAST);
                """)

                # ── seed_log ───────────────────────────────────────────────────
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS seed_log (
                        id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        seed_version          VARCHAR(64) NOT NULL,
                        seeded_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        inserted_case_studies INT NOT NULL DEFAULT 0,
                        skipped_case_studies  INT NOT NULL DEFAULT 0,
                        inserted_insights     INT NOT NULL DEFAULT 0,
                        skipped_insights      INT NOT NULL DEFAULT 0
                    );
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS seed_log_version_idx
                        ON seed_log (seed_version);
                """)

            conn.commit()
        LOGGER.info("Content tables initialized.")

    # ── Case Studies ───────────────────────────────────────────────────────────

    def list_case_studies(
        self,
        industry: str | None = None,
        service: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return published case studies, optionally filtered, newest first."""

        filters: list[str] = ["is_published = TRUE"]
        params: list[Any] = []

        if industry:
            filters.append("industry = %s")
            params.append(industry)
        if service:
            filters.append("service = %s")
            params.append(service)

        where = " AND ".join(filters)
        query = f"""
            SELECT id, slug, tags, industry, service, title, excerpt,
                   image_url, is_published, published_date,
                   meta_title, meta_description
            FROM case_studies
            WHERE {where}
            ORDER BY published_date DESC NULLS LAST
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def get_case_study(self, slug: str) -> dict[str, Any] | None:
        """Return full detail for a single published case study."""

        query = """
            SELECT id, slug, tags, industry, service, title, excerpt,
                   image_url, is_published, published_date,
                   meta_title, meta_description,
                   tag_line, hero_image, client_name, client_description,
                   challenge_heading, challenge_body,
                   solution_heading, solution_body, solution_capabilities,
                   impact_heading, impact_description,
                   impact_context_label, impact_context_body,
                   impact_cards, industry_stats, related_case_studies
            FROM case_studies
            WHERE slug = %s AND is_published = TRUE
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, [slug])
                return cur.fetchone()

    def upsert_case_study(self, data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update a case study by slug. Returns the persisted row."""

        row = dict(data)
        row.setdefault("id", str(uuid.uuid4()))

        for field in _JSONB_FIELDS_CASE_STUDY:
            if field in row and not isinstance(row[field], Jsonb):
                row[field] = Jsonb(row[field])

        query = """
            INSERT INTO case_studies (
                id, slug, tags, industry, service, title, excerpt, image_url,
                is_published, published_date, meta_title, meta_description,
                tag_line, hero_image, client_name, client_description,
                challenge_heading, challenge_body,
                solution_heading, solution_body, solution_capabilities,
                impact_heading, impact_description,
                impact_context_label, impact_context_body,
                impact_cards, industry_stats, related_case_studies
            ) VALUES (
                %(id)s, %(slug)s, %(tags)s, %(industry)s, %(service)s,
                %(title)s, %(excerpt)s, %(image_url)s,
                %(is_published)s, %(published_date)s,
                %(meta_title)s, %(meta_description)s,
                %(tag_line)s, %(hero_image)s,
                %(client_name)s, %(client_description)s,
                %(challenge_heading)s, %(challenge_body)s,
                %(solution_heading)s, %(solution_body)s,
                %(solution_capabilities)s,
                %(impact_heading)s, %(impact_description)s,
                %(impact_context_label)s, %(impact_context_body)s,
                %(impact_cards)s, %(industry_stats)s, %(related_case_studies)s
            )
            ON CONFLICT (slug) DO UPDATE SET
                tags                  = EXCLUDED.tags,
                industry              = EXCLUDED.industry,
                service               = EXCLUDED.service,
                title                 = EXCLUDED.title,
                excerpt               = EXCLUDED.excerpt,
                image_url             = EXCLUDED.image_url,
                is_published          = EXCLUDED.is_published,
                published_date        = EXCLUDED.published_date,
                meta_title            = EXCLUDED.meta_title,
                meta_description      = EXCLUDED.meta_description,
                tag_line              = EXCLUDED.tag_line,
                hero_image            = EXCLUDED.hero_image,
                client_name           = EXCLUDED.client_name,
                client_description    = EXCLUDED.client_description,
                challenge_heading     = EXCLUDED.challenge_heading,
                challenge_body        = EXCLUDED.challenge_body,
                solution_heading      = EXCLUDED.solution_heading,
                solution_body         = EXCLUDED.solution_body,
                solution_capabilities = EXCLUDED.solution_capabilities,
                impact_heading        = EXCLUDED.impact_heading,
                impact_description    = EXCLUDED.impact_description,
                impact_context_label  = EXCLUDED.impact_context_label,
                impact_context_body   = EXCLUDED.impact_context_body,
                impact_cards          = EXCLUDED.impact_cards,
                industry_stats        = EXCLUDED.industry_stats,
                related_case_studies  = EXCLUDED.related_case_studies,
                updated_at            = NOW()
            RETURNING *
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, row)
                result = cur.fetchone()
            conn.commit()
        return result

    # ── Insights ───────────────────────────────────────────────────────────────

    def list_insights(
        self,
        industry: str | None = None,
        service: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return published insights, optionally filtered, newest first."""

        filters: list[str] = ["is_published = TRUE"]
        params: list[Any] = []

        if industry:
            filters.append("industry = %s")
            params.append(industry)
        if service:
            filters.append("service = %s")
            params.append(service)

        where = " AND ".join(filters)
        query = f"""
            SELECT id, slug, tags, industry, service, title, excerpt,
                   image_url, is_published, published_date,
                   meta_title, meta_description
            FROM insights
            WHERE {where}
            ORDER BY published_date DESC NULLS LAST
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    def get_insight(self, slug: str) -> dict[str, Any] | None:
        """Return a single published insight by slug."""

        query = """
            SELECT id, slug, tags, industry, service, title, excerpt,
                   image_url, is_published, published_date,
                   meta_title, meta_description, content
            FROM insights
            WHERE slug = %s AND is_published = TRUE
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, [slug])
                return cur.fetchone()

    def upsert_insight(self, data: dict[str, Any]) -> dict[str, Any]:
        """Insert or update an insight by slug. Returns the persisted row."""

        row = dict(data)
        row.setdefault("id", str(uuid.uuid4()))

        query = """
            INSERT INTO insights (
                id, slug, tags, industry, service, title, excerpt, image_url,
                is_published, published_date, meta_title, meta_description, content
            ) VALUES (
                %(id)s, %(slug)s, %(tags)s, %(industry)s, %(service)s,
                %(title)s, %(excerpt)s, %(image_url)s,
                %(is_published)s, %(published_date)s,
                %(meta_title)s, %(meta_description)s, %(content)s
            )
            ON CONFLICT (slug) DO UPDATE SET
                tags             = EXCLUDED.tags,
                industry         = EXCLUDED.industry,
                service          = EXCLUDED.service,
                title            = EXCLUDED.title,
                excerpt          = EXCLUDED.excerpt,
                image_url        = EXCLUDED.image_url,
                is_published     = EXCLUDED.is_published,
                published_date   = EXCLUDED.published_date,
                meta_title       = EXCLUDED.meta_title,
                meta_description = EXCLUDED.meta_description,
                content          = EXCLUDED.content,
                updated_at       = NOW()
            RETURNING *
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, row)
                result = cur.fetchone()
            conn.commit()
        return result

    # ── Seed helpers (insert-only, never overwrites existing records) ──────────

    def insert_case_study_if_absent(self, data: dict[str, Any]) -> bool:
        """Insert a case study only if the slug is not already in the DB.

        Returns True if the row was inserted, False if it was already present.
        Uses ON CONFLICT (slug) DO NOTHING so existing content is never modified.
        """
        row = dict(data)
        row.setdefault("id", str(uuid.uuid4()))
        for field in _JSONB_FIELDS_CASE_STUDY:
            if field in row and not isinstance(row[field], Jsonb):
                row[field] = Jsonb(row[field])

        query = """
            INSERT INTO case_studies (
                id, slug, tags, industry, service, title, excerpt, image_url,
                is_published, published_date, meta_title, meta_description,
                tag_line, hero_image, client_name, client_description,
                challenge_heading, challenge_body,
                solution_heading, solution_body, solution_capabilities,
                impact_heading, impact_description,
                impact_context_label, impact_context_body,
                impact_cards, industry_stats, related_case_studies
            ) VALUES (
                %(id)s, %(slug)s, %(tags)s, %(industry)s, %(service)s,
                %(title)s, %(excerpt)s, %(image_url)s,
                %(is_published)s, %(published_date)s,
                %(meta_title)s, %(meta_description)s,
                %(tag_line)s, %(hero_image)s,
                %(client_name)s, %(client_description)s,
                %(challenge_heading)s, %(challenge_body)s,
                %(solution_heading)s, %(solution_body)s,
                %(solution_capabilities)s,
                %(impact_heading)s, %(impact_description)s,
                %(impact_context_label)s, %(impact_context_body)s,
                %(impact_cards)s, %(industry_stats)s, %(related_case_studies)s
            )
            ON CONFLICT (slug) DO NOTHING
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, row)
                inserted = cur.rowcount == 1
            conn.commit()
        return inserted

    def insert_insight_if_absent(self, data: dict[str, Any]) -> bool:
        """Insert an insight only if the slug is not already in the DB.

        Returns True if the row was inserted, False if it was already present.
        """
        row = dict(data)
        row.setdefault("id", str(uuid.uuid4()))

        query = """
            INSERT INTO insights (
                id, slug, tags, industry, service, title, excerpt, image_url,
                is_published, published_date, meta_title, meta_description, content
            ) VALUES (
                %(id)s, %(slug)s, %(tags)s, %(industry)s, %(service)s,
                %(title)s, %(excerpt)s, %(image_url)s,
                %(is_published)s, %(published_date)s,
                %(meta_title)s, %(meta_description)s, %(content)s
            )
            ON CONFLICT (slug) DO NOTHING
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, row)
                inserted = cur.rowcount == 1
            conn.commit()
        return inserted

    def record_seed_run(
        self,
        seed_version: str,
        inserted_case_studies: int,
        skipped_case_studies: int,
        inserted_insights: int,
        skipped_insights: int,
    ) -> None:
        """Append a row to seed_log recording this seed run."""
        query = """
            INSERT INTO seed_log (
                seed_version,
                inserted_case_studies, skipped_case_studies,
                inserted_insights, skipped_insights
            ) VALUES (%s, %s, %s, %s, %s)
        """
        with self._connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    [
                        seed_version,
                        inserted_case_studies,
                        skipped_case_studies,
                        inserted_insights,
                        skipped_insights,
                    ],
                )
            conn.commit()
