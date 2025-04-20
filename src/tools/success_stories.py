"""Success stories tool with real-time inspiration and insights."""

from typing import Dict, Any, List, Optional
from src.tools.tool_registry import BaseTool, register_tool
from src.tools.web_search import WebSearchTool
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@register_tool
class SuccessStoriesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="success_stories",
            description="Provides inspiring success stories and career transition insights with real-time data"
        )
        self.web_search = WebSearchTool()
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "success_stories"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, category: str) -> Path:
        """Get cache file path for a category."""
        return self.cache_dir / f"{category.lower().replace(' ', '_')}.json"
        
    def _load_story_data(self, category: str) -> Optional[Dict]:
        """Load cached story data if fresh."""
        cache_file = self._get_cache_path(category)
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
                logger.error(f"Error loading story data: {str(e)}")
        return None
        
    def _save_story_data(self, category: str, data: Dict):
        """Save story data to cache."""
        cache_file = self._get_cache_path(category)
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving story data: {str(e)}")
            
    def _fetch_story_data(self, category: str, background: str = "") -> Dict:
        """Fetch real-time success stories and insights using web search."""
        data = {
            'success_stories': [],
            'career_transitions': [],
            'learning_paths': [],
            'challenges_overcome': [],
            'advice': [],
            'industry_insights': []
        }
        
        # Search queries for different aspects
        queries = {
            'success_stories': f"inspiring success stories {category} career women in tech",
            'career_transitions': f"career transition success stories {background} to {category}",
            'learning_paths': f"how successful {category} learned skills career path",
            'challenges_overcome': f"challenges overcome women in tech {category} success",
            'advice': f"career advice tips successful women {category}",
            'industry_insights': f"industry insights {category} career growth opportunities"
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
        
    def _format_response(self, category: str, data: Dict, background: str = "") -> str:
        """Format success stories response."""
        response = []
        
        # Introduction
        if background:
            response.append(f"🌟 Inspiring Success Stories: {background} to {category}\n")
        else:
            response.append(f"🌟 Inspiring Success Stories in {category}\n")
        
        # Success Stories
        if data['success_stories']:
            response.append("💫 Featured Success Stories:")
            for story in data['success_stories'][:2]:
                response.append(f"• {story}")
        else:
            response.append("💫 Featured Success Stories:")
            response.append("• No recent success stories found. Please try a different category or check back later.")
        
        # Career Transitions
        if data['career_transitions']:
            response.append("\n🔄 Career Transition Insights:")
            for transition in data['career_transitions'][:2]:
                response.append(f"• {transition}")
        else:
            response.append("\n🔄 Career Transition Insights:")
            response.append("• No recent career transition stories found. Please try a different category or check back later.")
        
        # Learning Paths
        if data['learning_paths']:
            response.append("\n📚 Learning Paths Taken:")
            for path in data['learning_paths'][:2]:
                response.append(f"• {path}")
        else:
            response.append("\n📚 Learning Paths Taken:")
            response.append("• No recent learning path information found. Please try a different category or check back later.")
        
        # Challenges Overcome
        if data['challenges_overcome']:
            response.append("\n💪 Challenges Overcome:")
            for challenge in data['challenges_overcome'][:2]:
                response.append(f"• {challenge}")
        else:
            response.append("\n💪 Challenges Overcome:")
            response.append("• No recent challenge stories found. Please try a different category or check back later.")
        
        # Advice
        if data['advice']:
            response.append("\n💡 Key Advice from Successful Professionals:")
            for advice in data['advice'][:3]:
                response.append(f"• {advice}")
        else:
            response.append("\n💡 Key Advice from Successful Professionals:")
            response.append("• No recent advice found. Please try a different category or check back later.")
        
        # Industry Insights
        if data['industry_insights']:
            response.append("\n🌐 Industry Insights:")
            for insight in data['industry_insights'][:2]:
                response.append(f"• {insight}")
        else:
            response.append("\n🌐 Industry Insights:")
            response.append("• No recent industry insights found. Please try a different category or check back later.")
        
        # Key Takeaways
        response.append("\n✨ Key Takeaways:")
        response.append("1. Continuous learning is essential for success")
        response.append("2. Network and build relationships in the industry")
        response.append("3. Don't be afraid to take on challenging projects")
        response.append("4. Find mentors and support systems")
        response.append("5. Share your journey to inspire others")
        
        return "\n".join(response)
    
    def _execute(self, query: str) -> str:
        """Execute success stories search.

        Args:
            query: User query about success stories

        Returns:
            Curated success stories and insights
        """
        query = query.lower()
        
        # Determine category and background
        category = None
        background = None
        
        # Extract category
        if "data scientist" in query or "data science" in query:
            category = "Data Science"
        elif "software engineer" in query or "software developer" in query:
            category = "Software Engineering"
        elif "machine learning" in query or "ml engineer" in query:
            category = "Machine Learning"
        elif "data analyst" in query:
            category = "Data Analytics"
        elif "product manager" in query:
            category = "Product Management"
        elif "devops" in query:
            category = "DevOps"
        else:
            category = "Tech"  # default
            
        # Extract background (if mentioned)
        background_keywords = {
            "non-tech": ["non-tech", "non technical", "different field"],
            "student": ["student", "graduate", "university"],
            "self-taught": ["self taught", "self-taught", "bootcamp"],
            "career-switch": ["switch", "transition", "change career"]
        }
        
        for bg_type, keywords in background_keywords.items():
            if any(keyword in query for keyword in keywords):
                background = bg_type
                break

        # Try to load cached data
        data = self._load_story_data(category)
        
        # If no cache or expired, fetch new data
        if not data:
            data = self._fetch_story_data(category, background)
            self._save_story_data(category, data)
            
        # Format and return response
        return self._format_response(category, data, background) 