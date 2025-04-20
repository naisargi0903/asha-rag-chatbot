"""Web search tool for fetching real-time information."""

from typing import Dict, Any, List
from src.tools.tool_registry import BaseTool, register_tool
import logging
import requests
from datetime import datetime
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)

@register_tool
class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Fetches real-time information from the web using search APIs"
        )
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "web_search"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load API keys from environment
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for a query."""
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()
    
    def _load_from_cache(self, query: str, max_age_hours: int = 24) -> List[str]:
        """Load results from cache if fresh."""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                if self._is_cache_fresh(data['timestamp'], max_age_hours):
                    return data['results']
            except Exception as e:
                logger.error(f"Error loading from cache: {str(e)}")
        return None
    
    def _save_to_cache(self, query: str, results: List[str]):
        """Save results to cache."""
        cache_key = self._get_cache_key(query)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
    
    def _is_cache_fresh(self, timestamp: str, max_age_hours: int = 24) -> bool:
        """Check if cached data is fresh."""
        try:
            last_update = datetime.fromisoformat(timestamp)
            age = datetime.now() - last_update
            return age.total_seconds() < (max_age_hours * 3600)
        except:
            return False
    
    def _search_serp_api(self, query: str) -> List[str]:
        """Search using SERP API."""
        if not self.serp_api_key:
            logger.warning("SERP API key not found")
            return []
            
        try:
            url = "https://serpapi.com/search"
            params = {
                'api_key': self.serp_api_key,
                'q': query,
                'engine': 'google'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract organic results
            for result in data.get('organic_results', [])[:5]:
                results.append(f"{result['title']}: {result['snippet']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching SERP API: {str(e)}")
            return []
    
    def _search_news_api(self, query: str) -> List[str]:
        """Search using News API."""
        if not self.news_api_key:
            logger.warning("News API key not found")
            return []
            
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': self.news_api_key,
                'q': query,
                'sortBy': 'relevancy',
                'language': 'en'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Extract articles
            for article in data.get('articles', [])[:5]:
                results.append(f"{article['title']}: {article['description']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching News API: {str(e)}")
            return []
    
    def _execute(self, query: str) -> List[str]:
        """Execute web search.
        
        Args:
            query: Search query
            
        Returns:
            List of search result strings
        """
        # Try cache first
        cached_results = self._load_from_cache(query)
        if cached_results:
            return cached_results
        
        # Perform searches
        results = []
        
        # Try SERP API first
        serp_results = self._search_serp_api(query)
        if serp_results:
            results.extend(serp_results)
        
        # If not enough results, try News API
        if len(results) < 5:
            news_results = self._search_news_api(query)
            results.extend(news_results)
        
        # Deduplicate and limit results
        results = list(dict.fromkeys(results))[:5]
        
        # Cache results
        if results:
            self._save_to_cache(query, results)
        
        return results if results else ["No results found."]
    
    def get_response_title(self, query: str) -> str:
        """Override to provide a more specific title."""
        return f"Search Results for '{query}'" 