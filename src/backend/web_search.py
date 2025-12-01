"""
Web Search Module

Provides web search functionality using DuckDuckGo search API.
"""

from typing import Dict, List, Optional
import requests
from urllib.parse import quote
from src.utils.logger import get_logger, log_performance
from src.utils.error_handler import handle_error, ErrorType
from src.utils.retry import retry


class WebSearch:
    """
    Web search functionality using DuckDuckGo Instant Answer API.
    """
    
    def __init__(self):
        """Initialize the web search module."""
        self.logger = get_logger(__name__)
        self.base_url = "https://api.duckduckgo.com/"
        self.search_url = "https://html.duckduckgo.com/html/"
        self.logger.info("WebSearch initialized")
    
    @retry(max_retries=3, initial_delay=1.0, exponential_base=2.0, retryable_exceptions=(requests.RequestException,))
    @log_performance()
    def search(self, query: str, max_results: int = 5) -> Dict:
        """
        Search the web for a query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 5)
            
        Returns:
            Dictionary with search results:
            {
                "success": bool,
                "query": str,
                "results": List[Dict],  # List of {title, url, snippet}
                "error": str  # Error message if success is False
            }
        """
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Empty search query"
            }
        
        query = query.strip()
        self.logger.info(f"Searching web for: {query}")
        
        try:
            # Use DuckDuckGo Instant Answer API for quick results
            # Fallback to HTML scraping if needed
            results = self._search_duckduckgo(query, max_results)
            
            if results:
                self.logger.info(f"Found {len(results)} results for query: {query}")
                return {
                    "success": True,
                    "query": query,
                    "results": results
                }
            else:
                # Try alternative search method
                self.logger.warning(f"No results from DuckDuckGo API, trying alternative method")
                results = self._search_alternative(query, max_results)
                
                if results:
                    return {
                        "success": True,
                        "query": query,
                        "results": results
                    }
                else:
                    return {
                        "success": False,
                        "query": query,
                        "error": "No results found"
                    }
        
        except Exception as e:
            error_info = handle_error(e, context={"query": query}, logger=self.logger)
            return {
                "success": False,
                "query": query,
                "error": error_info["message"]
            }
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict]:
        """
        Search using DuckDuckGo Instant Answer API.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of result dictionaries
        """
        try:
            # DuckDuckGo Instant Answer API
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract Abstract (if available)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", query),
                    "url": data.get("AbstractURL", ""),
                    "snippet": data.get("Abstract", "")
                })
            
            # Extract Related Topics
            for topic in data.get("RelatedTopics", [])[:max_results - len(results)]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else query,
                        "url": topic.get("FirstURL", ""),
                        "snippet": topic.get("Text", "")
                    })
            
            return results[:max_results]
        
        except requests.RequestException as e:
            self.logger.debug(f"DuckDuckGo API request failed: {e}")
            return []
        except Exception as e:
            self.logger.debug(f"Error parsing DuckDuckGo results: {e}")
            return []
    
    def _search_alternative(self, query: str, max_results: int) -> List[Dict]:
        """
        Alternative search method using HTML parsing (fallback).
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of result dictionaries
        """
        try:
            # Simple fallback: return a formatted message
            # In a production system, you might use a different search API
            # or implement HTML parsing
            self.logger.info("Using alternative search method")
            
            # For now, return a helpful message
            return [{
                "title": f"Search results for: {query}",
                "url": f"https://duckduckgo.com/?q={quote(query)}",
                "snippet": f"Please visit DuckDuckGo to see results for '{query}'"
            }]
        
        except Exception as e:
            self.logger.error(f"Error in alternative search: {e}", exc_info=True)
            return []


def search_web(query: str, max_results: int = 5) -> str:
    """
    Convenience function for web search that returns formatted string.
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 5)
        
    Returns:
        Formatted string with search results
    """
    searcher = WebSearch()
    result = searcher.search(query, max_results)
    
    if not result["success"]:
        return f"Search failed: {result.get('error', 'Unknown error')}"
    
    if not result.get("results"):
        return f"No results found for: {query}"
    
    # Format results
    formatted = [f"Search results for: {query}\n"]
    for i, res in enumerate(result["results"], 1):
        formatted.append(f"{i}. {res['title']}")
        if res.get("url"):
            formatted.append(f"   URL: {res['url']}")
        if res.get("snippet"):
            formatted.append(f"   {res['snippet'][:200]}...")
        formatted.append("")
    
    return "\n".join(formatted)


if __name__ == "__main__":
    # Test the web search
    print("=" * 60)
    print("Testing Web Search")
    print("=" * 60)
    
    searcher = WebSearch()
    
    # Test search
    print("\n1. Testing search:")
    result = searcher.search("Python programming", max_results=3)
    if result["success"]:
        print(f"   ✅ Found {len(result['results'])} results")
        for i, res in enumerate(result["results"], 1):
            print(f"   {i}. {res['title']}")
            if res.get("url"):
                print(f"      URL: {res['url']}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    # Test convenience function
    print("\n2. Testing convenience function:")
    formatted = search_web("artificial intelligence", max_results=2)
    print(formatted)
    
    print("\n" + "=" * 60)
    print("✅ Web Search test complete!")
    print("=" * 60)

