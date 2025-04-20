"""Interview preparation tool with real-time data integration."""

from typing import Dict, Any, List, Optional
from src.tools.tool_registry import BaseTool, register_tool
from src.tools.web_search import WebSearchTool
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@register_tool
class InterviewPreparationTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="interview_prep",
            description="Provides personalized interview preparation with real-time data"
        )
        self.web_search = WebSearchTool()
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "interview_prep"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, role: str) -> Path:
        """Get cache file path for a role."""
        return self.cache_dir / f"{role.lower().replace(' ', '_')}.json"
        
    def _load_prep_data(self, role: str) -> Optional[Dict]:
        """Load cached interview prep data if fresh."""
        cache_file = self._get_cache_path(role)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                # Check if data is less than 24 hours old
                last_update = datetime.fromisoformat(data['timestamp'])
                age = datetime.now() - last_update
                if age.total_seconds() < 24 * 3600:
                    return data
            except Exception as e:
                logger.error(f"Error loading interview prep data: {str(e)}")
        return None
        
    def _save_prep_data(self, role: str, data: Dict):
        """Save interview prep data to cache."""
        cache_file = self._get_cache_path(role)
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving interview prep data: {str(e)}")
            
    def _fetch_interview_data(self, role: str) -> Dict:
        """Fetch real-time interview preparation data using web search."""
        data = {
            'common_questions': [],
            'technical_questions': [],
            'behavioral_questions': [],
            'company_insights': [],
            'interview_tips': [],
            'salary_negotiation': []
        }
        
        # Search queries for different aspects
        queries = {
            'common_questions': f"most common {role} interview questions 2024",
            'technical_questions': f"{role} technical interview questions coding problems",
            'behavioral_questions': f"{role} behavioral interview questions STAR method",
            'company_insights': f"top companies hiring {role} interview process",
            'interview_tips': f"{role} interview tips best practices dos and donts",
            'salary_negotiation': f"{role} salary negotiation tips market range"
        }
        
        # Fetch data for each aspect
        for aspect, query in queries.items():
            results = self.web_search.execute(query)
            data[aspect] = results
            
        return data
        
    def _format_response(self, role: str, data: Dict, experience_level: str = "entry") -> str:
        """Format interview preparation response."""
        response = []
        
        # Introduction
        response.append(f"🎯 Interview Preparation Guide for {role} ({experience_level} level):\n")
        
        # Common Questions
        response.append("📝 Common Interview Questions:")
        for q in data['common_questions'][:3]:
            response.append(f"• {q}")
        
        # Technical Questions
        response.append("\n💻 Technical Questions & Challenges:")
        for q in data['technical_questions'][:3]:
            response.append(f"• {q}")
        
        # Behavioral Questions
        response.append("\n🤝 Behavioral Questions (Use STAR Method):")
        for q in data['behavioral_questions'][:3]:
            response.append(f"• {q}")
        
        # Company Insights
        response.append("\n🏢 Company & Process Insights:")
        for insight in data['company_insights'][:2]:
            response.append(f"• {insight}")
        
        # Interview Tips
        response.append("\n💡 Key Interview Tips:")
        for tip in data['interview_tips'][:3]:
            response.append(f"• {tip}")
        
        # Salary Negotiation
        response.append("\n💰 Salary Negotiation Tips:")
        for tip in data['salary_negotiation'][:2]:
            response.append(f"• {tip}")
        
        # Preparation Checklist
        response.append("\n✅ Pre-Interview Checklist:")
        response.append("1. Research the company thoroughly")
        response.append("2. Review your projects and prepare STAR examples")
        response.append("3. Practice coding problems on platforms like LeetCode")
        response.append("4. Prepare questions to ask the interviewer")
        response.append("5. Test your technical setup for virtual interviews")
        response.append("6. Review the job description and match your experiences")
        
        return "\n".join(response)
    
    def _execute(self, query: str) -> str:
        """Execute interview preparation.

        Args:
            query: User query about interview preparation

        Returns:
            Detailed interview preparation guide
        """
        query = query.lower()
        
        # Determine role
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
        
        # Determine experience level
        experience_level = "entry"
        if "senior" in query or "experienced" in query:
            experience_level = "senior"
        elif "mid" in query or "intermediate" in query:
            experience_level = "mid"
            
        # Try to load cached data
        data = self._load_prep_data(role)
        
        # If no cache or expired, fetch new data
        if not data:
            data = self._fetch_interview_data(role)
            self._save_prep_data(role, data)
            
        # Format and return response
        return self._format_response(role, data, experience_level) 