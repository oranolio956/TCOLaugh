"""
Test a single platform with both existing and non-existing usernames.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from panopticon.analysis.recon.platform_database import PlatformDefinition
from panopticon.analysis.recon.test_platform import test_platform

import json


async def main():
    # Load Sherlock data
    with open("/tmp/sherlock/sherlock_project/resources/data.json", 'r') as f:
        data = json.load(f)
    
    # Test GitHub (should be reliable)
    platform_name = "GitHub"
    if platform_name not in data:
        print(f"Platform {platform_name} not found")
        return
    
    platform = PlatformDefinition(platform_name, data[platform_name])
    
    print(f"Testing platform: {platform_name}")
    print(f"URL template: {platform.url_template}")
    print(f"Error type: {platform.error_type}")
    print(f"Error codes: {platform.error_code}")
    print()
    
    # Test with claimed username (should exist)
    print("="*60)
    print(f"Test 1: Claimed username '{platform.username_claimed}' (should exist)")
    print("="*60)
    result1 = await test_platform(platform, platform.username_claimed)
    print(json.dumps(result1, indent=2))
    print()
    
    # Test with random username (should not exist)
    print("="*60)
    print(f"Test 2: Random username 'definitelydoesnotexist12345xyz' (should not exist)")
    print("="*60)
    result2 = await test_platform(platform, "definitelydoesnotexist12345xyz")
    print(json.dumps(result2, indent=2))
    print()
    
    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    if result1["status"] == "SUCCESS" and result2["status"] == "SUCCESS":
        found1 = result1["detection"]["found"]
        found2 = result2["detection"]["found"]
        
        if found1 and not found2:
            print("✓ Platform detection is working correctly!")
            print(f"  - Existing username detected: {found1}")
            print(f"  - Non-existing username detected: {not found2}")
        else:
            print("⚠ Platform detection may have issues:")
            print(f"  - Existing username detected: {found1}")
            print(f"  - Non-existing username detected: {not found2}")
    else:
        print("✗ Platform test failed:")
        print(f"  - Test 1 status: {result1['status']}")
        print(f"  - Test 2 status: {result2['status']}")


if __name__ == "__main__":
    asyncio.run(main())
