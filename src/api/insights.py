"""Insights API — JSON-based schema with comprehensive error handling and validation."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import ValidationError

from src.models.schemas import InsightCreate, InsightUpdate
from src.services.content_db import get_content_db_service

LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/insights",
    tags=["insights"],
    responses={
        404: {"description": "Insight not found"},
        500: {"description": "Internal server error"},
    },
)


def _to_response(row: dict) -> dict:
    """Map a DB row to the frontend-compatible response shape."""

    return {
        "id": row["id"],
        "page": row["page"],
        "slug": row.get("slug"),
        "version": row["version"],
        "tags": row.get("tags"),
        "industry": row.get("industry"),
        "service": row.get("service"),
        "meta": row["meta"],
        "sections": row["sections"],
        "isPublished": row["is_published"],
        "createdAt": row["created_at"].isoformat() if row.get("created_at") else None,
        "updatedAt": row["updated_at"].isoformat() if row.get("updated_at") else None,
    }


# ─── Public endpoints (frontend consumption) ──────────────────────────────────


@router.get(
    "",
    response_model=list[dict],
    summary="List published insights",
    description="Retrieve a list of published insights with optional filtering by industry and service",
)
def list_insights(
    industry: Optional[str] = Query(None, max_length=100, description="Filter by industry category"),
    service: Optional[str] = Query(None, max_length=100, description="Filter by service category"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip for pagination"),
):
    """List published insights, ordered by creation date descending.
    
    Args:
        industry: Optional industry filter
        service: Optional service filter
        limit: Maximum results (1-500)
        offset: Results to skip for pagination
        
    Returns:
        List of insight objects
        
    Raises:
        HTTPException: 500 if database error occurs
    """
    try:
        svc = get_content_db_service()
        rows = svc.list_insights(
            published_only=True, industry=industry, service=service, limit=limit, offset=offset
        )
        return [_to_response(r) for r in rows]
    except Exception as e:
        LOGGER.error(f"Error listing insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insights"
        )


# ─── Admin: list all (including unpublished) ───────────────────────────────────


@router.get(
    "/admin/all",
    response_model=list[dict],
    summary="List all insights (admin)",
    description="Retrieve all insights including unpublished ones. For admin use only.",
)
def list_all_insights(
    industry: Optional[str] = Query(None, max_length=100, description="Filter by industry"),
    service: Optional[str] = Query(None, max_length=100, description="Filter by service"),
    limit: int = Query(100, ge=1, le=500, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results to skip"),
):
    """List all insights including unpublished (admin endpoint).
    
    Returns:
        List of all insight objects including unpublished
    """
    try:
        svc = get_content_db_service()
        rows = svc.list_insights(
            published_only=False, industry=industry, service=service, limit=limit, offset=offset
        )
        return [_to_response(r) for r in rows]
    except Exception as e:
        LOGGER.error(f"Error listing all insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insights"
        )


@router.get(
    "/by-slug/{slug}",
    summary="Get insight by slug",
    description="Retrieve a single published insight by its URL slug",
)
def get_insight_by_slug(slug: str):
    """Get a single published insight by slug.
    
    Args:
        slug: URL-friendly slug identifier
        
    Returns:
        Insight object
        
    Raises:
        HTTPException: 404 if not found or not published
    """
    try:
        svc = get_content_db_service()
        row = svc.get_insight_by_slug(slug)
        
        if not row:
            LOGGER.info(f"Insight not found with slug: {slug}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insight with slug '{slug}' not found"
            )
            
        if not row["is_published"]:
            LOGGER.info(f"Attempted access to unpublished insight: {slug}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insight not found"
            )
            
        return _to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error retrieving insight by slug {slug}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insight"
        )


@router.get(
    "/{page}",
    summary="Get insight by page ID",
    description="Retrieve a single published insight by its page identifier",
)
def get_insight(page: str):
    """Get a single published insight by page identifier.
    
    Args:
        page: Unique page identifier
        
    Returns:
        Insight object
        
    Raises:
        HTTPException: 404 if not found or not published
    """
    try:
        svc = get_content_db_service()
        row = svc.get_insight_by_page(page)
        
        if not row:
            LOGGER.info(f"Insight not found with page: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insight with page '{page}' not found"
            )
            
        if not row["is_published"]:
            LOGGER.info(f"Attempted access to unpublished insight: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insight not found"
            )
            
        return _to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error retrieving insight by page {page}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve insight"
        )


# ─── CRUD endpoints ───────────────────────────────────────────────────────────


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create new insight",
    description="Create a new insight with validation",
    responses={
        201: {"description": "Insight created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Insight with this page ID already exists"},
    },
)
def create_insight(payload: InsightCreate) -> dict:
    """Create a new insight.
    
    Args:
        payload: Insight data to create
        
    Returns:
        Created insight object
        
    Raises:
        HTTPException: 400 for validation errors, 409 for duplicates, 500 for server errors
    """
    try:
        svc = get_content_db_service()

        # Convert Pydantic model to dict
        data = payload.model_dump(by_alias=False)
        
        # Convert meta to dict if it's a Pydantic model
        if hasattr(data.get("meta"), "model_dump"):
            data["meta"] = data["meta"].model_dump(by_alias=False)

        row = svc.create_insight(data)
        LOGGER.info(f"Successfully created insight: {payload.page}")
        return _to_response(row)
        
    except ValidationError as e:
        LOGGER.warning(f"Validation error creating insight: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "duplicate key" in error_msg or "unique" in error_msg:
            LOGGER.warning(f"Duplicate insight page: {payload.page}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insight with page '{payload.page}' already exists"
            )
        LOGGER.error(f"Error creating insight: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create insight"
        )


@router.put(
    "/{page}",
    summary="Update insight",
    description="Update an existing insight by page identifier",
    responses={
        200: {"description": "Insight updated successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Insight not found"},
    },
)
def update_insight(page: str, payload: InsightUpdate) -> dict:
    """Update an existing insight.
    
    Args:
        page: Page identifier of insight to update
        payload: Updated insight data
        
    Returns:
        Updated insight object
        
    Raises:
        HTTPException: 400 for validation, 404 if not found, 500 for errors
    """
    try:
        svc = get_content_db_service()
        existing = svc.get_insight_by_page(page)
        
        if not existing:
            LOGGER.info(f"Insight not found for update: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insight with page '{page}' not found"
            )

        data = payload.model_dump(by_alias=False, exclude_none=True)
        
        # Convert meta to dict if it's a Pydantic model
        if "meta" in data and hasattr(data["meta"], "model_dump"):
            data["meta"] = data["meta"].model_dump(by_alias=False)

        row = svc.update_insight(page, data)
        
        if not row:
            LOGGER.error(f"Update returned no result for page: {page}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Update failed"
            )
            
        LOGGER.info(f"Successfully updated insight: {page}")
        return _to_response(row)
        
    except HTTPException:
        raise
    except ValidationError as e:
        LOGGER.warning(f"Validation error updating insight: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        LOGGER.error(f"Error updating insight {page}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update insight"
        )


@router.delete(
    "/{page}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete insight",
    description="Delete an insight by page identifier",
    responses={
        204: {"description": "Insight deleted successfully"},
        404: {"description": "Insight not found"},
    },
)
def delete_insight(page: str) -> None:
    """Delete an insight by page identifier.
    
    Args:
        page: Page identifier of insight to delete
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if not found, 500 for errors
    """
    try:
        svc = get_content_db_service()
        deleted = svc.delete_insight(page)
        
        if not deleted:
            LOGGER.info(f"Insight not found for deletion: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insight with page '{page}' not found"
            )
            
        LOGGER.info(f"Successfully deleted insight: {page}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error deleting insight {page}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete insight"
        )


# ─── Seed endpoint ─────────────────────────────────────────────────────────────


@router.post(
    "/seed",
    summary="Seed insights from JSON",
    description="Load and seed insights from the Insights JSON.json file. Idempotent operation.",
    responses={
        200: {"description": "Insights seeded successfully"},
        500: {"description": "Seeding failed"},
    },
)
def seed_insights_endpoint() -> dict:
    """Seed insights from static JSON data.
    
    This operation is idempotent - safe to call multiple times.
    Existing insights will be updated, new ones will be created.
    
    Returns:
        Summary of seeding operation including counts
        
    Raises:
        HTTPException: 500 if seeding fails
    """
    try:
        from src.services.seed_data import seed_insights
        
        svc = get_content_db_service()
        result = seed_insights(svc)
        
        if result.get('error'):
            LOGGER.error(f"Seeding error: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Seeding failed: {result['error']}"
            )
        
        LOGGER.info(f"Successfully seeded {result['seeded']} insights")
        return {"message": "Insights seeded successfully", **result}
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error seeding insights: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed insights"
        )
