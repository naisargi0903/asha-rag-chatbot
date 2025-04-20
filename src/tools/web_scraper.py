"""Web scraping tool for RAG knowledge base."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Dict, Any, Optional
import logging
from src.tools.tool_registry import BaseTool

logger = logging.getLogger(__name__)

class WebScraperTool(BaseTool):
    """Tool for scraping and processing web content."""
    
    def __init__(self):
        super().__init__(
            name="web_scraper",
            description="Scrapes and processes web content for knowledge base"
        )
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract main content from webpage."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        return self._clean_text(text)
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _fetch_url(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse webpage."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract relevant links from webpage."""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            if self._is_valid_url(absolute_url):
                links.append(absolute_url)
        return links
    
    def _execute(self, query: str) -> str:
        """Execute web scraping based on query.
        
        Args:
            query: Search query or URL
        
        Returns:
            Formatted string containing scraped content
        """
        max_depth = 1
        max_pages = 5
        include_links = True
        
        results = {
            'content': [],
            'metadata': [],
            'links': []
        }
        
        # Check if query is a URL
        if self._is_valid_url(query):
            urls_to_scrape = [query]
        else:
            # TODO: Implement search engine integration
            # For now, return empty results
            return "No valid URL provided. Please provide a valid URL to scrape."
        
        depth = 0
        while depth < max_depth and urls_to_scrape and len(results['content']) < max_pages:
            current_url = urls_to_scrape.pop(0)
            soup = self._fetch_url(current_url)
            
            if soup:
                # Extract main content
                text = self._extract_text(soup)
                if text:
                    results['content'].append({
                        'url': current_url,
                        'text': text
                    })
                    
                    # Extract metadata
                    title = soup.title.string if soup.title else ''
                    description = soup.find('meta', attrs={'name': 'description'})
                    description = description['content'] if description else ''
                    
                    results['metadata'].append({
                        'url': current_url,
                        'title': title,
                        'description': description
                    })
                
                # Extract links if needed
                if include_links and depth < max_depth - 1:
                    new_links = self._extract_links(soup, current_url)
                    urls_to_scrape.extend(new_links)
                    results['links'].extend(new_links)
            
            depth += 1
        
        # Format results as string
        output = []
        
        # Add metadata
        for meta in results['metadata']:
            output.append(f"📄 {meta['title']}")
            if meta['description']:
                output.append(f"📝 {meta['description']}\n")
            output.append(f"🔗 {meta['url']}\n")
        
        # Add content
        for content in results['content']:
            output.append(content['text'])
            output.append("\n---\n")
        
        # Add extracted links if any
        if results['links']:
            output.append("\n🔍 Related Links:")
            for link in results['links'][:5]:  # Limit to 5 links
                output.append(f"• {link}")
        
        return "\n".join(output) if output else "No content found at the provided URL." 