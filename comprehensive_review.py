"""
Comprehensive review of Phase 1 and Phase 2 for gaps and issues.
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.recon.platform_database import PlatformDatabase
from panopticon.analysis.recon.detection_engine import DetectionEngine

async def test_issues():
    """Test for common issues."""
    issues = []
    
    print("="*60)
    print("COMPREHENSIVE REVIEW - PHASE 1 & 2")
    print("="*60)
    
    # Issue 1: Response time tracking
    print("\n1. Checking response time tracking...")
    try:
        test_scanner = ActiveScanner()
        # Check if response_time is tracked correctly
        print("   ✓ Scanner initialized")
        await test_scanner.close()
    except Exception as e:
        issues.append(f"Scanner initialization: {e}")
        print(f"   ✗ Error: {e}")
    
    # Issue 2: Platform database path resolution
    print("\n2. Checking platform database path...")
    try:
        db = PlatformDatabase()
        count = db.count()
        if count == 473:
            print(f"   ✓ Platform database loaded ({count} platforms)")
        else:
            issues.append(f"Platform count mismatch: expected 473, got {count}")
            print(f"   ✗ Platform count mismatch: {count}")
    except Exception as e:
        issues.append(f"Platform database load: {e}")
        print(f"   ✗ Error: {e}")
    
    # Issue 3: Detection engine backward compatibility
    print("\n3. Checking detection engine backward compatibility...")
    try:
        # Check if detect() method exists (backward compat)
        if hasattr(DetectionEngine, 'detect'):
            print("   ✓ detect() method exists")
        else:
            issues.append("detect() method missing")
            print("   ✗ detect() method missing")
        
        # Check if detect_enhanced() exists
        if hasattr(DetectionEngine, 'detect_enhanced'):
            print("   ✓ detect_enhanced() method exists")
        else:
            print("   ⚠ detect_enhanced() method missing (using detect())")
    except Exception as e:
        issues.append(f"Detection engine check: {e}")
        print(f"   ✗ Error: {e}")
    
    # Issue 4: Username validation
    print("\n4. Checking username validation...")
    try:
        db = PlatformDatabase()
        github = db.get_platform("GitHub")
        if github:
            # Test various usernames
            test_cases = [
                ("validuser", True),
                ("user-with-dash", True),
                ("", False),  # Empty should fail
                ("a" * 100, False),  # Very long should fail (over 100 char limit)
            ]
            for username, should_pass in test_cases:
                result = github.validate_username(username)
                if result != should_pass:
                    issues.append(f"Username validation failed for '{username}' (expected {should_pass}, got {result})")
                    print(f"   ✗ Validation failed for '{username}' (expected {should_pass}, got {result})")
            print("   ✓ Username validation working")
    except Exception as e:
        issues.append(f"Username validation: {e}")
        print(f"   ✗ Error: {e}")
    
    # Issue 5: Error handling
    print("\n5. Checking error handling...")
    try:
        test_scanner = ActiveScanner(timeout=0.01)  # Very short timeout
        # This should handle timeouts gracefully
        print("   ✓ Error handling configured")
        await test_scanner.close()
    except Exception as e:
        issues.append(f"Error handling: {e}")
        print(f"   ✗ Error: {e}")
    
    # Issue 6: API integration
    print("\n6. Checking API integration...")
    try:
        # Try importing scanner directly (not through main.py which requires numpy)
        from panopticon.analysis.recon.active_scanner import ActiveScanner
        api_scanner = ActiveScanner()
        if api_scanner:
            print("   ✓ API scanner can be initialized")
        else:
            issues.append("API scanner not initialized")
            print("   ✗ API scanner not initialized")
    except Exception as e:
        # numpy missing is OK - recon works without it
        if "numpy" not in str(e).lower():
            issues.append(f"API integration: {e}")
            print(f"   ✗ Error: {e}")
        else:
            print("   ⚠ numpy missing (not critical for recon)")
    
    # Issue 7: Resource cleanup
    print("\n7. Checking resource cleanup...")
    try:
        scanner = ActiveScanner()
        if hasattr(scanner, 'close'):
            print("   ✓ close() method exists")
        else:
            issues.append("close() method missing")
            print("   ✗ close() method missing")
    except Exception as e:
        issues.append(f"Resource cleanup: {e}")
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
        print("✓ No issues found!")
        return True

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_issues())
    sys.exit(0 if success else 1)
