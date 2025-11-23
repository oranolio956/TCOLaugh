"""Test Phase 2 enhanced detection methods."""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner

async def test_enhanced_detection():
    print("="*60)
    print("PHASE 2: ENHANCED DETECTION TEST")
    print("="*60)
    
    scanner = ActiveScanner(timeout=3.0, max_concurrent=50)
    
    # Test with known username
    username = "blue"
    test_platforms = ["GitHub", "Twitter", "Reddit", "Instagram", "About.me"]
    
    print(f"\nTesting username: {username}")
    print(f"Platforms: {', '.join(test_platforms)}")
    print("\n" + "-"*60)
    
    start = time.time()
    results = await scanner.check_username(username, platform_filter=test_platforms)
    elapsed = time.time() - start
    
    print(f"\nResults ({len(results)} found in {elapsed:.2f}s):")
    print("-"*60)
    
    for result in results:
        methods = result.get("methods_used", [result.get("method", "unknown")])
        methods_str = "+".join(methods) if isinstance(methods, list) else methods
        response_time = result.get("response_time_ms", "N/A")
        
        print(f"✓ {result['site']}")
        print(f"  URL: {result['url']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Methods: {methods_str}")
        print(f"  Response Time: {response_time}ms")
        print()
    
    # Check if enhanced detection is working
    enhanced_features = any("methods_used" in r for r in results)
    if enhanced_features:
        print("✅ Enhanced detection features active!")
        print("  - Multiple detection methods")
        print("  - Response time tracking")
        print("  - Profile element detection")
    else:
        print("⚠ Using standard detection (enhanced features not active)")
    
    await scanner.close()

if __name__ == "__main__":
    asyncio.run(test_enhanced_detection())
