"""
Final comprehensive check - test everything that could break.
"""
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner

async def test_edge_cases():
    """Test edge cases that could break."""
    print("="*60)
    print("FINAL COMPREHENSIVE CHECK - EDGE CASES")
    print("="*60)
    
    issues = []
    
    # Test 1: Empty username
    print("\n1. Empty username...")
    try:
        scanner = ActiveScanner()
        results = await scanner.check_username("", platform_filter=["GitHub"])
        print(f"   ✓ Handled gracefully: {len(results)} results")
        await scanner.close()
    except Exception as e:
        issues.append(f"Empty username: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 2: Very long username
    print("\n2. Very long username...")
    try:
        scanner = ActiveScanner()
        long_username = "a" * 200
        results = await scanner.check_username(long_username, platform_filter=["GitHub"])
        print(f"   ✓ Handled: {len(results)} results")
        await scanner.close()
    except Exception as e:
        issues.append(f"Long username: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 3: Special characters
    print("\n3. Special characters...")
    try:
        scanner = ActiveScanner()
        special_chars = "test-user_name.test@123"
        results = await scanner.check_username(special_chars, platform_filter=["GitHub"])
        print(f"   ✓ Handled: {len(results)} results")
        await scanner.close()
    except Exception as e:
        issues.append(f"Special chars: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 4: Non-existent platform
    print("\n4. Non-existent platform filter...")
    try:
        scanner = ActiveScanner()
        results = await scanner.check_username("test", platform_filter=["NonExistentPlatform123"])
        print(f"   ✓ Handled: {len(results)} results (should be 0)")
        await scanner.close()
    except Exception as e:
        issues.append(f"Non-existent platform: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 5: Concurrent requests
    print("\n5. Concurrent requests...")
    try:
        scanner = ActiveScanner()
        tasks = [
            scanner.check_username("blue", platform_filter=["GitHub"]),
            scanner.check_username("test", platform_filter=["GitHub"]),
            scanner.check_username("user", platform_filter=["GitHub"]),
        ]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        exceptions = [r for r in all_results if isinstance(r, Exception)]
        if exceptions:
            issues.append(f"Concurrent requests failed: {len(exceptions)} exceptions")
            print(f"   ✗ {len(exceptions)} exceptions")
        else:
            print(f"   ✓ All concurrent requests succeeded")
        await scanner.close()
    except Exception as e:
        issues.append(f"Concurrent requests: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 6: Rate limiting with multiple platforms
    print("\n6. Rate limiting with multiple platforms...")
    try:
        scanner = ActiveScanner(enable_rate_limiting=True)
        start = time.time()
        results = await scanner.check_username("blue", platform_filter=["GitHub", "Twitter", "Reddit"])
        elapsed = time.time() - start
        print(f"   ✓ Completed in {elapsed:.2f}s: {len(results)} results")
        await scanner.close()
    except Exception as e:
        issues.append(f"Rate limiting: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 7: Early termination
    print("\n7. Early termination...")
    try:
        scanner = ActiveScanner(early_termination=2)
        start = time.time()
        results = await scanner.check_username("blue", platform_filter=["GitHub", "Twitter", "Reddit", "Instagram"])
        elapsed = time.time() - start
        if len(results) <= 2:
            print(f"   ✓ Early termination working: {len(results)} results in {elapsed:.2f}s")
        else:
            issues.append("Early termination not working")
            print(f"   ✗ Early termination failed: {len(results)} results")
        await scanner.close()
    except Exception as e:
        issues.append(f"Early termination: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 8: Result format consistency
    print("\n8. Result format consistency...")
    try:
        scanner = ActiveScanner()
        results = await scanner.check_username("blue", platform_filter=["GitHub", "Twitter"])
        
        required_fields = ["site", "url", "status"]
        for result in results:
            missing = [f for f in required_fields if f not in result]
            if missing:
                issues.append(f"Missing fields in result: {missing}")
                print(f"   ✗ Missing fields: {missing}")
                break
        else:
            print(f"   ✓ All results have required fields")
        await scanner.close()
    except Exception as e:
        issues.append(f"Result format: {e}")
        print(f"   ✗ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    if issues:
        print(f"Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False
    else:
        print("✓ All edge cases handled correctly!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_edge_cases())
    sys.exit(0 if success else 1)
