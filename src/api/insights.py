"""Insights API routes."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

from src.config.settings import get_settings
from src.services.content_service import ContentService

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/insights", tags=["insights"])

_admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_service() -> ContentService:
    return ContentService(get_settings().database_url)


def _require_admin(x_admin_key: str | None = Depends(_admin_key_header)) -> None:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")


def _format_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map snake_case DB row to camelCase JSON for the frontend."""
    mapping: dict[str, str] = {
        "id": "id",
        "slug": "slug",
        "tags": "tags",
        "industry": "industry",
        "service": "service",
        "title": "title",
        "excerpt": "excerpt",
        "image_url": "imageUrl",
        "is_published": "isPublished",
        "published_date": "publishedDate",
        "meta_title": "metaTitle",
        "meta_description": "metaDescription",
        "content": "content",
    }
    result: dict[str, Any] = {}
    for db_key, json_key in mapping.items():
        if db_key not in row:
            continue
        value = row[db_key]
        if isinstance(value, datetime):
            value = value.isoformat()
        result[json_key] = value
    return result


# ── Public endpoints ───────────────────────────────────────────────────────────

@router.get("", response_model=list[dict])
def list_insights(
    industry: str | None = Query(default=None, description="Filter by industry"),
    service: str | None = Query(default=None, description="Filter by service"),
) -> list[dict]:
    """List published insights sorted by publishedDate descending."""
    rows = _get_service().list_insights(industry=industry, service=service)
    return [_format_row(r) for r in rows]


@router.get("/{slug}", response_model=dict)
def get_insight(slug: str) -> dict:
    """Return a single published insight by slug."""
    row = _get_service().get_insight(slug)
    if not row:
        raise HTTPException(status_code=404, detail="Insight not found.")
    return _format_row(row)


# ── Admin endpoints ────────────────────────────────────────────────────────────

class InsightUpsertRequest(BaseModel):
    slug: str
    tags: str = ""
    industry: str = ""
    service: str = ""
    title: str
    excerpt: str = ""
    imageUrl: str = Field(default="")
    isPublished: bool = False
    publishedDate: str | None = None
    metaTitle: str = ""
    metaDescription: str = ""
    content: str = ""


@router.post("", response_model=dict, status_code=201)
def upsert_insight(
    payload: InsightUpsertRequest,
    _: None = Depends(_require_admin),
) -> dict:
    """Create or update an insight (requires X-Admin-Key header)."""
    data = {
        "slug": payload.slug,
        "tags": payload.tags,
        "industry": payload.industry,
        "service": payload.service,
        "title": payload.title,
        "excerpt": payload.excerpt,
        "image_url": payload.imageUrl,
        "is_published": payload.isPublished,
        "published_date": payload.publishedDate,
        "meta_title": payload.metaTitle,
        "meta_description": payload.metaDescription,
        "content": payload.content,
    }
    row = _get_service().upsert_insight(data)
    return _format_row(row)
