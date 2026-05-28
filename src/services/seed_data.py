"""Seed data for Case Studies and Insights.

Contains the current static data from the frontend, mapped to the DB schema.
The seed process is idempotent — uses ON CONFLICT (slug) DO UPDATE to avoid duplicates.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.services.content_db import ContentDBService, SHARED_ASSETS_PATH

# ─── Image asset mapping ───────────────────────────────────────────────────────
# All hero images are stored under the shared assets path.
# Original paths from frontend are normalized to shared location.
IMAGE_MAP = {
    "fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png": (
        f"{SHARED_ASSETS_PATH}/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"
    ),
    "d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png": (
        f"{SHARED_ASSETS_PATH}/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png"
    ),
}


def _img(original_path: str) -> str:
    """Normalize an asset path to the shared upload location."""

    if not original_path:
        return ""
    filename = original_path.rsplit("/", 1)[-1] if "/" in original_path else original_path
    return IMAGE_MAP.get(filename, f"{SHARED_ASSETS_PATH}/{filename}")


# ─── Case Study seed data ──────────────────────────────────────────────────────

CASE_STUDIES_SEED: list[dict] = [
    {
        "slug": "healthcare-mobile-platform",
        "tags": "HEALTHCARE • MOBILE PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "Mobile Platform Increases Company Value for Healthcare Benefits Provider",
        "excerpt": (
            "A leading healthcare benefits provider needed a mobile strategy to extend "
            "services to brokers, employers, and end users. Technossus delivered a scalable "
            "platform with seamless data integration across insurers, brokers, and enterprise systems."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 1, 15, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Mobile Platform Increases Company Value | Technossus",
        "meta_description": (
            "See how Technossus delivered a scalable mobile platform for a healthcare "
            "benefits provider, integrating data across insurers, brokers, and enterprise systems."
        ),
        "tag_line": "HEALTHCARE • MOBILE PLATFORM",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "client_name": "Healthcare Benefits Provider",
        "client_description": (
            "A leading healthcare benefits provider needed a mobile strategy to extend "
            "services to brokers, employers, and end users, with seamless data integration "
            "across insurers, brokers, and enterprise systems."
        ),
        "challenge_heading": "Disconnected systems limiting mobile reach",
        "challenge_body": (
            "The client lacked a unified mobile presence to serve brokers, employers, "
            "and end users. Existing systems were siloed across insurers and enterprise "
            "platforms, making it impossible to deliver a consistent, real-time experience "
            "on mobile devices."
        ),
        "solution_heading": "Scalable mobile platform with deep enterprise integration",
        "solution_body": (
            "Technossus designed and delivered a scalable mobile platform that unified "
            "data flows across insurers, brokers, and enterprise systems. The solution "
            "provided tailored experiences for each user type — brokers, employers, and "
            "members — while maintaining a single source of truth."
        ),
        "solution_capabilities": [
            "Cross-platform mobile application for iOS and Android",
            "Real-time data integration with insurer and broker systems",
            "Role-based experiences for brokers, employers, and members",
            "Secure authentication and HIPAA-compliant data handling",
            "API layer connecting legacy enterprise systems to mobile",
            "Scalable architecture supporting rapid user growth",
        ],
        "impact_heading": "Greater reach. Higher value. Faster growth.",
        "impact_description": (
            "The mobile platform expanded the client's market reach, improved broker "
            "productivity, and directly contributed to increased company valuation."
        ),
        "impact_context_label": "MEASURABLE OUTCOMES",
        "impact_context_body": (
            "The platform enabled the client to serve a broader user base with a "
            "consistent mobile experience, strengthening relationships with brokers "
            "and employers while improving operational efficiency."
        ),
        "impact_cards": [
            {
                "title": "Expanded Market Reach",
                "body": (
                    "The mobile platform enabled the client to extend services to brokers, "
                    "employers, and end users who previously had no mobile access to benefits data."
                ),
            },
            {
                "title": "Seamless Data Integration",
                "body": (
                    "Real-time integration across insurers, brokers, and enterprise systems "
                    "eliminated manual data reconciliation and improved data accuracy."
                ),
            },
            {
                "title": "Increased Company Valuation",
                "body": (
                    "The mobile platform became a key differentiator, directly contributing "
                    "to increased company value and competitive positioning in the market."
                ),
            },
            {
                "title": "Improved Broker Productivity",
                "body": (
                    "Brokers gained instant mobile access to client data and plan information, "
                    "reducing response times and improving service quality."
                ),
            },
        ],
        "industry_stats": [
            {"value": "90%", "label": "Of healthcare consumers prefer mobile access to benefits"},
            {"value": "$4.5T", "label": "U.S. healthcare spending annually"},
            {"value": "60%", "label": "Of brokers report mobile tools improve client retention"},
            {"value": "3x", "label": "Faster benefits enrollment via mobile vs. desktop"},
        ],
        "related_case_studies": [
            {
                "tags": "HEALTHCARE • CRM INTEGRATION",
                "title": "CRM with Complex External Integrations Launches On Time",
                "excerpt": (
                    "A leading healthcare insurance provider needed a CRM integrating data "
                    "from state and federal platforms under evolving regulatory requirements "
                    "and a fixed go-live deadline."
                ),
                "image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
                "slug": "clinical-trial-platform",
            },
            {
                "tags": "LIFE SCIENCES • CLINICAL PLATFORM",
                "title": "Clinical Trial Platform Accelerates Drug Development Timelines",
                "excerpt": (
                    "A unified digital platform to manage trial data, patient recruitment, "
                    "and regulatory compliance from a single source of truth."
                ),
                "image": _img("/assets/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png"),
                "slug": "clinical-trial-platform",
            },
            {
                "tags": "HEALTHCARE • REVENUE CYCLE",
                "title": "Revenue Cycle Automation Reduces Denials and Improves Cash Flow",
                "excerpt": (
                    "Intelligent pre-submission validation catches errors before claims are "
                    "submitted, routes exceptions automatically, and gives finance teams "
                    "real-time visibility."
                ),
                "image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
                "slug": "clinical-trial-platform",
            },
        ],
    },
    {
        "slug": "clinical-trial-platform",
        "tags": "LIFE SCIENCES • CLINICAL PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "Clinical Trial Platform Accelerates Drug Development Timelines",
        "excerpt": (
            "A leading pharmaceutical company conducting multi-site clinical trials across "
            "30+ countries needed a unified digital platform to manage trial data, patient "
            "recruitment, and regulatory compliance from a single source of truth."
        ),
        "image_url": _img("/assets/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png"),
        "published_date": datetime(2025, 2, 10, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Clinical Trial Platform | Technossus",
        "meta_description": (
            "See how Technossus built a cloud-native clinical trial management platform "
            "that unified data ingestion, patient tracking, and regulatory workflows."
        ),
        "tag_line": "LIFE SCIENCES • CLINICAL PLATFORM",
        "hero_image": _img("/assets/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png"),
        "client_name": "Global Pharmaceutical Organization",
        "client_description": (
            "A leading pharmaceutical company conducting multi-site clinical trials across "
            "30+ countries needed a unified digital platform to manage trial data, patient "
            "recruitment, and regulatory compliance from a single source of truth."
        ),
        "challenge_heading": "Fragmented systems slowing critical research",
        "challenge_body": (
            "Trial data lived in six separate systems with no shared schema, forcing manual "
            "reconciliation that delayed reporting by weeks. Regulatory submissions required "
            "intensive manual effort, and patient recruitment was hampered by poor site "
            "visibility and slow data access."
        ),
        "solution_heading": "Unified clinical data platform with AI-assisted compliance",
        "solution_body": (
            "Technossus designed and delivered a cloud-native clinical trial management "
            "platform that unified data ingestion, patient tracking, and regulatory workflows. "
            "Built-in AI flagged protocol deviations in real time and automated generation "
            "of regulatory submission packages."
        ),
        "solution_capabilities": [
            "Unified data ingestion across 6 legacy source systems",
            "Real-time protocol deviation detection via ML models",
            "Automated regulatory submission package generation",
            "Multi-site patient recruitment and randomization module",
            "Role-based audit trail for 21 CFR Part 11 compliance",
            "HL7 FHIR-compliant data exchange with partner sites",
        ],
        "impact_heading": "Faster trials. Fewer errors. Lower cost.",
        "impact_description": (
            "The platform reduced administrative overhead, shortened submission timelines, "
            "and gave trial coordinators real-time visibility into patient and site performance."
        ),
        "impact_context_label": "MEASURABLE OUTCOMES",
        "impact_context_body": (
            "Across three active Phase III trials, the platform delivered consistent "
            "improvements in data quality, regulatory speed, and operational efficiency — "
            "all without adding headcount."
        ),
        "impact_cards": [
            {
                "title": "40% Reduction in Data Reconciliation Time",
                "body": (
                    "Automated ingestion and validation eliminated weeks of manual "
                    "cross-system reconciliation, freeing clinical data managers to "
                    "focus on higher-value analysis."
                ),
            },
            {
                "title": "60% Faster Regulatory Submissions",
                "body": (
                    "AI-assisted document assembly and audit trail automation cut "
                    "submission preparation from 6 weeks to under 2.5 weeks per package."
                ),
            },
            {
                "title": "Zero Protocol Deviation Escapes",
                "body": (
                    "Real-time ML monitoring flagged 100% of protocol deviations before "
                    "they progressed — preventing costly trial amendments and audit findings."
                ),
            },
            {
                "title": "30% Improvement in Patient Recruitment Rate",
                "body": (
                    "Site-level visibility and automated eligibility screening accelerated "
                    "enrollment, helping three trials meet recruitment targets ahead of schedule."
                ),
            },
        ],
        "industry_stats": [
            {"value": "$2.6B", "label": "Average cost to bring a new drug to market"},
            {"value": "10–15y", "label": "Typical drug development timeline"},
            {"value": "80%", "label": "Of clinical trials experience enrollment delays"},
            {"value": "50%", "label": "Of trial costs attributed to data management"},
        ],
        "related_case_studies": [
            {
                "tags": "LIFE SCIENCES • LAB PLATFORM",
                "title": "Unified Lab Platform Reduces Licensing Costs and Improves Throughput",
                "excerpt": (
                    "Helix replaced three fragmented lab systems with one higher-performing "
                    "LIMS, reducing licensing fees and enabling greater testing throughput "
                    "without adding staff."
                ),
                "image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
                "slug": "unified-lab-platform",
            },
            {
                "tags": "HEALTHCARE • STREAMING DATA",
                "title": "Streaming Analytics Enables Real-Time Visibility Across Patient Flow",
                "excerpt": (
                    "A streaming analytics platform now feeds clinical dashboards in real "
                    "time, enabling immediate action on delays, risks, and bottlenecks."
                ),
                "image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
                "slug": "streaming-analytics-patient-flow",
            },
            {
                "tags": "HEALTHCARE • REVENUE CYCLE",
                "title": "Revenue Cycle Automation Reduces Denials and Improves Cash Flow",
                "excerpt": (
                    "Intelligent pre-submission validation catches errors before claims are "
                    "submitted, routes exceptions automatically, and gives finance teams "
                    "real-time visibility."
                ),
                "image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
                "slug": "revenue-cycle-automation",
            },
        ],
    },
    # ─── List-only case studies (no detail page data) ──────────────────────────
    {
        "slug": "crm-complex-integrations",
        "tags": "HEALTHCARE • CRM INTEGRATION",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "CRM with Complex External Integrations Launches On Time",
        "excerpt": (
            "A leading healthcare insurance provider needed a CRM integrating data from "
            "state and federal platforms under evolving regulatory requirements and a fixed "
            "go-live deadline. Delivered on time with real-time access to customer data."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 1, 20, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "CRM Integration Case Study | Technossus",
        "meta_description": (
            "Healthcare CRM integrating state and federal platforms, delivered on time."
        ),
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "alm-digital-transformation",
        "tags": "HEALTHCARE • ALM & GOVERNANCE",
        "industry": "Healthcare",
        "service": "Quality Engineering",
        "title": "ALM Expertise Drives Successful Large-Scale Digital Transformation",
        "excerpt": (
            "A major U.S. healthcare provider needed to coordinate a complex multi-vendor "
            "digital platform transformation. Technossus established enterprise-wide ALM "
            "processes and governance frameworks, improving visibility and reducing risk."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 2, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "ALM Governance Transformation | Technossus",
        "meta_description": (
            "Enterprise-wide ALM processes and governance for healthcare digital transformation."
        ),
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "unified-lab-platform",
        "tags": "LIFE SCIENCES • LAB PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "Unified Lab Platform Reduces Licensing Costs and Improves Throughput",
        "excerpt": (
            "Helix replaced three fragmented lab systems with one higher-performing LIMS, "
            "reducing licensing fees, eliminating manual labor through standardized "
            "integrations, and enabling greater testing throughput without adding staff."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 2, 20, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Unified Lab Platform | Technossus",
        "meta_description": "Consolidated LIMS reducing licensing costs and improving throughput.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "streaming-analytics-patient-flow",
        "tags": "HEALTHCARE • STREAMING DATA",
        "industry": "Healthcare",
        "service": "Data Intelligence & Analytics",
        "title": "Streaming Analytics Enables Real-Time Visibility Across Patient Flow",
        "excerpt": (
            "A healthcare organization needed live visibility into patient data as it was "
            "generated. A streaming analytics platform now feeds clinical dashboards in "
            "real time, enabling immediate action on delays, risks, and bottlenecks."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 3, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Streaming Analytics for Patient Flow | Technossus",
        "meta_description": "Real-time streaming analytics for clinical dashboards.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "revenue-cycle-automation",
        "tags": "HEALTHCARE • REVENUE CYCLE",
        "industry": "Healthcare",
        "service": "AI Led Business Transformation",
        "title": "Revenue Cycle Automation Reduces Denials and Improves Cash Flow",
        "excerpt": (
            "Intelligent pre-submission validation catches errors before claims are submitted, "
            "routes exceptions automatically, and gives finance teams a real-time view from "
            "service to payment — improving collections and reducing revenue leakage."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 3, 15, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Revenue Cycle Automation | Technossus",
        "meta_description": "AI-driven revenue cycle automation reducing denials and leakage.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "unified-mortgage-platform",
        "tags": "FINTECH • MORTGAGE PLATFORM",
        "industry": "Financial Services",
        "service": "Product Engineering",
        "title": "Unified Mortgage Platform Enables Scalable Lending Operations",
        "excerpt": (
            "A leading financial services organization needed to unify multiple acquired "
            "mortgage systems into a single, seamless experience. Technossus built a unified "
            "platform connecting fragmented systems, improving data flow and simplifying workflows."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 4, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Unified Mortgage Platform | Technossus",
        "meta_description": "Unified mortgage platform connecting fragmented lending systems.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "automated-data-validation",
        "tags": "INVESTMENT BANKING • DATA",
        "industry": "Financial Services",
        "service": "Data Intelligence & Analytics",
        "title": "Automated Data Validation Improves Decision Confidence",
        "excerpt": (
            "A global investment bank depended on manual validation of financial dashboards, "
            "resulting in slow reporting cycles. An automated validation framework now "
            "continuously tests data across systems, automating 95% of validation scenarios."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 4, 15, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Data Validation Automation | Technossus",
        "meta_description": "Automated data validation framework for financial dashboards.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "insurance-quote-turnaround",
        "tags": "INSURANCE • DIGITAL EXPERIENCE",
        "industry": "Financial Services",
        "service": "Digital Experience Design",
        "title": "Insurance Brokerage Achieves 30% Faster Quote Turnaround",
        "excerpt": (
            "A leading insurance broker lacked a fast, intuitive way to generate quotes. "
            "A mobile-first QuoteLite portal with real-time quoting capabilities reduced "
            "turnaround time by ~30% and improved broker productivity."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 5, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Insurance Quote Optimization | Technossus",
        "meta_description": "Mobile-first quoting portal achieving 30% faster turnaround.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "connected-product-experience",
        "tags": "HEALTHTECH • PRODUCT REDESIGN",
        "industry": "HiTech / SaaS",
        "service": "Digital Experience Design",
        "title": "Connected Product Experience Improves Adoption — App Rating 1.4 to 3.4",
        "excerpt": (
            "A migraine treatment companion app was redesigned around real user conditions. "
            "Onboarding steps reduced from 13 to 7. Bluetooth reliability re-engineered. "
            "App rating improved from 1.4 to 3.4."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 5, 10, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Connected Product Redesign | Technossus",
        "meta_description": "App redesign improving rating from 1.4 to 3.4.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "real-time-visual-intelligence",
        "tags": "SECURITY • COMPUTER VISION",
        "industry": "HiTech / SaaS",
        "service": "AI Led Business Transformation",
        "title": "Real-Time Visual Intelligence Enables 10ms Plate Recognition",
        "excerpt": (
            "An edge-to-alert computer vision pipeline ingested live video from cameras, "
            "drones, and moving patrol cars — detecting vehicles, extracting license plate "
            "data via OCR, and matching against watchlist databases in near real time."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 5, 20, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Computer Vision Intelligence | Technossus",
        "meta_description": "Edge-to-alert computer vision with 10ms plate recognition.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "workflow-automation-backlog",
        "tags": "GOVTECH • WORKFLOW AUTOMATION",
        "industry": "HiTech / SaaS",
        "service": "AI Led Business Transformation",
        "title": "Workflow Automation Clears 100% of Operational Backlog in 24 Hours",
        "excerpt": (
            "A high-volume traffic offence reporting workflow was automated from email "
            "intake to PDF review, validation, API lookups, and system submission — "
            "clearing the entire historical backlog in a single 24-hour cycle with "
            "1000% efficiency improvement."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 6, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Workflow Automation | Technossus",
        "meta_description": "Automated workflow clearing 100% backlog in 24 hours.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
]


# ─── Insights seed data ────────────────────────────────────────────────────────
# Derived from Insights.tsx caseStudies array — these are the listing items.

INSIGHTS_SEED: list[dict] = [
    {
        "slug": "healthcare-mobile-platform",
        "tags": "HEALTHCARE • MOBILE PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "Mobile Platform Increases Company Value for Healthcare Benefits Provider",
        "excerpt": (
            "A leading healthcare benefits provider needed a mobile strategy to extend "
            "services to brokers, employers, and end users. Technossus delivered a scalable "
            "platform with seamless data integration across insurers, brokers, and enterprise systems."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 1, 15, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Mobile Platform for Healthcare | Technossus",
        "meta_description": (
            "Mobile strategy extending services to brokers, employers, and end users."
        ),
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "crm-complex-integrations",
        "tags": "HEALTHCARE • CRM INTEGRATION",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "CRM with Complex External Integrations Launches On Time",
        "excerpt": (
            "A leading healthcare insurance provider needed a CRM integrating data from "
            "state and federal platforms under evolving regulatory requirements and a fixed "
            "go-live deadline. Delivered on time with real-time access to customer data."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 1, 20, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "CRM Integration Case Study | Technossus",
        "meta_description": (
            "Healthcare CRM integrating state and federal platforms, delivered on time."
        ),
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "alm-digital-transformation",
        "tags": "HEALTHCARE • ALM & GOVERNANCE",
        "industry": "Healthcare",
        "service": "Quality Engineering",
        "title": "ALM Expertise Drives Successful Large-Scale Digital Transformation",
        "excerpt": (
            "A major U.S. healthcare provider needed to coordinate a complex multi-vendor "
            "digital platform transformation. Technossus established enterprise-wide ALM "
            "processes and governance frameworks, improving visibility and reducing risk."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 2, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "ALM Governance Transformation | Technossus",
        "meta_description": (
            "Enterprise-wide ALM processes and governance for healthcare digital transformation."
        ),
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "clinical-trial-platform",
        "tags": "LIFE SCIENCES • CLINICAL PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "Clinical Trial Platform Accelerates Drug Development Timelines",
        "excerpt": (
            "A leading pharmaceutical company conducting multi-site clinical trials across "
            "30+ countries needed a unified digital platform to manage trial data, patient "
            "recruitment, and regulatory compliance from a single source of truth."
        ),
        "image_url": _img("/assets/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png"),
        "published_date": datetime(2025, 2, 10, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Clinical Trial Platform | Technossus",
        "meta_description": (
            "Unified clinical trial management platform for multi-site global trials."
        ),
        "hero_image": _img("/assets/d16e5b610d1fff4d128bb7e9580d630eb3fa03e8.png"),
    },
    {
        "slug": "unified-lab-platform",
        "tags": "LIFE SCIENCES • LAB PLATFORM",
        "industry": "Healthcare",
        "service": "Product Engineering",
        "title": "Unified Lab Platform Reduces Licensing Costs and Improves Throughput",
        "excerpt": (
            "Helix replaced three fragmented lab systems with one higher-performing LIMS, "
            "reducing licensing fees, eliminating manual labor through standardized "
            "integrations, and enabling greater testing throughput without adding staff."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 2, 20, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Unified Lab Platform | Technossus",
        "meta_description": "Consolidated LIMS reducing licensing costs and improving throughput.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "streaming-analytics-patient-flow",
        "tags": "HEALTHCARE • STREAMING DATA",
        "industry": "Healthcare",
        "service": "Data Intelligence & Analytics",
        "title": "Streaming Analytics Enables Real-Time Visibility Across Patient Flow",
        "excerpt": (
            "A healthcare organization needed live visibility into patient data as it was "
            "generated. A streaming analytics platform now feeds clinical dashboards in "
            "real time, enabling immediate action on delays, risks, and bottlenecks."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 3, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Streaming Analytics for Patient Flow | Technossus",
        "meta_description": "Real-time streaming analytics for clinical dashboards.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "revenue-cycle-automation",
        "tags": "HEALTHCARE • REVENUE CYCLE",
        "industry": "Healthcare",
        "service": "AI Led Business Transformation",
        "title": "Revenue Cycle Automation Reduces Denials and Improves Cash Flow",
        "excerpt": (
            "Intelligent pre-submission validation catches errors before claims are submitted, "
            "routes exceptions automatically, and gives finance teams a real-time view from "
            "service to payment — improving collections and reducing revenue leakage."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 3, 15, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Revenue Cycle Automation | Technossus",
        "meta_description": "AI-driven revenue cycle automation reducing denials and leakage.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "unified-mortgage-platform",
        "tags": "FINTECH • MORTGAGE PLATFORM",
        "industry": "Financial Services",
        "service": "Product Engineering",
        "title": "Unified Mortgage Platform Enables Scalable Lending Operations",
        "excerpt": (
            "A leading financial services organization needed to unify multiple acquired "
            "mortgage systems into a single, seamless experience. Technossus built a unified "
            "platform connecting fragmented systems, improving data flow and simplifying workflows."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 4, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Unified Mortgage Platform | Technossus",
        "meta_description": "Unified mortgage platform connecting fragmented lending systems.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "automated-data-validation",
        "tags": "INVESTMENT BANKING • DATA",
        "industry": "Financial Services",
        "service": "Data Intelligence & Analytics",
        "title": "Automated Data Validation Improves Decision Confidence",
        "excerpt": (
            "A global investment bank depended on manual validation of financial dashboards, "
            "resulting in slow reporting cycles. An automated validation framework now "
            "continuously tests data across systems, automating 95% of validation scenarios."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 4, 15, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Data Validation Automation | Technossus",
        "meta_description": "Automated data validation framework for financial dashboards.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "insurance-quote-turnaround",
        "tags": "INSURANCE • DIGITAL EXPERIENCE",
        "industry": "Financial Services",
        "service": "Digital Experience Design",
        "title": "Insurance Brokerage Achieves 30% Faster Quote Turnaround",
        "excerpt": (
            "A leading insurance broker lacked a fast, intuitive way to generate quotes. "
            "A mobile-first QuoteLite portal with real-time quoting capabilities reduced "
            "turnaround time by ~30% and improved broker productivity."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 5, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Insurance Quote Optimization | Technossus",
        "meta_description": "Mobile-first quoting portal achieving 30% faster turnaround.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "connected-product-experience",
        "tags": "HEALTHTECH • PRODUCT REDESIGN",
        "industry": "HiTech / SaaS",
        "service": "Digital Experience Design",
        "title": "Connected Product Experience Improves Adoption — App Rating 1.4 to 3.4",
        "excerpt": (
            "A migraine treatment companion app was redesigned around real user conditions. "
            "Onboarding steps reduced from 13 to 7. Bluetooth reliability re-engineered. "
            "App rating improved from 1.4 to 3.4."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 5, 10, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Connected Product Redesign | Technossus",
        "meta_description": "App redesign improving rating from 1.4 to 3.4.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "real-time-visual-intelligence",
        "tags": "SECURITY • COMPUTER VISION",
        "industry": "HiTech / SaaS",
        "service": "AI Led Business Transformation",
        "title": "Real-Time Visual Intelligence Enables 10ms Plate Recognition",
        "excerpt": (
            "An edge-to-alert computer vision pipeline ingested live video from cameras, "
            "drones, and moving patrol cars — detecting vehicles, extracting license plate "
            "data via OCR, and matching against watchlist databases in near real time."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 5, 20, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Computer Vision Intelligence | Technossus",
        "meta_description": "Edge-to-alert computer vision with 10ms plate recognition.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
    {
        "slug": "workflow-automation-backlog",
        "tags": "GOVTECH • WORKFLOW AUTOMATION",
        "industry": "HiTech / SaaS",
        "service": "AI Led Business Transformation",
        "title": "Workflow Automation Clears 100% of Operational Backlog in 24 Hours",
        "excerpt": (
            "A high-volume traffic offence reporting workflow was automated from email "
            "intake to PDF review, validation, API lookups, and system submission — "
            "clearing the entire historical backlog in a single 24-hour cycle with "
            "1000% efficiency improvement."
        ),
        "image_url": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
        "published_date": datetime(2025, 6, 1, tzinfo=timezone.utc),
        "is_published": True,
        "content": None,
        "meta_title": "Workflow Automation | Technossus",
        "meta_description": "Automated workflow clearing 100% backlog in 24 hours.",
        "hero_image": _img("/assets/fbbad1d37f7a4e076de4d16631dc6863c6c4444a.png"),
    },
]


def seed_case_studies(service: ContentDBService) -> dict:
    """Seed case studies. Idempotent — uses upsert on slug."""

    seeded = 0
    for item in CASE_STUDIES_SEED:
        service.upsert_case_study(item.copy())
        seeded += 1
    return {"seeded": seeded, "total_records": len(CASE_STUDIES_SEED)}


def seed_insights(service: ContentDBService) -> dict:
    """Seed insights. Idempotent — uses upsert on slug."""

    seeded = 0
    for item in INSIGHTS_SEED:
        service.upsert_insight(item.copy())
        seeded += 1
    return {"seeded": seeded, "total_records": len(INSIGHTS_SEED)}
