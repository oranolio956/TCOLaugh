"""
Platform Testing Script

Tests individual platforms to ensure they work correctly.
Run this to verify each platform before adding to production.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

import httpx

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from panopticon.analysis.recon.detection_engine import DetectionEngine
from panopticon.analysis.recon.platform_database import PlatformDefinition

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_platform(
    platform: PlatformDefinition,
    test_username: Optional[str] = None,
    timeout: float = 10.0
) -> Dict:
    """
    Test a single platform with a username.
    
    Args:
        platform: Platform definition to test
        test_username: Username to test (uses platform.username_claimed if None)
        timeout: Request timeout in seconds
    
    Returns:
        Dict with test results
    """
    username = test_username or platform.username_claimed
    if not username:
        return {
            "platform": platform.name,
            "status": "SKIP",
            "reason": "No test username provided"
        }
    
    # Validate username format
    if not platform.validate_username(username):
        return {
            "platform": platform.name,
            "status": "SKIP",
            "reason": f"Username '{username}' doesn't match regex: {platform.regex_check}"
        }
    
    url = platform.build_url(username)
    
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            # Prepare request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            headers.update(platform.headers)
            
            # Make request
            if platform.request_method == "POST":
                response = await client.post(
                    url,
                    json=platform.request_payload,
                    headers=headers
                )
            else:
                response = await client.get(url, headers=headers)
            
            # Get final URL after redirects
            final_url = str(response.url)
            
            # Detect using engine
            result = DetectionEngine.detect(
                platform,
                response.status_code,
                response.text,
                url,
                final_url
            )
            
            return {
                "platform": platform.name,
                "username": username,
                "url": url,
                "status_code": response.status_code,
                "final_url": final_url,
                "detection": {
                    "found": result.found,
                    "confidence": result.confidence,
                    "method": result.method,
                    "details": result.details
                },
                "status": "SUCCESS"
            }
    
    except httpx.TimeoutException:
        return {
            "platform": platform.name,
            "username": username,
            "url": url,
            "status": "TIMEOUT",
            "error": "Request timed out"
        }
    
    except Exception as e:
        return {
            "platform": platform.name,
            "username": username,
            "url": url,
            "status": "ERROR",
            "error": str(e)
        }


async def test_platforms_from_sherlock(
    sherlock_data_file: str,
    limit: Optional[int] = None,
    start_index: int = 0
):
    """
    Test platforms from Sherlock's data.json file.
    
    Args:
        sherlock_data_file: Path to Sherlock's data.json
        limit: Maximum number of platforms to test (None = all)
        start_index: Index to start from (for resuming)
    """
    # Load Sherlock data
    with open(sherlock_data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter out schema keys
    platforms_data = {k: v for k, v in data.items() if not k.startswith("$")}
    platform_names = list(platforms_data.keys())[start_index:]
    
    if limit:
        platform_names = platform_names[:limit]
    
    logger.info(f"Testing {len(platform_names)} platforms...")
    
    results = []
    for i, name in enumerate(platform_names, start=1):
        logger.info(f"[{i}/{len(platform_names)}] Testing {name}...")
        
        try:
            platform = PlatformDefinition(name, platforms_data[name])
            result = await test_platform(platform)
            results.append(result)
            
            # Log result
            if result["status"] == "SUCCESS":
                found = result["detection"]["found"]
                confidence = result["detection"]["confidence"]
                logger.info(f"  ✓ {name}: {'FOUND' if found else 'NOT_FOUND'} (confidence: {confidence:.2f})")
            else:
                logger.warning(f"  ✗ {name}: {result['status']} - {result.get('error', result.get('reason', ''))}")
        
        except Exception as e:
            logger.error(f"  ✗ {name}: Exception - {e}")
            results.append({
                "platform": name,
                "status": "EXCEPTION",
                "error": str(e)
            })
        
        # Small delay to be respectful
        await asyncio.sleep(0.5)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    success = sum(1 for r in results if r["status"] == "SUCCESS")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    timeouts = sum(1 for r in results if r["status"] == "TIMEOUT")
    skipped = sum(1 for r in results if r["status"] == "SKIP")
    
    logger.info(f"Total tested: {len(results)}")
    logger.info(f"  Success: {success}")
    logger.info(f"  Errors: {errors}")
    logger.info(f"  Timeouts: {timeouts}")
    logger.info(f"  Skipped: {skipped}")
    
    # Save results
    output_file = Path(__file__).parent / "platforms" / "test_results.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test platforms from Sherlock")
    parser.add_argument("--sherlock-data", default="/tmp/sherlock/sherlock_project/resources/data.json",
                       help="Path to Sherlock's data.json")
    parser.add_argument("--limit", type=int, default=5,
                       help="Limit number of platforms to test")
    parser.add_argument("--start", type=int, default=0,
                       help="Start index")
    
    args = parser.parse_args()
    
    asyncio.run(test_platforms_from_sherlock(
        args.sherlock_data,
        limit=args.limit,
        start_index=args.start
    ))
