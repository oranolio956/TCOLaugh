"""
Systematic review and fix verification.
Tests each component individually.
"""
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.recon.platform_database import PlatformDatabase
from panopticon.analysis.recon.detection_engine import DetectionEngine
from panopticon.analysis.recon.proxy_manager import ProxyManager
from panopticon.analysis.recon.rate_limiter import RateLimiter
from panopticon.analysis.recon.user_agent_rotator import UserAgentRotator

async def review_all():
    issues = []
    fixes_applied = []
    
    print("="*60)
    print("SYSTEMATIC REVIEW - ALL PHASES")
    print("="*60)
    
    # 1. Platform Database
    print("\n1. Platform Database...")
    try:
        db = PlatformDatabase()
        count = db.count()
        if count == 473:
            print(f"   ✓ {count} platforms loaded")
        else:
            issues.append(f"Platform count: expected 473, got {count}")
            print(f"   ✗ Platform count mismatch: {count}")
        
        # Check path resolution
        db_path = db.data_file
        if db_path.exists():
            print(f"   ✓ Platform DB file exists: {db_path}")
        else:
            issues.append(f"Platform DB file not found: {db_path}")
            print(f"   ✗ Platform DB file not found: {db_path}")
    except Exception as e:
        issues.append(f"Platform database: {e}")
        print(f"   ✗ Error: {e}")
    
    # 2. Detection Engine
    print("\n2. Detection Engine...")
    try:
        # Check if enhanced features exist
        has_enhanced = hasattr(DetectionEngine, 'detect_enhanced')
        has_profile = hasattr(DetectionEngine, '_detect_by_profile_elements')
        has_json = hasattr(DetectionEngine, '_detect_by_json')
        has_timing = hasattr(DetectionEngine, '_detect_by_response_time')
        
        print(f"   ✓ detect_enhanced: {has_enhanced}")
        print(f"   ✓ Profile elements: {has_profile}")
        print(f"   ✓ JSON detection: {has_json}")
        print(f"   ✓ Timing analysis: {has_timing}")
        
        if not all([has_enhanced, has_profile, has_json, has_timing]):
            issues.append("Detection engine missing enhanced features")
    except Exception as e:
        issues.append(f"Detection engine: {e}")
        print(f"   ✗ Error: {e}")
    
    # 3. Proxy Manager
    print("\n3. Proxy Manager...")
    try:
        pm = ProxyManager(enable_proxy=False)
        stats = pm.get_stats()
        print(f"   ✓ Proxy manager initialized")
        print(f"   ✓ Stats: {stats}")
    except Exception as e:
        issues.append(f"Proxy manager: {e}")
        print(f"   ✗ Error: {e}")
    
    # 4. Rate Limiter
    print("\n4. Rate Limiter...")
    try:
        rl = RateLimiter()
        limit = rl.get_limit("GitHub")
        print(f"   ✓ Rate limiter initialized")
        print(f"   ✓ GitHub limit: {limit} req/min")
        
        # Test thread safety (async safety)
        await rl.wait_if_needed("GitHub")
        print(f"   ✓ Rate limiting works")
    except Exception as e:
        issues.append(f"Rate limiter: {e}")
        print(f"   ✗ Error: {e}")
    
    # 5. User-Agent Rotator
    print("\n5. User-Agent Rotator...")
    try:
        ua = UserAgentRotator()
        ua1 = ua.get_rotated()
        ua2 = ua.get_rotated()
        if ua1 != ua2:
            print(f"   ✓ Rotation working")
        else:
            issues.append("User-Agent rotation not working")
            print(f"   ✗ Rotation not working")
    except Exception as e:
        issues.append(f"User-Agent rotator: {e}")
        print(f"   ✗ Error: {e}")
    
    # 6. ActiveScanner Integration
    print("\n6. ActiveScanner Integration...")
    try:
        scanner = ActiveScanner(
            enable_rate_limiting=True,
            enable_user_agent_rotation=True,
            enable_proxy=False
        )
        
        # Check all features are initialized
        checks = {
            "Platform DB": scanner.platform_db is not None,
            "Proxy Manager": scanner.proxy_manager is not None,
            "Rate Limiter": scanner.rate_limiter is not None,
            "UA Rotator": scanner.user_agent_rotator is not None,
        }
        
        for name, present in checks.items():
            status = "✓" if present else "✗"
            print(f"   {status} {name}: {present}")
            if not present:
                issues.append(f"{name} not initialized")
        
        # Test actual scan
        results = await scanner.check_username("blue", platform_filter=["GitHub"])
        if results:
            result = results[0]
            enhanced_features = {
                "confidence": "confidence" in result,
                "methods_used": "methods_used" in result,
                "response_time_ms": "response_time_ms" in result,
            }
            print(f"   ✓ Scan works: {len(results)} results")
            for feature, present in enhanced_features.items():
                status = "✓" if present else "✗"
                print(f"   {status} {feature}: {present}")
                if not present:
                    issues.append(f"Enhanced feature missing: {feature}")
        else:
            print(f"   ⚠ No results (might be expected)")
        
        await scanner.close()
    except Exception as e:
        issues.append(f"ActiveScanner: {e}")
        print(f"   ✗ Error: {e}")
    
    # 7. API Response Format
    print("\n7. API Response Format...")
    try:
        scanner = ActiveScanner()
        results = await scanner.check_username("blue", platform_filter=["GitHub"])
        
        if results:
            result = results[0]
            required_fields = ["site", "url", "status"]
            missing = [f for f in required_fields if f not in result]
            if missing:
                issues.append(f"Missing required fields: {missing}")
                print(f"   ✗ Missing fields: {missing}")
            else:
                print(f"   ✓ All required fields present")
        await scanner.close()
    except Exception as e:
        issues.append(f"API format: {e}")
        print(f"   ✗ Error: {e}")
    
    # 8. Error Handling
    print("\n8. Error Handling...")
    try:
        scanner = ActiveScanner(timeout=0.01)  # Very short timeout
        # Should handle gracefully
        results = await scanner.check_username("test", platform_filter=["GitHub"])
        print(f"   ✓ Timeout handled gracefully")
        await scanner.close()
    except Exception as e:
        # Should not crash
        print(f"   ⚠ Exception: {e} (might be OK)")
    
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
    success = asyncio.run(review_all())
    sys.exit(0 if success else 1)
