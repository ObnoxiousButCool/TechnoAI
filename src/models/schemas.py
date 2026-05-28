"""Pydantic schemas for Case Studies and Insights."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict
import re


# ─── Case Study schemas ────────────────────────────────────────────────────


class CaseStudyMeta(BaseModel):
    """Metadata for case study SEO and social sharing."""
    
    title: str = Field(..., min_length=1, max_length=200, description="SEO page title")
    description: str = Field(..., min_length=1, max_length=500, description="SEO meta description")
    canonical_path: str = Field(..., alias="canonicalPath", pattern=r"^/[a-z0-9-/]+$", description="Canonical URL path")
    og_image_url: str = Field(..., alias="ogImageUrl", description="Open Graph image URL")

    model_config = ConfigDict(populate_by_name=True)


class CaseStudySection(BaseModel):
    template: str
    id: str
    # Additional fields vary by template type, stored as arbitrary dict
    
    class Config:
        extra = "allow"  # Allow additional fields not explicitly defined


class CaseStudy(BaseModel):
    """Case study with flexible section structure."""
    
    page: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$", description="Unique page identifier")
    slug: Optional[str] = Field(None, max_length=255, pattern=r"^[a-z0-9-]*$", description="URL-friendly slug")
    version: int = Field(default=1, ge=1, description="Content version number")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    industry: Optional[str] = Field(None, max_length=100, description="Industry category")
    service: Optional[str] = Field(None, max_length=100, description="Service category")
    tag_line: Optional[str] = Field(None, max_length=200, alias="tagLine", description="Short tagline")
    meta: CaseStudyMeta = Field(..., description="SEO metadata")
    sections: list[dict] = Field(..., min_length=1, description="Flexible section structure")
    is_published: bool = Field(default=False, alias="isPublished", description="Publication status")

    model_config = ConfigDict(populate_by_name=True)
    
    @field_validator('page', 'slug')
    @classmethod
    def validate_slug_format(cls, v: Optional[str]) -> Optional[str]:
        """Ensure slug contains only lowercase letters, numbers, and hyphens."""
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Must contain only lowercase letters, numbers, and hyphens')
        return v


class CaseStudyCreate(CaseStudy):
    pass


class CaseStudyUpdate(BaseModel):
    """Partial update model for case studies."""
    
    slug: Optional[str] = Field(None, max_length=255, pattern=r"^[a-z0-9-]*$")
    version: Optional[int] = Field(None, ge=1)
    tags: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    service: Optional[str] = Field(None, max_length=100)
    tag_line: Optional[str] = Field(None, max_length=200, alias="tagLine")
    meta: Optional[CaseStudyMeta] = None
    sections: Optional[list[dict]] = None
    is_published: Optional[bool] = Field(None, alias="isPublished")

    model_config = ConfigDict(populate_by_name=True)


class CaseStudyResponse(CaseStudy):
    """Case study response model with timestamps."""
    
    id: int = Field(..., description="Unique database identifier")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


# ─── Insight schemas (JSON-based section structure) ───────────────────────────


class InsightMeta(BaseModel):
    """Metadata for insight SEO."""
    
    title: str = Field(..., min_length=1, max_length=200, description="SEO page title")
    description: str = Field(..., min_length=1, max_length=500, description="SEO meta description")
    canonical_path: str = Field(..., alias="canonicalPath", pattern=r"^/[a-z0-9-/]+$", description="Canonical URL path")

    model_config = ConfigDict(populate_by_name=True)


class Insight(BaseModel):
    """Insight with JSON-based flexible section structure."""
    
    page: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$", description="Unique page identifier")
    slug: Optional[str] = Field(None, max_length=255, pattern=r"^[a-z0-9-]*$", description="URL-friendly slug")
    version: int = Field(default=1, ge=1, description="Content version number")
    tags: Optional[str] = Field(None, max_length=500, description="Comma-separated tags")
    industry: Optional[str] = Field(None, max_length=100, description="Industry category")
    service: Optional[str] = Field(None, max_length=100, description="Service category")
    meta: InsightMeta = Field(..., description="SEO metadata")
    sections: list[dict] = Field(..., min_length=1, description="Flexible section structure")
    is_published: bool = Field(default=False, alias="isPublished", description="Publication status")

    model_config = ConfigDict(populate_by_name=True)
    
    @field_validator('page', 'slug')
    @classmethod
    def validate_slug_format(cls, v: Optional[str]) -> Optional[str]:
        """Ensure slug contains only lowercase letters, numbers, and hyphens."""
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Must contain only lowercase letters, numbers, and hyphens')
        return v


class InsightCreate(Insight):
    pass


class InsightUpdate(BaseModel):
    """Partial update model for insights."""
    
    slug: Optional[str] = Field(None, max_length=255, pattern=r"^[a-z0-9-]*$")
    version: Optional[int] = Field(None, ge=1)
    tags: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    service: Optional[str] = Field(None, max_length=100)
    meta: Optional[InsightMeta] = None
    sections: Optional[list[dict]] = None
    is_published: Optional[bool] = Field(None, alias="isPublished")

    model_config = ConfigDict(populate_by_name=True)


class InsightResponse(Insight):
    """Insight response model with timestamps."""
    
    id: int = Field(..., description="Unique database identifier")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
