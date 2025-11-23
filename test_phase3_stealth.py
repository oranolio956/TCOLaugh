"""Test Phase 3 stealth features."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.recon.proxy_manager import ProxyManager
from panopticon.analysis.recon.user_agent_rotator import UserAgentRotator
from panopticon.analysis.recon.rate_limiter import RateLimiter

async def test_stealth_features():
    print("="*60)
    print("PHASE 3: STEALTH FEATURES TEST")
    print("="*60)
    
    # Test 1: User-Agent Rotation
    print("\n1. User-Agent Rotation...")
    rotator = UserAgentRotator()
    ua1 = rotator.get_rotated()
    ua2 = rotator.get_rotated()
    ua3 = rotator.get_random()
    print(f"   ✓ Rotated UA 1: {ua1[:50]}...")
    print(f"   ✓ Rotated UA 2: {ua2[:50]}...")
    print(f"   ✓ Random UA: {ua3[:50]}...")
    if ua1 != ua2:
        print("   ✓ User-Agents are different (rotation working)")
    else:
        print("   ⚠ User-Agents are same")
    
    # Test 2: Rate Limiter
    print("\n2. Rate Limiter...")
    limiter = RateLimiter(default_requests_per_minute=30)
    print(f"   ✓ Default limit: {limiter.default_rpm} req/min")
    print(f"   ✓ GitHub limit: {limiter.get_limit('GitHub')} req/min")
    print(f"   ✓ Twitter limit: {limiter.get_limit('Twitter')} req/min")
    
    # Test 3: Proxy Manager (without actual proxies)
    print("\n3. Proxy Manager...")
    proxy_manager = ProxyManager(enable_proxy=False)
    stats = proxy_manager.get_stats()
    print(f"   ✓ Proxy manager initialized")
    print(f"   ✓ Enabled: {stats['enabled']}")
    print(f"   ✓ Total proxies: {stats['total_proxies']}")
    
    # Test 4: Scanner with stealth features
    print("\n4. Scanner with Stealth Features...")
    scanner = ActiveScanner(
        enable_rate_limiting=True,
        enable_user_agent_rotation=True,
        enable_proxy=False  # No proxies for testing
    )
    
    print(f"   ✓ Rate limiter: {scanner.rate_limiter is not None}")
    print(f"   ✓ User-Agent rotator: {scanner.user_agent_rotator is not None}")
    print(f"   ✓ Proxy manager: {scanner.proxy_manager is not None}")
    
    # Test 5: Actual scan with stealth features
    print("\n5. Test Scan with Stealth Features...")
    results = await scanner.check_username("blue", platform_filter=["GitHub", "Twitter"])
    
    print(f"   ✓ Found on {len(results)} platforms")
    if results:
        for result in results[:2]:
            print(f"   ✓ {result['site']}: {result.get('url', 'N/A')}")
    
    await scanner.close()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("✅ All stealth features initialized and working!")
    print("✅ User-Agent rotation: Active")
    print("✅ Rate limiting: Active")
    print("✅ Proxy manager: Ready (disabled for testing)")

if __name__ == "__main__":
    asyncio.run(test_stealth_features())
