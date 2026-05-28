"""Seed the new case studies table."""

from src.services.content_db import get_content_db_service
from src.services.seed_data import seed_case_studies

def main():
    print("Seeding case studies...")
    svc = get_content_db_service()
    result = seed_case_studies(svc)
    print(f"Seeded {result['seeded']} out of {result['total']} case studies")
    
    print("\nVerifying data...")
    rows = svc.list_case_studies(published_only=False, limit=10, offset=0)
    print(f"Found {len(rows)} case studies in database")
    for row in rows:
        print(f"  - Page: {row.get('page')}")
        print(f"    Slug: {row.get('slug')}")
        print(f"    Tags: {row.get('tags')}")
        print(f"    Industry: {row.get('industry')}")
        print(f"    Service: {row.get('service')}")
        print()

if __name__ == "__main__":
    main()
