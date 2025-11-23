import logging
import os
import asyncio
from typing import Optional, Dict, Any, List
from panopticon.analysis.recon.active_scanner import ProxyManager

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

class HeadlessScanner:
    """
    Handles complex web interactions using a headless browser.
    Features:
    - JS Execution
    - Screenshotting (Visual Recon)
    - Proxy Support
    - User-Agent Rotation
    """
    def __init__(self):
        self.proxy_manager = ProxyManager()
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not installed. Headless scanning disabled.")

    async def scan_profile(self, url: str, check_text: Optional[str] = None) -> Dict[str, Any]:
        """
        Visits a profile URL and determines if it exists.
        Returns metadata and potentially a screenshot path.
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {"error": "Playwright unavailable"}

        result = {
            "url": url,
            "exists": False,
            "title": "",
            "screenshot": None,
            "method": "headless"
        }

        proxy_url = self.proxy_manager.get_proxy()
        # Playwright proxy format: { "server": "http://..." }
        proxy_config = {"server": proxy_url} if proxy_url else None

        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    proxy=proxy_config,
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"] # Anti-detection
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={"width": 1280, "height": 720},
                    locale="en-US"
                )
                
                page = await context.new_page()
                
                try:
                    # Navigate with timeout
                    await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                    
                    # Check for typical 404 indicators if check_text not provided
                    content = await page.content()
                    title = await page.title()
                    result["title"] = title
                    
                    # Simple 404 logic
                    not_found_terms = ["page not found", "doesn't exist", "suspended", "404"]
                    if any(term in title.lower() for term in not_found_terms):
                        result["exists"] = False
                    elif check_text and check_text not in content:
                        result["exists"] = False
                    else:
                        result["exists"] = True
                        # Take screenshot for visual evidence
                        # Ensure directory exists
                        os.makedirs("/tmp/panopticon_screens", exist_ok=True)
                        filename = f"/tmp/panopticon_screens/{hash(url)}.png"
                        await page.screenshot(path=filename)
                        result["screenshot"] = filename
                        
                except PlaywrightTimeout:
                    logger.warning(f"Timeout scanning {url}")
                    result["error"] = "Timeout"
                except Exception as e:
                    logger.warning(f"Page error {url}: {e}")
                    result["error"] = str(e)
                
                await browser.close()
                
            except Exception as e:
                logger.error(f"Browser launch failed: {e}")
                result["error"] = str(e)

        return result
