import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class KnowledgeBase:
    """Knowledge base for career guidance data and API integration."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("data")
        self.srp_api_key = os.getenv("SERP_API_KEY")
        self.news_api_key = os.getenv("NEWS_API_KEY")
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data files
        self._ensure_data_files_exist()
        
    def _ensure_data_files_exist(self):
        """Ensure all required data files exist."""
        files = [
            "career_resources.json",
            "market_trends.json",
            "career_insights.json"
        ]
        
        for file in files:
            file_path = self.data_dir / file
            if not file_path.exists():
                self._create_empty_json_file(file_path)
                
    def _create_empty_json_file(self, file_path: Path):
        """Create an empty JSON file with basic structure."""
        if file_path.name == "career_resources.json":
            data = {
                "learning_resources": {
                    "python_development": [],
                    "web_development": [],
                    "data_science": [],
                    "machine_learning": [],
                    "cloud_computing": []
                },
                "career_paths": {
                    "software_development": [],
                    "data_engineering": [],
                    "devops": [],
                    "ai_ml": [],
                    "cloud_architecture": []
                },
                "last_updated": "",
                "source": "serp_api"
            }
        elif file_path.name == "market_trends.json":
            data = {
                "industry_trends": {
                    "software_development": {},
                    "data_science": {},
                    "ai_ml": {},
                    "cloud_computing": {},
                    "cybersecurity": {}
                },
                "job_market_insights": {
                    "demand_level": "",
                    "growth_rate": "",
                    "top_companies": [],
                    "required_skills": [],
                    "salary_ranges": {},
                    "remote_opportunities": {}
                },
                "last_updated": "",
                "source": "news_api"
            }
        else:  # career_insights.json
            data = {
                "success_stories": {
                    "software_development": [],
                    "data_science": [],
                    "ai_ml": [],
                    "cloud_computing": [],
                    "cybersecurity": []
                },
                "career_advice": {
                    "entry_level": [],
                    "mid_level": [],
                    "senior_level": []
                },
                "interview_insights": {
                    "technical_interviews": [],
                    "behavioral_interviews": [],
                    "system_design": []
                },
                "skill_development": {
                    "technical_skills": [],
                    "soft_skills": [],
                    "leadership_skills": []
                },
                "last_updated": "",
                "source": "serp_api"
            }
            
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
            
    def load_data(self, file_name: str) -> Dict:
        """Load data from a JSON file."""
        try:
            file_path = self.data_dir / file_name
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading data from {file_name}: {str(e)}")
            return {}
            
    def save_data(self, file_name: str, data: Dict):
        """Save data to a JSON file."""
        try:
            file_path = self.data_dir / file_name
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving data to {file_name}: {str(e)}")
            
    def fetch_srp_data(self, query: str) -> Dict:
        """Fetch data from the SERP API."""
        if not self.srp_api_key:
            self.logger.error("SERP API key not found")
            return {}
            
        try:
            params = {
                "api_key": self.srp_api_key,
                "q": query,
                "engine": "google",
                "num": 10
            }
            
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching data from SERP API: {str(e)}")
            return {}
            
    def fetch_news_data(self, query: str) -> Dict:
        """Fetch data from the News API."""
        if not self.news_api_key:
            self.logger.error("News API key not found")
            return {}
            
        try:
            params = {
                "apiKey": self.news_api_key,
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10
            }
            
            response = requests.get("https://newsapi.org/v2/everything", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching data from News API: {str(e)}")
            return {}
            
    def update_career_resources(self, role: str, skills: List[str]):
        """Update career resources based on role and skills."""
        query = f"{role} career path {', '.join(skills)}"
        srp_data = self.fetch_srp_data(query)
        
        if not srp_data:
            return
            
        resources = self.load_data("career_resources.json")
        
        # Extract learning resources
        if "organic_results" in srp_data:
            for result in srp_data["organic_results"]:
                if "title" in result and "link" in result:
                    resource = {
                        "title": result["title"],
                        "url": result["link"],
                        "description": result.get("snippet", ""),
                        "type": "learning_resource"
                    }
                    
                    # Add to appropriate category
                    for category in resources["learning_resources"]:
                        if category in result["title"].lower():
                            resources["learning_resources"][category].append(resource)
                            
        # Update last_updated timestamp
        resources["last_updated"] = str(datetime.now())
        
        # Save updated data
        self.save_data("career_resources.json", resources)
        
    def update_market_trends(self, role: str):
        """Update market trends based on role."""
        query = f"{role} job market trends 2024"
        news_data = self.fetch_news_data(query)
        
        if not news_data:
            return
            
        trends = self.load_data("market_trends.json")
        
        # Extract market trends
        if "articles" in news_data:
            for article in news_data["articles"]:
                if "title" in article and "url" in article:
                    trend = {
                        "title": article["title"],
                        "url": article["url"],
                        "description": article.get("description", ""),
                        "published_at": article.get("publishedAt", ""),
                        "source": article.get("source", {}).get("name", "")
                    }
                    
                    # Add to appropriate category
                    for category in trends["industry_trends"]:
                        if category in article["title"].lower():
                            trends["industry_trends"][category] = trend
                            
        # Update last_updated timestamp
        trends["last_updated"] = str(datetime.now())
        
        # Save updated data
        self.save_data("market_trends.json", trends)
        
    def update_career_insights(self, role: str):
        """Update career insights based on role."""
        query = f"{role} career success stories and advice"
        srp_data = self.fetch_srp_data(query)
        
        if not srp_data:
            return
            
        insights = self.load_data("career_insights.json")
        
        # Extract success stories and advice
        if "organic_results" in srp_data:
            for result in srp_data["organic_results"]:
                if "title" in result and "link" in result:
                    insight = {
                        "title": result["title"],
                        "url": result["link"],
                        "description": result.get("snippet", ""),
                        "type": "success_story" if "success" in result["title"].lower() else "career_advice"
                    }
                    
                    # Add to appropriate category
                    if insight["type"] == "success_story":
                        for category in insights["success_stories"]:
                            if category in result["title"].lower():
                                insights["success_stories"][category].append(insight)
                    else:
                        for category in insights["career_advice"]:
                            if category in result["title"].lower():
                                insights["career_advice"][category].append(insight)
                                
        # Update last_updated timestamp
        insights["last_updated"] = str(datetime.now())
        
        # Save updated data
        self.save_data("career_insights.json", insights)
        
    def get_career_guidance(self, role: str, skills: List[str]) -> Dict:
        """Get comprehensive career guidance based on role and skills."""
        # Update data from APIs
        self.update_career_resources(role, skills)
        self.update_market_trends(role)
        self.update_career_insights(role)
        
        # Load all data
        resources = self.load_data("career_resources.json")
        trends = self.load_data("market_trends.json")
        insights = self.load_data("career_insights.json")
        
        # Combine and format response
        return {
            "role": role,
            "skills": skills,
            "learning_resources": resources["learning_resources"],
            "market_trends": trends["industry_trends"],
            "success_stories": insights["success_stories"],
            "career_advice": insights["career_advice"],
            "last_updated": {
                "resources": resources["last_updated"],
                "trends": trends["last_updated"],
                "insights": insights["last_updated"]
            }
        }