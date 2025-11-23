import logging
import asyncio
import os
from typing import List
from panopticon.analysis.recon.headless_scanner import HeadlessScanner
from panopticon.persistence.vector.router import vector_router
from panopticon.analysis.visual.face_engine import FaceEngine
import numpy as np

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

class VisualCrawler:
    """
    Crawls web pages to harvest images and index faces.
    This implements the 'PimEyes Model' - building a reverse image search index from the open web.
    """
    def __init__(self):
        self.scanner = HeadlessScanner()
        self.face_engine = FaceEngine()
        self.router = vector_router

    async def crawl_and_index(self, url: str):
        """
        1. Visit URL (Headless)
        2. Extract all <img> src
        3. Download images
        4. Detect Faces
        5. Index Vectors
        """
        logger.info(f"Visual Crawl started for {url}")
        
        # We use Playwright to find images even if lazy-loaded
        # Re-using scanner logic but tailored for image extraction
        from playwright.async_api import async_playwright
        
        images = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=30000, wait_until="networkidle")
                
                # Extract image sources
                elements = await page.query_selector_all("img")
                for el in elements:
                    src = await el.get_attribute("src")
                    if src and src.startswith("http"):
                        images.append(src)
                        
            except Exception as e:
                logger.error(f"Crawl failed: {e}")
            finally:
                await browser.close()
                
        logger.info(f"Found {len(images)} images on {url}")
        
        # Process Images
        count = 0
        async with httpx.AsyncClient() as client:
            for img_url in images[:20]: # Limit per page to avoid abuse
                try:
                    resp = await client.get(img_url, timeout=5)
                    if resp.status_code == 200:
                        # Save to temp
                        temp_path = f"/tmp/vc_{hash(img_url)}.jpg"
                        with open(temp_path, "wb") as f:
                            f.write(resp.content)
                            
                        # Process
                        detections = self.face_engine.process_image(temp_path)
                        for det in detections:
                            vec = np.array(det["embedding"], dtype=np.float32)
                            # External ID is the Source URL + Image URL
                            self.router.add_vector(
                                vec, 
                                f"web_{hash(img_url)}", 
                                {"source_url": url, "image_url": img_url, "score": det["detection_score"]}
                            )
                            count += 1
                        
                        # Cleanup
                        os.remove(temp_path)
                except Exception as e:
                    pass
                    
        logger.info(f"Indexed {count} faces from {url}")
        return count
