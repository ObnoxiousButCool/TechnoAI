"""Case Studies API — New JSON-based schema.

Provides endpoints for managing case studies with JSON-based flexible schema.
Includes public endpoints for frontend consumption and admin endpoints for management.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import ValidationError

from src.models.schemas import CaseStudyNewCreate, CaseStudyNewUpdate, CaseStudyNewResponse
from src.services.content_db import get_content_db_service

LOGGER = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/case-studies",
    tags=["case-studies"],
    responses={
        500: {"description": "Internal server error"},
        400: {"description": "Bad request - validation error"},
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
        "tagLine": row.get("tag_line"),
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
    summary="List published case studies",
    description="Retrieve a list of published case studies with optional filtering",
    responses={
        200: {"description": "List of case studies retrieved successfully"},
    },
)
def list_case_studies(
    industry: Optional[str] = Query(None, max_length=100, description="Filter by industry"),
    service: Optional[str] = Query(None, max_length=100, description="Filter by service"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List published case studies, ordered by creation date descending.
    
    Args:
        industry: Filter by industry (optional)
        service: Filter by service (optional)
        limit: Maximum number of results (1-1000, default 100)
        offset: Number of results to skip (default 0)
        
    Returns:
        List of published case study objects
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        svc = get_content_db_service()
        rows = svc.list_case_studies_new(
            published_only=True, industry=industry, service=service, limit=limit, offset=offset
        )
        LOGGER.info(f"Retrieved {len(rows)} case studies (industry={industry}, service={service})")
        return [_to_response(r) for r in rows]
    except Exception as e:
        LOGGER.error(f"Error listing case studies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve case studies"
        )


# ─── Admin: list all (including unpublished) ───────────────────────────────────


@router.get(
    "/admin/all",
    response_model=list[dict],
    summary="List all case studies (admin)",
    description="Retrieve all case studies including unpublished ones. Admin access required.",
    responses={
        200: {"description": "List of all case studies retrieved successfully"},
    },
)
def list_all_case_studies(
    industry: Optional[str] = Query(None, max_length=100, description="Filter by industry"),
    service: Optional[str] = Query(None, max_length=100, description="Filter by service"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """List all case studies including unpublished (admin access).
    
    Args:
        industry: Filter by industry (optional)
        service: Filter by service (optional)
        limit: Maximum number of results (1-1000, default 100)
        offset: Number of results to skip (default 0)
        
    Returns:
        List of all case study objects (published and unpublished)
        
    Raises:
        HTTPException: 500 if database operation fails
    """
    try:
        svc = get_content_db_service()
        rows = svc.list_case_studies_new(
            published_only=False, industry=industry, service=service, limit=limit, offset=offset
        )
        LOGGER.info(f"Admin retrieved {len(rows)} case studies (all statuses)")
        return [_to_response(r) for r in rows]
    except Exception as e:
        LOGGER.error(f"Error listing all case studies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve case studies"
        )


@router.get(
    "/by-slug/{slug}",
    summary="Get case study by slug",
    description="Retrieve a single published case study by its URL slug",
    responses={
        200: {"description": "Case study retrieved successfully"},
        404: {"description": "Case study not found or not published"},
    },
)
def get_case_study_by_slug(slug: str):
    """Get a single published case study by slug.
    
    Args:
        slug: URL-friendly slug identifier
        
    Returns:
        Case study object
        
    Raises:
        HTTPException: 404 if not found or not published, 500 for errors
    """
    try:
        svc = get_content_db_service()
        row = svc.get_case_study_by_slug_new(slug)
        
        if not row:
            LOGGER.info(f"Case study not found by slug: {slug}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case study with slug '{slug}' not found"
            )
            
        if not row["is_published"]:
            LOGGER.info(f"Case study found but not published: {slug}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case study not found"
            )
            
        LOGGER.info(f"Retrieved case study by slug: {slug}")
        return _to_response(row)
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error retrieving case study by slug {slug}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve case study"
        )


@router.get(
    "/{page}",
    summary="Get case study by page ID",
    description="Retrieve a single published case study by its page identifier",
    responses={
        200: {"description": "Case study retrieved successfully"},
        404: {"description": "Case study not found or not published"},
    },
)
def get_case_study(page: str):
    """Get a single published case study by page identifier.
    
    Args:
        page: Page identifier
        
    Returns:
        Case study object
        
    Raises:
        HTTPException: 404 if not found or not published, 500 for errors
    """
    try:
        svc = get_content_db_service()
        row = svc.get_case_study_by_page(page)
        
        if not row:
            LOGGER.info(f"Case study not found by page: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case study with page '{page}' not found"
            )
            
        if not row["is_published"]:
            LOGGER.info(f"Case study found but not published: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case study not found"
            )
            
        LOGGER.info(f"Retrieved case study by page: {page}")
        return _to_response(row)
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error retrieving case study {page}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve case study"
        )


# ─── CRUD endpoints ───────────────────────────────────────────────────────────


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create new case study",
    description="Create a new case study with validation",
    responses={
        201: {"description": "Case study created successfully"},
        400: {"description": "Invalid input data"},
        409: {"description": "Case study with this page ID already exists"},
    },
)
def create_case_study(payload: CaseStudyNewCreate):
    """Create a new case study.
    
    Args:
        payload: Case study data to create
        
    Returns:
        Created case study object
        
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

        row = svc.create_case_study_new(data)
        LOGGER.info(f"Successfully created case study: {payload.page}")
        return _to_response(row)
        
    except ValidationError as e:
        LOGGER.warning(f"Validation error creating case study: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        error_msg = str(e).lower()
        if "duplicate key" in error_msg or "unique" in error_msg:
            LOGGER.warning(f"Duplicate case study page: {payload.page}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Case study with page '{payload.page}' already exists"
            )
        LOGGER.error(f"Error creating case study: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create case study"
        )


@router.put(
    "/{page}",
    summary="Update case study",
    description="Update an existing case study by page identifier",
    responses={
        200: {"description": "Case study updated successfully"},
        400: {"description": "Invalid input data"},
        404: {"description": "Case study not found"},
    },
)
def update_case_study(page: str, payload: CaseStudyNewUpdate):
    """Update an existing case study.
    
    Args:
        page: Page identifier of case study to update
        payload: Updated case study data
        
    Returns:
        Updated case study object
        
    Raises:
        HTTPException: 400 for validation, 404 if not found, 500 for errors
    """
    try:
        svc = get_content_db_service()
        existing = svc.get_case_study_by_page(page)
        
        if not existing:
            LOGGER.info(f"Case study not found for update: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case study with page '{page}' not found"
            )

        data = payload.model_dump(by_alias=False, exclude_none=True)
        
        # Convert meta to dict if it's a Pydantic model
        if "meta" in data and hasattr(data["meta"], "model_dump"):
            data["meta"] = data["meta"].model_dump(by_alias=False)

        row = svc.update_case_study_new(page, data)
        
        if not row:
            LOGGER.error(f"Update returned no result for page: {page}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Update failed"
            )
            
        LOGGER.info(f"Successfully updated case study: {page}")
        return _to_response(row)
        
    except HTTPException:
        raise
    except ValidationError as e:
        LOGGER.warning(f"Validation error updating case study: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        LOGGER.error(f"Error updating case study {page}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update case study"
        )


@router.delete(
    "/{page}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete case study",
    description="Delete a case study by page identifier",
    responses={
        204: {"description": "Case study deleted successfully"},
        404: {"description": "Case study not found"},
    },
)
def delete_case_study(page: str):
    """Delete a case study by page identifier.
    
    Args:
        page: Page identifier of case study to delete
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if not found, 500 for errors
    """
    try:
        svc = get_content_db_service()
        deleted = svc.delete_case_study_new(page)
        
        if not deleted:
            LOGGER.info(f"Case study not found for deletion: {page}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Case study with page '{page}' not found"
            )
            
        LOGGER.info(f"Successfully deleted case study: {page}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        LOGGER.error(f"Error deleting case study {page}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete case study"
        )

    svc = get_content_db_service()
    deleted = svc.delete_case_study_new(page)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case study not found")
    return None


# ─── Seed endpoint ─────────────────────────────────────────────────────────────


@router.post(
    "/seed",
    summary="Seed case studies from JSON",
    description="Load and seed case studies from static JSON data. Idempotent operation.",
    responses={
        200: {"description": "Case studies seeded successfully"},
        500: {"description": "Seeding failed"},
    },
)
def seed_case_studies_endpoint():
    """Seed case studies from static JSON data.
    
    This operation is idempotent - safe to call multiple times.
    Existing case studies will be updated, new ones will be created.
    
    Returns:
        Summary of seeding operation including counts
        
    Raises:
        HTTPException: 500 if seeding fails
    """
    try:
        from src.services.seed_data_new import seed_case_studies_new
        
        svc = get_content_db_service()
        result = seed_case_studies_new(svc)
        
        if result.get('failed', 0) > 0:
            LOGGER.warning(f"Seeding completed with {result['failed']} failures")
        
        LOGGER.info(f"Successfully seeded {result['seeded']}/{result['total']} case studies")
        return {"message": "Case studies seeded successfully", **result}
        
    except Exception as e:
        LOGGER.error(f"Error seeding case studies: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to seed case studies"
        )


