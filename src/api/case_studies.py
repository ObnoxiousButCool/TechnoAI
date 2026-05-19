"""Case studies API routes."""

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
router = APIRouter(prefix="/case-studies", tags=["case-studies"])

_admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_service() -> ContentService:
    return ContentService(get_settings().database_url)


def _require_admin(x_admin_key: str | None = Depends(_admin_key_header)) -> None:
    settings = get_settings()
    if not x_admin_key or x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Forbidden")


def _format_row(row: dict[str, Any]) -> dict[str, Any]:
    """Map snake_case DB row to camelCase JSON for the frontend.

    Handles datetime serialisation and JSONB fields that are already
    deserialised by psycopg into native Python objects.
    """
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
        # Detail-page fields
        "tag_line": "tagLine",
        "hero_image": "heroImage",
        "client_name": "clientName",
        "client_description": "clientDescription",
        "challenge_heading": "challengeHeading",
        "challenge_body": "challengeBody",
        "solution_heading": "solutionHeading",
        "solution_body": "solutionBody",
        "solution_capabilities": "solutionCapabilities",
        "impact_heading": "impactHeading",
        "impact_description": "impactDescription",
        "impact_context_label": "impactContextLabel",
        "impact_context_body": "impactContextBody",
        "impact_cards": "impactCards",
        "industry_stats": "industryStats",
        "related_case_studies": "relatedCaseStudies",
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
def list_case_studies(
    industry: str | None = Query(default=None, description="Filter by industry"),
    service: str | None = Query(default=None, description="Filter by service"),
) -> list[dict]:
    """List published case studies sorted by publishedDate descending."""
    rows = _get_service().list_case_studies(industry=industry, service=service)
    return [_format_row(r) for r in rows]


@router.get("/{slug}", response_model=dict)
def get_case_study(slug: str) -> dict:
    """Return full case study detail for the given slug."""
    row = _get_service().get_case_study(slug)
    if not row:
        raise HTTPException(status_code=404, detail="Case study not found.")
    return _format_row(row)


# ── Admin endpoints ────────────────────────────────────────────────────────────

class ImpactCard(BaseModel):
    title: str
    body: str


class IndustryStat(BaseModel):
    value: str
    label: str


class RelatedCaseStudy(BaseModel):
    tags: str
    title: str
    excerpt: str
    image: str
    slug: str


class CaseStudyUpsertRequest(BaseModel):
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
    # Detail-page fields
    tagLine: str = ""
    heroImage: str = ""
    clientName: str = ""
    clientDescription: str = ""
    challengeHeading: str = ""
    challengeBody: str = ""
    solutionHeading: str = ""
    solutionBody: str = ""
    solutionCapabilities: list[str] = Field(default_factory=list)
    impactHeading: str = ""
    impactDescription: str = ""
    impactContextLabel: str | None = None
    impactContextBody: str | None = None
    impactCards: list[ImpactCard] = Field(default_factory=list)
    industryStats: list[IndustryStat] = Field(default_factory=list)
    relatedCaseStudies: list[RelatedCaseStudy] = Field(default_factory=list)


@router.post("", response_model=dict, status_code=201)
def upsert_case_study(
    payload: CaseStudyUpsertRequest,
    _: None = Depends(_require_admin),
) -> dict:
    """Create or update a case study (requires X-Admin-Key header)."""
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
        "tag_line": payload.tagLine,
        "hero_image": payload.heroImage,
        "client_name": payload.clientName,
        "client_description": payload.clientDescription,
        "challenge_heading": payload.challengeHeading,
        "challenge_body": payload.challengeBody,
        "solution_heading": payload.solutionHeading,
        "solution_body": payload.solutionBody,
        "solution_capabilities": payload.solutionCapabilities,
        "impact_heading": payload.impactHeading,
        "impact_description": payload.impactDescription,
        "impact_context_label": payload.impactContextLabel,
        "impact_context_body": payload.impactContextBody,
        "impact_cards": [c.model_dump() for c in payload.impactCards],
        "industry_stats": [s.model_dump() for s in payload.industryStats],
        "related_case_studies": [r.model_dump() for r in payload.relatedCaseStudies],
    }
    row = _get_service().upsert_case_study(data)
    return _format_row(row)
