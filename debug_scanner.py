"""Debug scanner to see what's happening."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner

async def main():
    scanner = ActiveScanner()
    
    print("Testing with username 'blue' on GitHub...")
    results = await scanner.check_username("blue", platform_filter=["GitHub"])
    
    print(f"\nTotal results returned: {len(results)}")
    print(f"Results: {results}")
    
    if len(results) > 0:
        print("\nFirst result:")
        for key, value in results[0].items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
