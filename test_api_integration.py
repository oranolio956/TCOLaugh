"""
Test API endpoint integration.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner

async def test_api_format():
    """Test that results match API format."""
    scanner = ActiveScanner()
    
    # Test username
    username = "blue"
    
    print(f"Testing username: {username}")
    print("="*60)
    
    # Get results
    results = await scanner.check_username(username, platform_filter=["GitHub", "Twitter", "Reddit"])
    
    print(f"\nFound on {len(results)} platform(s):")
    for result in results:
        print(f"  ✓ {result['site']}: {result['url']}")
        print(f"    Confidence: {result.get('confidence', 0):.2f}")
        print(f"    Method: {result.get('method', 'unknown')}")
    
    # Verify API format
    print("\n" + "="*60)
    print("API Format Check:")
    print("="*60)
    
    required_fields = ["site", "url", "status"]
    optional_fields = ["confidence", "method", "details", "status_code"]
    
    all_valid = True
    for result in results:
        for field in required_fields:
            if field not in result:
                print(f"✗ Missing required field: {field}")
                all_valid = False
    
    if all_valid:
        print("✓ All results have required fields")
    
    # Test API response format
    api_response = {
        "username": username,
        "found_on": results
    }
    
    print(f"\nAPI Response (first 3 results):")
    print(json.dumps(api_response, indent=2)[:500])
    
    return all_valid

if __name__ == "__main__":
    success = asyncio.run(test_api_format())
    sys.exit(0 if success else 1)
