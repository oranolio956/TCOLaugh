"""
Performance Analyzer - Identify bottlenecks and optimize.
"""
import asyncio
import sys
import time
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner


async def benchmark_scanner():
    """Benchmark current scanner performance."""
    scanner = ActiveScanner()
    
    # Test with different batch sizes
    test_username = "blue"
    batch_sizes = [5, 10, 20, 30, 50]
    
    print("="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    results = {}
    
    for batch_size in batch_sizes:
        # Get platforms
        all_platforms = list(scanner.platform_db.get_all_platforms().keys())[:batch_size]
        
        # Time the scan
        start_time = time.time()
        scan_results = await scanner.check_username(test_username, platform_filter=all_platforms)
        elapsed = time.time() - start_time
        
        found_count = len(scan_results)
        platforms_per_second = batch_size / elapsed if elapsed > 0 else 0
        
        results[batch_size] = {
            "elapsed": elapsed,
            "found": found_count,
            "platforms_per_second": platforms_per_second,
            "avg_time_per_platform": elapsed / batch_size if batch_size > 0 else 0
        }
        
        print(f"\nBatch Size: {batch_size}")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Found: {found_count}")
        print(f"  Platforms/sec: {platforms_per_second:.2f}")
        print(f"  Avg per platform: {elapsed/batch_size*1000:.0f}ms")
    
    return results


async def analyze_bottlenecks():
    """Analyze where time is spent."""
    import httpx
    
    scanner = ActiveScanner()
    test_platforms = ["GitHub", "Twitter", "Reddit", "Instagram", "About.me"]
    
    print("\n" + "="*60)
    print("BOTTLENECK ANALYSIS")
    print("="*60)
    
    times = {
        "platform_load": [],
        "http_request": [],
        "detection": [],
        "total": []
    }
    
    for platform_name in test_platforms:
        platform = scanner.platform_db.get_platform(platform_name)
        if not platform:
            continue
        
        # Time platform loading
        t0 = time.time()
        url = platform.build_url("test")
        t1 = time.time()
        times["platform_load"].append(t1 - t0)
        
        # Time HTTP request
        t2 = time.time()
        async with httpx.AsyncClient(timeout=6.0) as client:
            try:
                response = await client.get(url)
                t3 = time.time()
                times["http_request"].append(t3 - t2)
                
                # Time detection
                t4 = time.time()
                from panopticon.analysis.recon.detection_engine import DetectionEngine
                DetectionEngine.detect(
                    platform,
                    response.status_code,
                    response.text,
                    url,
                    str(response.url)
                )
                t5 = time.time()
                times["detection"].append(t5 - t4)
                times["total"].append(t5 - t0)
            except Exception as e:
                print(f"Error testing {platform_name}: {e}")
    
    print("\nAverage Times:")
    for category, values in times.items():
        if values:
            avg = sum(values) / len(values)
            print(f"  {category}: {avg*1000:.0f}ms (min: {min(values)*1000:.0f}ms, max: {max(values)*1000:.0f}ms)")
    
    return times


if __name__ == "__main__":
    print("Running performance analysis...")
    asyncio.run(benchmark_scanner())
    asyncio.run(analyze_bottlenecks())
