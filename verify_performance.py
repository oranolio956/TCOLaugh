import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from panopticon.analysis.recon.active_scanner import ActiveScanner

async def verify():
    s = ActiveScanner(timeout=3.0, max_concurrent=50)
    print('✅ Optimized scanner ready')
    print(f'  - Timeout: {s.timeout}s')
    print(f'  - Max concurrent: {s.max_concurrent}')
    print(f'  - Platforms: {s.platform_db.count() if s.platform_db else 0}')
    await s.close()

asyncio.run(verify())
