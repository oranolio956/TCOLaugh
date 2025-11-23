import httpx
import asyncio
import time

async def test():
    async with httpx.AsyncClient() as c:
        start = time.time()
        r = await c.get('https://github.com')
        elapsed = time.time() - start
        print(f'Manual timing: {elapsed*1000:.2f}ms')
        print(f'Has elapsed attr: {hasattr(r, "elapsed")}')

asyncio.run(test())
