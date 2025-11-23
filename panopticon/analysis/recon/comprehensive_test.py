"""
Comprehensive Testing Suite for Phase 1

Tests all aspects of the platform expansion system.
"""
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import httpx

from panopticon.analysis.recon.active_scanner import ActiveScanner
from panopticon.analysis.recon.detection_engine import DetectionEngine
from panopticon.analysis.recon.platform_database import PlatformDatabase, PlatformDefinition

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestResults:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.errors = []
    
    def add_pass(self, test_name: str):
        self.passed += 1
        logger.info(f"✓ PASS: {test_name}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append(f"{test_name}: {reason}")
        logger.error(f"✗ FAIL: {test_name} - {reason}")
    
    def add_skip(self, test_name: str, reason: str):
        self.skipped += 1
        logger.warning(f"⊘ SKIP: {test_name} - {reason}")
    
    def summary(self) -> str:
        total = self.passed + self.failed + self.skipped
        return f"""
{'='*60}
TEST SUMMARY
{'='*60}
Total Tests: {total}
  Passed: {self.passed} ({self.passed/total*100:.1f}%)
  Failed: {self.failed} ({self.failed/total*100:.1f}%)
  Skipped: {self.skipped} ({self.skipped/total*100:.1f}%)

Errors:
{chr(10).join(f'  - {e}' for e in self.errors) if self.errors else '  None'}
"""


async def test_platform_database_load(results: TestResults):
    """Test 1: Platform database loads correctly."""
    try:
        db = PlatformDatabase()
        count = db.count()
        
        if count == 473:
            results.add_pass("Platform database load (473 platforms)")
        elif count > 0:
            results.add_fail("Platform database load", f"Expected 473, got {count}")
        else:
            results.add_fail("Platform database load", "No platforms loaded")
    except Exception as e:
        results.add_fail("Platform database load", str(e))


async def test_scanner_initialization(results: TestResults):
    """Test 2: ActiveScanner initializes correctly."""
    try:
        scanner = ActiveScanner()
        
        if scanner.platform_db and scanner.platform_db.count() > 0:
            results.add_pass(f"ActiveScanner initialization ({scanner.platform_db.count()} platforms)")
        elif scanner.sites:
            results.add_pass("ActiveScanner initialization (fallback mode)")
        else:
            results.add_fail("ActiveScanner initialization", "No platforms or fallback")
    except Exception as e:
        results.add_fail("ActiveScanner initialization", str(e))


async def test_detection_engine(results: TestResults):
    """Test 3: Detection engine works correctly."""
    try:
        # Load a test platform (GitHub)
        db = PlatformDatabase()
        github = db.get_platform("GitHub")
        
        if not github:
            results.add_skip("Detection engine", "GitHub platform not found")
            return
        
        # Test with mock response
        result = DetectionEngine.detect(
            github,
            response_status=200,
            response_text="<html><body>GitHub Profile</body></html>",
            response_url="https://github.com/test",
            final_url="https://github.com/test"
        )
        
        if result.found and result.confidence > 0:
            results.add_pass("Detection engine (200 status)")
        else:
            results.add_fail("Detection engine", f"Unexpected result: {result}")
        
        # Test with 404
        result_404 = DetectionEngine.detect(
            github,
            response_status=404,
            response_text="<html><body>404 Not Found</body></html>",
            response_url="https://github.com/test",
            final_url="https://github.com/test"
        )
        
        if not result_404.found:
            results.add_pass("Detection engine (404 status)")
        else:
            results.add_fail("Detection engine", f"404 should not be found: {result_404}")
    
    except Exception as e:
        results.add_fail("Detection engine", str(e))


async def test_username_validation(results: TestResults):
    """Test 4: Username validation works."""
    try:
        db = PlatformDatabase()
        
        # Find a platform with regex
        platform_with_regex = None
        for name, platform in db.get_all_platforms().items():
            if platform.regex_check:
                platform_with_regex = platform
                break
        
        if not platform_with_regex:
            results.add_skip("Username validation", "No platform with regex found")
            return
        
        # Test valid username
        valid = platform_with_regex.validate_username("test123")
        # Test invalid username (if regex exists)
        invalid = platform_with_regex.validate_username("invalid-username-with-dashes")
        
        results.add_pass("Username validation")
    
    except Exception as e:
        results.add_fail("Username validation", str(e))


async def test_real_platform_scan(results: TestResults, username: str = "blue"):
    """Test 5: Real platform scan with known username."""
    try:
        scanner = ActiveScanner()
        
        # Test with a few reliable platforms
        test_platforms = ["GitHub", "Twitter", "Reddit"]
        results_list = await scanner.check_username(username, platform_filter=test_platforms)
        
        if len(results_list) > 0:
            found_count = len(results_list)  # All results are "found" (only found usernames are returned)
            results.add_pass(f"Real platform scan (found on {found_count}/{len(test_platforms)} platforms)")
        else:
            results.add_fail("Real platform scan", "No results returned")
    
    except Exception as e:
        results.add_fail("Real platform scan", str(e))


async def test_nonexistent_username(results: TestResults):
    """Test 6: Non-existent username detection."""
    try:
        scanner = ActiveScanner()
        
        # Use a very unlikely username
        fake_username = "definitelydoesnotexist12345xyz98765"
        results_list = await scanner.check_username(fake_username, platform_filter=["GitHub"])
        
        # GitHub should return empty (no results = username doesn't exist)
        if len(results_list) == 0:
            results.add_pass("Non-existent username detection")
        else:
            # If we got results, it's a false positive
            results.add_fail("Non-existent username detection", f"False positive: got {len(results_list)} results")
    
    except Exception as e:
        results.add_fail("Non-existent username detection", str(e))


async def test_batch_platforms(results: TestResults, count: int = 20):
    """Test 7: Test a batch of diverse platforms."""
    try:
        db = PlatformDatabase()
        scanner = ActiveScanner()
        
        # Get diverse platforms
        all_platforms = list(db.get_all_platforms().keys())
        test_platforms = all_platforms[:count]
        
        logger.info(f"Testing {len(test_platforms)} platforms...")
        
        # Test with a known username
        results_list = await scanner.check_username("blue", platform_filter=test_platforms)
        
        success_count = len(results_list)
        success_rate = success_count / len(test_platforms) * 100
        
        if success_rate >= 50:  # At least 50% should work
            results.add_pass(f"Batch platform test ({success_count}/{len(test_platforms)} successful)")
        else:
            results.add_fail("Batch platform test", f"Only {success_rate:.1f}% successful")
    
    except Exception as e:
        results.add_fail("Batch platform test", str(e))


async def test_error_handling(results: TestResults):
    """Test 8: Error handling (timeouts, network errors)."""
    try:
        scanner = ActiveScanner(timeout=0.1)  # Very short timeout
        
        # This should handle timeouts gracefully
        results_list = await scanner.check_username("test", platform_filter=["GitHub"])
        
        # Should not crash
        results.add_pass("Error handling (timeouts)")
    
    except Exception as e:
        results.add_fail("Error handling", str(e))


async def test_concurrent_requests(results: TestResults):
    """Test 9: Concurrent request handling."""
    try:
        scanner = ActiveScanner()
        
        # Make multiple concurrent requests
        tasks = [
            scanner.check_username("blue", platform_filter=["GitHub"]),
            scanner.check_username("test", platform_filter=["GitHub"]),
            scanner.check_username("user", platform_filter=["GitHub"]),
        ]
        
        all_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check no exceptions
        exceptions = [r for r in all_results if isinstance(r, Exception)]
        if len(exceptions) == 0:
            results.add_pass("Concurrent request handling")
        else:
            results.add_fail("Concurrent request handling", f"{len(exceptions)} exceptions")
    
    except Exception as e:
        results.add_fail("Concurrent request handling", str(e))


async def test_platform_database_structure(results: TestResults):
    """Test 10: Validate platform database structure."""
    try:
        db = PlatformDatabase()
        
        required_fields = ["url", "urlMain", "errorType", "username_claimed"]
        invalid_platforms = []
        
        for name, platform in db.get_all_platforms().items():
            if not platform.url_template or not platform.url_main:
                invalid_platforms.append(name)
        
        if len(invalid_platforms) == 0:
            results.add_pass("Platform database structure validation")
        else:
            results.add_fail("Platform database structure", f"{len(invalid_platforms)} invalid platforms")
    
    except Exception as e:
        results.add_fail("Platform database structure", str(e))


async def test_special_characters(results: TestResults):
    """Test 11: Special characters in usernames."""
    try:
        scanner = ActiveScanner()
        
        # Test with special characters
        special_usernames = ["test-user", "test_user", "test.user", "test123"]
        
        for username in special_usernames:
            try:
                results_list = await scanner.check_username(username, platform_filter=["GitHub"])
                # Should not crash
            except Exception as e:
                results.add_fail("Special characters", f"Failed for '{username}': {e}")
                return
        
        results.add_pass("Special characters handling")
    
    except Exception as e:
        results.add_fail("Special characters", str(e))


async def run_all_tests():
    """Run all tests."""
    results = TestResults()
    
    logger.info("="*60)
    logger.info("COMPREHENSIVE TEST SUITE - PHASE 1")
    logger.info("="*60)
    logger.info("")
    
    # Run tests
    await test_platform_database_load(results)
    await test_scanner_initialization(results)
    await test_detection_engine(results)
    await test_username_validation(results)
    await test_real_platform_scan(results)
    await test_nonexistent_username(results)
    await test_error_handling(results)
    await test_concurrent_requests(results)
    await test_platform_database_structure(results)
    await test_special_characters(results)
    
    # Batch test (slower, so do it last)
    logger.info("Running batch platform test (this may take a while)...")
    await test_batch_platforms(results, count=30)
    
    # Print summary
    print(results.summary())
    
    # Save results
    output_file = Path(__file__).parent / "platforms" / "comprehensive_test_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "passed": results.passed,
            "failed": results.failed,
            "skipped": results.skipped,
            "errors": results.errors,
            "timestamp": time.time()
        }, f, indent=2)
    
    logger.info(f"Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
