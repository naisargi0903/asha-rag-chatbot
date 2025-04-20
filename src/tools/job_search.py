import requests
import json
import re
from typing import Dict, List, Any, Optional, Union
import os
from src.tools.tool_registry import BaseTool, register_tool
from src.tools.web_search import WebSearchTool
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@register_tool
class JobSearchTool(BaseTool):
    """Tool for searching and recommending jobs."""
    
    def __init__(self):
        super().__init__(
            name="job_search",
            description="Provides personalized job recommendations with real-time market data"
        )
        self.api_key = "e10dad0fc6msh8db63d5ea96bf1dp17c351jsn8ab61d7adb5b"
        self.base_url = "https://jsearch.p.rapidapi.com/search"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        self.web_search = WebSearchTool()
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "job_search"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Mock job data for demo purposes
        self.mock_jobs = [
            {
                "title": "UX/UI Designer (Junior)",
                "company": "TechStart Solutions",
                "location": "Remote, India",
                "description": "Looking for a creative junior designer with experience in user research and wireframing.",
                "requirements": ["Basic wireframing skills", "Understanding of user research", "Portfolio of design work"],
                "women_friendly_score": 0.85,
                "inclusive_keywords": ["diverse team", "flexible hours", "mentorship program"]
            },
            {
                "title": "Junior UX Researcher",
                "company": "InnovateCorp",
                "location": "Bangalore, India",
                "description": "Join our research team to conduct user interviews and usability testing.",
                "requirements": ["Knowledge of user research methods", "Good communication skills", "Analytical mindset"],
                "women_friendly_score": 0.9,
                "inclusive_keywords": ["women in tech", "equal opportunity", "work-life balance"]
            },
            {
                "title": "UX Design Associate",
                "company": "DesignHub",
                "location": "Hybrid - Mumbai, India",
                "description": "Mentorship program specifically for career changers moving into UX design.",
                "requirements": ["Passion for UX", "Prior experience in any field", "Willingness to learn"],
                "women_friendly_score": 0.95,
                "inclusive_keywords": ["career changers welcome", "mentorship", "supportive environment"]
            }
        ]

    def _get_cache_path(self, role: str, location: str = "global") -> Path:
        """Get cache file path for a role and location."""
        return self.cache_dir / f"{role.lower()}_{location.lower().replace(' ', '_')}.json"
        
    def _load_job_data(self, role: str, location: str = "global") -> Optional[Dict]:
        """Load cached job data if fresh."""
        cache_file = self._get_cache_path(role, location)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                # Check if data is less than 6 hours old for job listings
                last_update = datetime.fromisoformat(data['timestamp'])
                age = datetime.now() - last_update
                if age.total_seconds() < 6 * 3600:  # 6 hours for job data
                    return data
            except Exception as e:
                logger.error(f"Error loading job data: {str(e)}")
        return None
        
    def _save_job_data(self, role: str, location: str, data: Dict):
        """Save job data to cache."""
        cache_file = self._get_cache_path(role, location)
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving job data: {str(e)}")
            
    def _fetch_job_data(self, role: str, location: str = "global", experience_level: str = "entry") -> Dict:
        """Fetch real-time job market data using web search."""
        data = {
            'job_listings': [],
            'salary_insights': [],
            'company_insights': [],
            'market_trends': [],
            'remote_opportunities': [],
            'skill_requirements': [],
            'women_friendly_companies': []
        }
        
        # Search queries for different aspects
        location_query = f"in {location}" if location.lower() != "global" else ""
        queries = {
            'job_listings': f"{role} jobs {location_query} {experience_level} level hiring now",
            'salary_insights': f"{role} salary range {location_query} {experience_level} level 2024",
            'company_insights': f"best companies hiring {role} {location_query} company culture",
            'market_trends': f"{role} job market trends growth opportunities {location_query}",
            'remote_opportunities': f"remote {role} jobs {experience_level} level",
            'skill_requirements': f"{role} required skills most in demand {experience_level}",
            'women_friendly_companies': f"women friendly companies hiring {role} diversity inclusion"
        }
        
        # Fetch data for each aspect
        for aspect, query in queries.items():
            results = self.web_search.execute(query)
            data[aspect] = results
            
        return data
        
    def _format_response(self, role: str, data: Dict, location: str, experience_level: str) -> str:
        """Format job search response."""
        response = []
        
        # Introduction
        response.append(f"🎯 Job Opportunities for {role} ({experience_level} level)")
        if location.lower() != "global":
            response.append(f"📍 Location: {location}\n")
        
        # Latest Job Listings
        response.append("💼 Latest Job Openings:")
        for job in data['job_listings'][:5]:
            response.append(f"• {job}")
        
        # Salary Insights
        response.append("\n💰 Salary Insights:")
        for insight in data['salary_insights'][:2]:
            response.append(f"• {insight}")
        
        # Company Insights
        response.append("\n🏢 Top Companies & Culture:")
        for company in data['company_insights'][:3]:
            response.append(f"• {company}")
        
        # Market Trends
        response.append("\n📈 Market Trends:")
        for trend in data['market_trends'][:2]:
            response.append(f"• {trend}")
        
        # Remote Opportunities
        response.append("\n🌐 Remote Opportunities:")
        for remote in data['remote_opportunities'][:3]:
            response.append(f"• {remote}")
        
        # Skill Requirements
        response.append("\n💡 In-Demand Skills:")
        for skill in data['skill_requirements'][:3]:
            response.append(f"• {skill}")
        
        # Women-Friendly Companies
        response.append("\n👩‍💻 Women-Friendly Companies:")
        for company in data['women_friendly_companies'][:3]:
            response.append(f"• {company}")
        
        # Job Search Tips
        response.append("\n✨ Job Search Tips:")
        response.append("1. Tailor your resume for each application")
        response.append("2. Research companies before applying")
        response.append("3. Network with professionals in your field")
        response.append("4. Prepare a strong online presence (LinkedIn, GitHub)")
        response.append("5. Follow up on applications professionally")
        
        return "\n".join(response)

    def _execute(self, query: str) -> str:
        """Execute job search.
        
        Args:
            query: User query about job search
            
        Returns:
            Formatted string containing job search results
        """
        query = query.lower()
        
        # Extract role
        role = None
        if "data scientist" in query or "data science" in query:
            role = "Data Scientist"
        elif "software engineer" in query or "software developer" in query:
            role = "Software Engineer"
        elif "machine learning" in query or "ml engineer" in query:
            role = "Machine Learning Engineer"
        elif "data analyst" in query:
            role = "Data Analyst"
        elif "product manager" in query:
            role = "Product Manager"
        elif "devops" in query:
            role = "DevOps Engineer"
        else:
            role = "Software Engineer"  # default
        
        # Extract location (basic implementation)
        location = "global"
        common_locations = ["us", "uk", "canada", "australia", "india", "remote"]
        for loc in common_locations:
            if loc in query:
                location = loc.title()
                break
        
        # Determine experience level
        experience_level = "entry"
        if "senior" in query or "experienced" in query:
            experience_level = "senior"
        elif "mid" in query or "intermediate" in query:
            experience_level = "mid"
            
        # Try to load cached data
        data = self._load_job_data(role, location)
        
        # If no cache or expired, fetch new data
        if not data:
            data = self._fetch_job_data(role, location, experience_level)
            self._save_job_data(role, location, data)
            
        # Format and return response
        return self._format_response(role, data, location, experience_level)

    def get_response_title(self, query: str) -> str:
        """Override to provide a more specific title."""
        return "Job Search Results"

    # Remove the old execute method since we're now using _execute

    def search_jobs(self,
                   query: str,
                   location: str = "india",
                   remote_only: bool = False,
                   date_posted: str = "month",
                   page: int = 1,
                   num_pages: int = 1) -> Dict[str, Any]:
        """
        Search for jobs based on the provided parameters.

        Args:
            query: Job title, skills, or keywords
            location: Location for the job search (default: india)
            remote_only: Whether to search for remote jobs only
            date_posted: Timeframe for job posting (all, today, 3days, week, month)
            page: Page number for pagination
            num_pages: Number of pages to return

        Returns:
            Dict containing job search results
        """
        search_query = f"{query} jobs in {location}"
        if remote_only:
            search_query += " remote"
        params = {
            "query": search_query,
            "page": page,
            "num_pages": num_pages,
            "date_posted": date_posted,
            "country": "in",
            "language": "en"
        }

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            if "data" in data:
                analyzed_jobs = self._analyze_women_friendly_jobs(data["data"])
                data["data"] = analyzed_jobs

            return data

        except requests.exceptions.RequestException as e:
            return {"error": f"API Request failed: {str(e)}"}
        except json.JSONDecodeError:
            return {"error": "Failed to parse API response"}

    def _analyze_women_friendly_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Analyze jobs based on multiple women-friendly parameters.

        Args:
            jobs: List of job listings from the API

        Returns:
            Analyzed and scored list of jobs
        """
        scored_jobs = []
        parameters = {
            "inclusive_policy": {
                "keywords": ["diversity", "inclusion", "inclusive", "equal opportunity",
                           "gender equality", "gender diversity", "women in tech", "female leadership"],
                "weight": 5.0,
                "description": "Company mentions diversity and inclusion policies"
            },
            "flexible_work": {
                "keywords": ["flexible hours", "flexible schedule", "work-life balance",
                           "remote work", "hybrid work", "work from home"],
                "weight": 1.5,
                "description": "Offers flexible working arrangements"
            },
            "parental_benefits": {
                "keywords": ["maternity leave", "paternity leave", "parental leave",
                           "childcare", "family benefits", "baby care"],
                "weight": 0.5,
                "description": "Provides parental benefits and support"
            },
            "career_growth": {
                "keywords": ["mentorship", "career development", "growth opportunities",
                           "professional development", "training programs", "leadership development"],
                "weight": 1.5,
                "description": "Focuses on career growth and development"
            },
            "supportive_culture": {
                "keywords": ["supportive", "collaborative", "team-oriented",
                           "employee wellbeing", "work culture", "positive environment"],
                "weight": 0.5,
                "description": "Promotes a supportive work culture"
            },
            "women_representation": {
                "keywords": ["women leadership", "female leaders", "women in management",
                           "women-led", "female founder", "women executives"],
                "weight": 1.0,
                "description": "Has women in leadership positions"
            }
        }

        for job in jobs:
            job_text = f"{job.get('job_title', '')} {job.get('job_description', '')} {job.get('employer_name', '')}"
            job_text = job_text.lower()
            women_friendly_aspects = []
            total_score = 0
            matched_parameters = {}
            
            for param_name, param_data in parameters.items():
                param_score = 0
                matches = []

                for keyword in param_data["keywords"]:
                    keyword_pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(keyword_pattern, job_text):
                        param_score += param_data["weight"]
                        matches.append(keyword)

                if param_score > 0:
                    normalized_score = min(param_score, param_data["weight"])
                    total_score += normalized_score
                    women_friendly_aspects.append(param_data["description"])
                    matched_parameters[param_name] = {
                        "score": normalized_score,
                        "max_score": param_data["weight"],
                        "matched_keywords": matches
                    }

            max_possible_score = sum(param["weight"] for param in parameters.values())
            women_friendly_score = round((total_score / max_possible_score) * 10, 1)

            job["women_friendly_score"] = women_friendly_score
            job["women_friendly_aspects"] = women_friendly_aspects
            job["women_friendly_analysis"] = matched_parameters

            scored_jobs.append(job)

        return sorted(scored_jobs, key=lambda x: x.get("women_friendly_score", 0), reverse=True)

    def format_job_listings(self, jobs_data: Dict[str, Any], max_results: int = 5) -> str:
        """
        Format job listings for display to the user.

        Args:
            jobs_data: The data returned from search_jobs
            max_results: Maximum number of results to include in the formatted output

        Returns:
            Formatted string with job listings
        """
        if "error" in jobs_data:
            return f"Error searching for jobs: {jobs_data['error']}"

        if not jobs_data.get("data"):
            return "No job listings found matching your criteria."

        formatted_output = f"Found {len(jobs_data['data'])} job listings:\n\n"
        
        for job in jobs_data["data"][:max_results]:
            formatted_output += f"Title: {job.get('job_title', 'N/A')}\n"
            formatted_output += f"Company: {job.get('employer_name', 'N/A')}\n"
            formatted_output += f"Location: {job.get('job_country', 'N/A')}\n"
            formatted_output += f"Women-Friendly Score: {job.get('women_friendly_score', 'N/A')}\n"
            
            if job.get('women_friendly_aspects'):
                formatted_output += "\nWomen-Friendly Aspects:\n"
                for aspect in job.get('women_friendly_aspects', []):
                    formatted_output += f"- ✅ {aspect}\n"

            if job.get('job_apply_link'):
                formatted_output += f"\n🔗 [Apply for this position]({job.get('job_apply_link')})\n"

            if job.get('job_description'):
                desc = job.get('job_description')
                short_desc = desc[:300] + "..." if len(desc) > 300 else desc
                formatted_output += f"\nJob Description Preview\n{short_desc}\n"

            formatted_output += "\n---\n\n"

        return formatted_output