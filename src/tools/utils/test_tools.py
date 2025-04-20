"""Test script for verifying tool functionality."""

import unittest
from src.tools.web_scraper import WebScraperTool
from src.tools.career_path import CareerPathTool
from src.tools.tool_registry import get_registry
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestTools(unittest.TestCase):
    """Test suite for verifying tool functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = get_registry()
        self.web_scraper = WebScraperTool()
        self.career_path = CareerPathTool()
    
    def test_tool_registry(self):
        """Test tool registry functionality."""
        logger.info("Testing tool registry...")
        
        # Test if registry has tools
        tools = self.registry.get_all_tools()
        self.assertTrue(len(tools) > 0)
        logger.info(f"Found {len(tools)} registered tools")
        
        # Test if we can get specific tools
        web_scraper = self.registry.get_tool("web_scraper")
        self.assertIsNotNone(web_scraper)
        self.assertIsInstance(web_scraper, WebScraperTool)
        
        career_path = self.registry.get_tool("career_path")
        self.assertIsNotNone(career_path)
        self.assertIsInstance(career_path, CareerPathTool)
    
    def test_web_scraper(self):
        """Test web scraper functionality."""
        logger.info("Testing web scraper...")
        
        # Test with a simple URL
        url = "https://example.com"
        result = self.web_scraper._execute(url)
        
        # Check if result is a string
        self.assertIsInstance(result, str)
        
        # Check if result contains expected content
        self.assertTrue(len(result) > 0)
        self.assertIn('http', result.lower())  # Should contain URL
    
    def test_career_path(self):
        """Test career path tool functionality."""
        logger.info("Testing career path tool...")
        
        # Test with a sample query
        query = "I'm interested in software development"
        result = self.career_path._execute(query)
        
        # Check if result is a string
        self.assertIsInstance(result, str)
        
        # Check if result contains expected content
        self.assertTrue(len(result) > 0)
        self.assertIn('career', result.lower())
        self.assertIn('skill', result.lower())
        self.assertIn('learning', result.lower())

if __name__ == '__main__':
    unittest.main() 