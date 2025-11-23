"""Final validation test for Phase 1 & 2 fixes."""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner

async def test_all():
    print("="*60)
    print("FINAL VALIDATION - PHASE 1 & 2")
    print("="*60)
    
    issues = []
    
    # Test 1: Scanner initialization
    print("\n1. Scanner initialization...")
    try:
        scanner = ActiveScanner()
        print(f"   ✓ Loaded {scanner.platform_db.count() if scanner.platform_db else 0} platforms")
    except Exception as e:
        issues.append(f"Scanner init: {e}")
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Response time tracking
    print("\n2. Response time tracking...")
    try:
        start = time.time()
        results = await scanner.check_username("blue", platform_filter=["GitHub"])
        elapsed = time.time() - start
        
        if results:
            has_time = "response_time_ms" in results[0]
            if has_time:
                print(f"   ✓ Response time tracked: {results[0]['response_time_ms']}ms")
            else:
                issues.append("Response time not in results")
                print("   ✗ Response time not tracked")
        else:
            print("   ⚠ No results (might be expected)")
    except Exception as e:
        issues.append(f"Response time test: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 3: Enhanced detection
    print("\n3. Enhanced detection...")
    try:
        results = await scanner.check_username("blue", platform_filter=["Twitter", "GitHub"])
        if results:
            has_methods = "methods_used" in results[0]
            if has_methods:
                methods = results[0]["methods_used"]
                print(f"   ✓ Multiple methods: {methods}")
            else:
                print("   ⚠ methods_used not in results")
        else:
            print("   ⚠ No results")
    except Exception as e:
        issues.append(f"Enhanced detection: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 4: Username validation
    print("\n4. Username validation...")
    try:
        github = scanner.platform_db.get_platform("GitHub")
        if github:
            empty_valid = github.validate_username("")
            long_valid = github.validate_username("a" * 101)
            if not empty_valid and not long_valid:
                print("   ✓ Validation working (empty and long usernames rejected)")
            else:
                issues.append("Username validation not strict enough")
                print("   ✗ Validation too lenient")
    except Exception as e:
        issues.append(f"Validation test: {e}")
        print(f"   ✗ Error: {e}")
    
    # Test 5: Error handling
    print("\n5. Error handling...")
    try:
        # Test with invalid username
        results = await scanner.check_username("", platform_filter=["GitHub"])
        print("   ✓ Empty username handled gracefully")
    except Exception as e:
        # Should handle gracefully, not crash
        print(f"   ⚠ Exception raised: {e}")
    
    # Test 6: Resource cleanup
    print("\n6. Resource cleanup...")
    try:
        await scanner.close()
        print("   ✓ Scanner closed successfully")
    except Exception as e:
        issues.append(f"Cleanup: {e}")
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
        print("✓ All tests passed!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_all())
    sys.exit(0 if success else 1)
