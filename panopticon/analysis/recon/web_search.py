import logging
from typing import List

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

logger = logging.getLogger(__name__)

class WebSearch:
    def __init__(self):
        if not DDGS_AVAILABLE:
            logger.warning("duckduckgo-search not installed. Web search disabled.")

    def search_public(self, query: str, num_results: int = 5) -> List[str]:
        """
        Performs a public web search using DuckDuckGo.
        """
        if not DDGS_AVAILABLE:
            return []
        
        try:
            results = []
            with DDGS() as ddgs:
                # max_results is named differently in different versions, checking docs/typical usage
                # .text(keywords, max_results=...)
                for r in ddgs.text(query, max_results=num_results):
                    # Result is a dict with 'title', 'href', 'body'
                    if 'href' in r:
                        results.append(r['href'])
            return results
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []

    def dork_search(self, target: str, dork_type: str) -> List[str]:
        """
        Performs search with specific keywords.
        """
        if dork_type == "social":
            q = f'{target} (site:twitter.com OR site:facebook.com OR site:instagram.com OR site:linkedin.com)'
        elif dork_type == "documents":
            q = f'{target} (filetype:pdf OR filetype:doc OR filetype:xls)'
        elif dork_type == "email":
            q = f'"{target}" email OR contact OR "gmail.com" OR "yahoo.com"'
        else:
            q = target
            
        return self.search_public(q, num_results=5)
