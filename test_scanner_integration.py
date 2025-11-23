"""
Test the refactored ActiveScanner with real username.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner


async def test_scanner():
    scanner = ActiveScanner()
    
    print(f"Loaded {scanner.platform_db.count() if scanner.platform_db else 0} platforms")
    print()
    
    # Test with a known username (GitHub's "blue" user)
    username = "blue"
    print(f"Testing username: {username}")
    print("="*60)
    
    # Test with just a few platforms first
    test_platforms = ["GitHub", "Twitter", "Reddit", "Instagram"]
    print(f"Testing {len(test_platforms)} platforms: {', '.join(test_platforms)}")
    
    results = await scanner.check_username(username, platform_filter=test_platforms)
    
    print(f"\nFound on {len(results)} platform(s):")
    for result in results:
        print(f"  ✓ {result['site']}: {result['url']} (confidence: {result.get('confidence', 0):.2f})")
    
    print("\n" + "="*60)
    print("Full results:")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    asyncio.run(test_scanner())
