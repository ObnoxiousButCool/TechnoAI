"""Seed data for Case Studies schema.

Contains the data from Case Study JSON.json file.
The seed process is idempotent — uses ON CONFLICT (page) DO UPDATE to avoid duplicates.
"""

from __future__ import annotations

import logging

from src.services.content_db import ContentDBService

LOGGER = logging.getLogger(__name__)


# ─── Case Study seed data (from Case Study JSON.json) ─────────────────────────

CASE_STUDIES_SEED: list[dict] = [
    {
        "page": "case-study-healthcare-mobile-platform",
        "slug": "healthcare-mobile-platform",
        "version": 1,
        "tags": "HEALTHCARE • MOBILE PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "meta_title": "Mobile Platform Increases Company Value for Healthcare Benefits Provider — Technossus",
        "meta_description": "A leading healthcare benefits provider needed a mobile strategy to extend services to brokers, employers, and end users, with seamless data integration across insurers, brokers, and enterprise systems.",
        "tag_line": "HEALTHCARE • MOBILE PLATFORM",
        "meta": {
            "title": "Mobile Platform Increases Company Value for Healthcare Benefits Provider — Technossus",
            "description": "A leading healthcare benefits provider needed a mobile strategy to extend services to brokers, employers, and end users, with seamless data integration across insurers, brokers, and enterprise systems.",
            "canonical_path": "/case-studies/healthcare-mobile-platform",
            "og_image_url": "/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.optimized.webp"
        },
        "sections": [
            {
                "template": "CASE_STUDY_HERO_SECTION",
                "id": "healthcare-hero",
                "tagLine": "HEALTHCARE • MOBILE PLATFORM",
                "title": "Mobile Platform Increases Company Value for Healthcare Benefits Provider",
                "heroImageUrl": "/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.optimized.webp"
            },
            {
                "template": "CLIENT_CHALLENGE_SECTION",
                "id": "healthcare-challenge",
                "left": {
                    "clientName": "Healthcare Benefits Provider",
                    "clientDescription": "A leading healthcare benefits provider needed a mobile strategy to extend services to brokers, employers, and end users, with seamless data integration across insurers, brokers, and enterprise systems."
                },
                "right": {
                    "heading": "Disconnected systems limiting mobile reach",
                    "body": "The client lacked a unified mobile presence to serve brokers, employers, and end users. Existing systems were siloed across insurers and enterprise platforms, making it impossible to deliver a consistent, real-time experience on mobile devices."
                }
            },
            {
                "template": "SOLUTION_SECTION",
                "id": "healthcare-solution",
                "heading": "Scalable mobile platform with deep enterprise integration",
                "left": {
                    "body": "Technossus designed and delivered a scalable mobile platform that unified data flows across insurers, brokers, and enterprise systems. The solution provided tailored experiences for each user type — brokers, employers, and members — while maintaining a single source of truth."
                },
                "right": {
                    "capabilities": [
                        "Cross-platform mobile application for iOS and Android",
                        "Real-time data integration with insurer and broker systems",
                        "Role-based experiences for brokers, employers, and members",
                        "Secure authentication and HIPAA-compliant data handling",
                        "API layer connecting legacy enterprise systems to mobile",
                        "Scalable architecture supporting rapid user growth"
                    ]
                }
            },
            {
                "template": "IMPACT_SECTION",
                "id": "healthcare-impact",
                "heading": "Greater reach. Higher value. Faster growth.",
                "description": "The mobile platform expanded the client's market reach, improved broker productivity, and directly contributed to increased company valuation.",
                "context": {
                    "label": "MEASURABLE OUTCOMES",
                    "body": "The platform enabled the client to serve a broader user base with a consistent mobile experience, strengthening relationships with brokers and employers while improving operational efficiency."
                },
                "impactCards": [
                    {
                        "title": "Expanded Market Reach",
                        "body": "The mobile platform enabled the client to extend services to brokers, employers, and end users who previously had no mobile access to benefits data."
                    },
                    {
                        "title": "Seamless Data Integration",
                        "body": "Real-time integration across insurers, brokers, and enterprise systems eliminated manual data reconciliation and improved data accuracy."
                    },
                    {
                        "title": "Increased Company Valuation",
                        "body": "The mobile platform became a key differentiator, directly contributing to increased company value and competitive positioning in the market."
                    },
                    {
                        "title": "Improved Broker Productivity",
                        "body": "Brokers gained instant mobile access to client data and plan information, reducing response times and improving service quality."
                    }
                ],
                "industryStats": [
                    {"value": "90%", "label": "Of healthcare consumers prefer mobile access to benefits"},
                    {"value": "$4.5T", "label": "U.S. healthcare spending annually"},
                    {"value": "60%", "label": "Of brokers report mobile tools improve client retention"},
                    {"value": "3x", "label": "Faster benefits enrollment via mobile vs. desktop"}
                ]
            },
            {
                "template": "RELATED_CASE_STUDIES_SECTION",
                "id": "healthcare-related",
                "items": [
                    {
                        "tags": "HEALTHCARE • CRM INTEGRATION",
                        "title": "CRM with Complex External Integrations Launches On Time",
                        "excerpt": "A leading healthcare insurance provider needed a CRM integrating data from state and federal platforms under evolving regulatory requirements and a fixed go-live deadline.",
                        "imageUrl": "/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.optimized.webp",
                        "slug": "clinical-trial-platform"
                    },
                    {
                        "tags": "LIFE SCIENCES • CLINICAL PLATFORM",
                        "title": "Clinical Trial Platform Accelerates Drug Development Timelines",
                        "excerpt": "A unified digital platform to manage trial data, patient recruitment, and regulatory compliance from a single source of truth.",
                        "imageUrl": "/assets/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.optimized.webp",
                        "slug": "clinical-trial-platform"
                    },
                    {
                        "tags": "HEALTHCARE • REVENUE CYCLE",
                        "title": "Revenue Cycle Automation Reduces Denials and Improves Cash Flow",
                        "excerpt": "Intelligent pre-submission validation catches errors before claims are submitted, routes exceptions automatically, and gives finance teams real-time visibility.",
                        "imageUrl": "/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.optimized.webp",
                        "slug": "clinical-trial-platform"
                    }
                ]
            }
        ],
        "is_published": True
    }
]


def seed_case_studies(svc: ContentDBService) -> dict:
    """Seed case studies from the new JSON-based schema.
    
    Args:
        svc: ContentDBService instance
        
    Returns:
        Dictionary with seeded count and total count
    """
    seeded_count = 0
    failed_count = 0
    
    for case_study_data in CASE_STUDIES_SEED:
        try:
            svc.upsert_case_study(case_study_data)
            seeded_count += 1
            LOGGER.info(f"Seeded case study: {case_study_data['page']}")
        except Exception as e:
            failed_count += 1
            LOGGER.error(f"Failed to seed case study {case_study_data['page']}: {e}", exc_info=True)

    total = len(CASE_STUDIES_SEED)
    LOGGER.info(f"Case studies seeding complete: {seeded_count}/{total} successful, {failed_count} failed")
    return {"seeded": seeded_count, "total": total, "failed": failed_count}


# ─── Insights seed data ────────────────────────────────────────────────────────


def seed_insights(svc: ContentDBService) -> dict:
    """Seed insights from the Insights JSON.json file.
    
    This function loads the JSON data dynamically and seeds it into the database.
    The operation is idempotent - existing records will be updated.
    
    Args:
        svc: ContentDBService instance
        
    Returns:
        Dictionary with seeded count, total count, and any error messages
    """
    import json
    from pathlib import Path
    
    # Construct path to JSON file
    json_file = Path(__file__).parent.parent.parent / "Insights JSON.json"
    
    # Validate file exists
    if not json_file.exists():
        error_msg = f"Insights JSON file not found at {json_file}"
        LOGGER.error(error_msg)
        return {"seeded": 0, "total": 0, "failed": 0, "error": "File not found"}
    
    # Load and parse JSON
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            insights_data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse Insights JSON: {e}"
        LOGGER.error(error_msg)
        return {"seeded": 0, "total": 0, "failed": 0, "error": "Invalid JSON"}
    except Exception as e:
        error_msg = f"Failed to read Insights JSON: {e}"
        LOGGER.error(error_msg, exc_info=True)
        return {"seeded": 0, "total": 0, "failed": 0, "error": str(e)}
    
    # Handle both list and single object formats
    if not isinstance(insights_data, list):
        insights_data = [insights_data] if insights_data else []
    
    total_count = len(insights_data)
    seeded_count = 0
    failed_count = 0
    
    # Seed each insight
    for insight_data in insights_data:
        try:
            # Validate required fields
            if "page" not in insight_data:
                LOGGER.warning("Skipping insight without 'page' field")
                failed_count += 1
                continue
            
            if "meta" not in insight_data:
                LOGGER.warning(f"Skipping insight {insight_data['page']} without 'meta' field")
                failed_count += 1
                continue
            
            if "sections" not in insight_data:
                LOGGER.warning(f"Skipping insight {insight_data['page']} without 'sections' field")
                failed_count += 1
                continue
            
            # Set defaults for optional fields
            insight_data.setdefault("version", 1)
            insight_data.setdefault("is_published", True)
            insight_data.setdefault("slug", None)
            insight_data.setdefault("tags", None)
            insight_data.setdefault("industry", None)
            insight_data.setdefault("service", None)
            
            # Upsert insight
            svc.upsert_insight(insight_data)
            seeded_count += 1
            LOGGER.info(f"Seeded insight: {insight_data['page']}")
            
        except Exception as e:
            failed_count += 1
            page_id = insight_data.get('page', 'unknown')
            LOGGER.error(f"Failed to seed insight {page_id}: {e}", exc_info=True)
    
    LOGGER.info(
        f"Insights seeding complete: {seeded_count}/{total_count} successful, {failed_count} failed"
    )
    return {"seeded": seeded_count, "total": total_count, "failed": failed_count}
