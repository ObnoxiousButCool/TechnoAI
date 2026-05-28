"""Quick test to check database connection and queries."""

from src.services.content_db import get_content_db_service

def test_query():
    svc = get_content_db_service()
    
    print("Testing list_case_studies_new...")
    try:
        rows = svc.list_case_studies_new(published_only=False, limit=10, offset=0)
        print(f"Success! Found {len(rows)} rows")
        for row in rows:
            print(f"  - {row.get('page', 'N/A')}: {row.get('slug', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()
