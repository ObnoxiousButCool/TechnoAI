"""Test the API endpoint directly."""

import sys
import traceback

# Test importing the module
try:
    from src.api.case_studies_new import list_case_studies
    print("✓ Successfully imported list_case_studies")
except Exception as e:
    print(f"✗ Error importing: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test calling the function
try:
    print("\nTesting list_case_studies()...")
    result = list_case_studies()
    print(f"✓ Success! Returned {len(result)} items")
    if result:
        print(f"\nFirst item keys: {list(result[0].keys())}")
        print(f"\nFirst item: {result[0]}")
except Exception as e:
    print(f"✗ Error calling function: {e}")
    traceback.print_exc()
