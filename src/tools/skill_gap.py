"""Skill gap analysis tool for career development."""

from typing import Dict, Any, List, Optional
from src.tools.tool_registry import BaseTool, register_tool
from src.tools.web_search import WebSearchTool
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@register_tool
class SkillGapTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="skill_gap",
            description="Analyzes skill gaps and provides learning recommendations"
        )
        self.web_search = WebSearchTool()
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "skill_gap"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, role: str) -> Path:
        """Get cache file path for a role."""
        return self.cache_dir / f"{role.lower().replace(' ', '_')}.json"
        
    def _load_skill_data(self, role: str) -> Optional[Dict]:
        """Load cached skill data if fresh."""
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
                logger.error(f"Error loading skill data: {str(e)}")
        return None
        
    def _save_skill_data(self, role: str, data: Dict):
        """Save skill data to cache."""
        cache_file = self._get_cache_path(role)
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving skill data: {str(e)}")
            
    def _fetch_skill_data(self, role: str, current_skills: List[str]) -> Dict:
        """Fetch real-time skill gap data using web search."""
        data = {
            'required_skills': [],
            'emerging_skills': [],
            'learning_resources': [],
            'industry_trends': [],
            'certifications': [],
            'skill_importance': []
        }
        
        # Search queries for different aspects
        queries = {
            'required_skills': f"essential skills required for {role} 2024",
            'emerging_skills': f"emerging technologies trends skills {role} future",
            'learning_resources': f"best resources platforms learn {role} skills",
            'industry_trends': f"industry trends affecting {role} skills demand",
            'certifications': f"most valuable certifications for {role}",
            'skill_importance': f"most in-demand skills {role} job market"
        }
        
        # Fetch data for each aspect
        for aspect, query in queries.items():
            results = self.web_search.execute(query)
            if isinstance(results, list):
                data[aspect] = results
            else:
                logger.warning(f"Unexpected result type from web search: {type(results)}")
                data[aspect] = []
            
        return data
        
    def _format_response(self, role: str, data: Dict, current_skills: List[str]) -> str:
        """Format skill gap analysis response."""
        response = []
        
        # Introduction
        response.append(f"🎯 Skill Gap Analysis for {role}\n")
        
        # Required Skills
        if data['required_skills']:
            response.append("💡 Required Skills:")
            for skill in data['required_skills'][:5]:
                response.append(f"• {skill}")
        else:
            response.append("💡 Required Skills:")
            response.append("• No recent skill requirements found. Please try a different role or check back later.")
        
        # Emerging Skills
        if data['emerging_skills']:
            response.append("\n🚀 Emerging Skills:")
            for skill in data['emerging_skills'][:3]:
                response.append(f"• {skill}")
        else:
            response.append("\n🚀 Emerging Skills:")
            response.append("• No recent emerging skills found. Please try a different role or check back later.")
        
        # Learning Resources
        if data['learning_resources']:
            response.append("\n📚 Learning Resources:")
            for resource in data['learning_resources'][:3]:
                response.append(f"• {resource}")
            else:
            response.append("\n📚 Learning Resources:")
            response.append("• No recent learning resources found. Please try a different role or check back later.")
        
        # Industry Trends
        if data['industry_trends']:
            response.append("\n📈 Industry Trends:")
            for trend in data['industry_trends'][:2]:
                response.append(f"• {trend}")
            else:
            response.append("\n📈 Industry Trends:")
            response.append("• No recent industry trends found. Please try a different role or check back later.")
        
        # Certifications
        if data['certifications']:
            response.append("\n🏆 Recommended Certifications:")
            for cert in data['certifications'][:3]:
                response.append(f"• {cert}")
                else:
            response.append("\n🏆 Recommended Certifications:")
            response.append("• No recent certification recommendations found. Please try a different role or check back later.")
        
        # Skill Importance
        if data['skill_importance']:
            response.append("\n🎯 Skill Importance:")
            for skill in data['skill_importance'][:3]:
                response.append(f"• {skill}")
        else:
            response.append("\n🎯 Skill Importance:")
            response.append("• No recent skill importance data found. Please try a different role or check back later.")
        
        # Next Steps
        response.append("\n✨ Next Steps:")
        response.append("1. Identify which required skills you need to develop")
        response.append("2. Create a learning plan for acquiring new skills")
        response.append("3. Consider relevant certifications to validate your skills")
        response.append("4. Stay updated with industry trends and emerging technologies")
        response.append("5. Practice and apply your skills in real-world projects")
        
        return "\n".join(response)
    
    def _execute(self, query: str) -> str:
        """Execute skill gap analysis.

        Args:
            query: User query about skill gaps

        Returns:
            Skill gap analysis and recommendations
        """
        query = query.lower()
        
        # Extract role and current skills from query
        role = None
        current_skills = []
        
        # Extract role
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
            role = "Tech Professional"  # default
            
        # Extract skills (if mentioned)
        skill_keywords = {
            "python": ["python", "pandas", "numpy"],
            "javascript": ["javascript", "js", "react", "node"],
            "java": ["java", "spring", "j2ee"],
            "cloud": ["aws", "azure", "gcp", "cloud"],
            "database": ["sql", "nosql", "mongodb", "postgresql"],
            "devops": ["docker", "kubernetes", "ci/cd", "jenkins"]
        }
        
        for skill_type, keywords in skill_keywords.items():
            if any(keyword in query for keyword in keywords):
                current_skills.append(skill_type)

        # Try to load cached data
        data = self._load_skill_data(role)
        
        # If no cache or expired, fetch new data
        if not data:
            data = self._fetch_skill_data(role, current_skills)
            self._save_skill_data(role, data)
            
        # Format and return response
        return self._format_response(role, data, current_skills)