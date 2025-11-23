import asyncio
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from panopticon.analysis.recon.active_scanner import ActiveScanner

async def test():
    print("Testing optimized scanner...")
    scanner = ActiveScanner(timeout=3.0, max_concurrent=50)
    start = time.time()
    results = await scanner.check_username("blue", platform_filter=["GitHub", "Twitter", "Reddit", "Instagram", "About.me"])
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Found: {len(results)} platforms")
    await scanner.close()

asyncio.run(test())
