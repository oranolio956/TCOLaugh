"""Test actual result format."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from panopticon.analysis.recon.active_scanner import ActiveScanner

async def test():
    scanner = ActiveScanner()
    results = await scanner.check_username("blue", platform_filter=["GitHub", "Twitter"])
    
    print("="*60)
    print("ACTUAL RESULT FORMAT")
    print("="*60)
    
    if results:
        print(f"\nFound {len(results)} results:")
        print("\nFirst result structure:")
        print(json.dumps(results[0], indent=2))
        
        print("\n" + "="*60)
        print("CHECKING FOR ENHANCED FEATURES:")
        print("="*60)
        
        result = results[0]
        checks = {
            "confidence": "confidence" in result,
            "methods_used": "methods_used" in result,
            "response_time_ms": "response_time_ms" in result,
            "method": "method" in result,
            "details": "details" in result,
        }
        
        for key, present in checks.items():
            status = "✓" if present else "✗"
            value = result.get(key, "MISSING")
            print(f"{status} {key}: {value}")
    
    await scanner.close()

asyncio.run(test())
