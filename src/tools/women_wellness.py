"""Women wellness tool with real-time resources and support."""

from typing import Dict, Any, List, Optional
from src.tools.tool_registry import BaseTool, register_tool
from src.tools.web_search import WebSearchTool
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@register_tool
class WomenWellnessTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="women_wellness",
            description="Provides wellness resources and support for women in tech with real-time data"
        )
        self.web_search = WebSearchTool()
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "wellness"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, category: str) -> Path:
        """Get cache file path for a wellness category."""
        return self.cache_dir / f"{category.lower().replace(' ', '_')}.json"
        
    def _load_wellness_data(self, category: str) -> Optional[Dict]:
        """Load cached wellness data if fresh."""
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
                logger.error(f"Error loading wellness data: {str(e)}")
        return None
        
    def _save_wellness_data(self, category: str, data: Dict):
        """Save wellness data to cache."""
        cache_file = self._get_cache_path(category)
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving wellness data: {str(e)}")
            
    def _fetch_wellness_data(self, category: str) -> Dict:
        """Fetch real-time wellness resources using web search."""
        data = {
            'mental_health': [],
            'work_life_balance': [],
            'physical_wellness': [],
            'support_networks': [],
            'stress_management': [],
            'career_wellness': [],
            'community_resources': []
        }
        
        # Search queries for different aspects
        queries = {
            'mental_health': "mental health resources women in tech stress anxiety support",
            'work_life_balance': "work life balance tips women tech industry",
            'physical_wellness': "physical health wellness tips busy tech professionals",
            'support_networks': "women in tech support groups mentorship networks",
            'stress_management': "stress management techniques women tech workplace",
            'career_wellness': "career wellbeing professional development women tech",
            'community_resources': "women tech communities support resources organizations"
        }
        
        # Fetch data for each aspect
        for aspect, query in queries.items():
            results = self.web_search.execute(query)
            data[aspect] = results
            
        return data
        
    def _format_response(self, category: str, data: Dict) -> str:
        """Format wellness resources response."""
        response = []
        
        # Introduction
        response.append(f"🌸 Wellness Resources & Support for Women in Tech\n")
        
        # Mental Health
        response.append("🧠 Mental Health Support:")
        for resource in data['mental_health'][:3]:
            response.append(f"• {resource}")
        
        # Work-Life Balance
        response.append("\n⚖️ Work-Life Balance Tips:")
        for tip in data['work_life_balance'][:3]:
            response.append(f"• {tip}")
        
        # Physical Wellness
        response.append("\n💪 Physical Wellness:")
        for tip in data['physical_wellness'][:3]:
            response.append(f"• {tip}")
        
        # Support Networks
        response.append("\n🤝 Support Networks:")
        for network in data['support_networks'][:3]:
            response.append(f"• {network}")
        
        # Stress Management
        response.append("\n🌿 Stress Management Techniques:")
        for technique in data['stress_management'][:3]:
            response.append(f"• {technique}")
        
        # Career Wellness
        response.append("\n💼 Career Wellness:")
        for tip in data['career_wellness'][:3]:
            response.append(f"• {tip}")
        
        # Community Resources
        response.append("\n👥 Community Resources:")
        for resource in data['community_resources'][:3]:
            response.append(f"• {resource}")
        
        # Daily Wellness Tips
        response.append("\n✨ Daily Wellness Practices:")
        response.append("1. Take regular breaks during work")
        response.append("2. Practice mindfulness or meditation")
        response.append("3. Maintain boundaries between work and personal life")
        response.append("4. Stay connected with supportive communities")
        response.append("5. Prioritize physical and mental health")
        
        # Emergency Resources
        response.append("\n🆘 Important Resources:")
        response.append("• National Crisis Hotline: 988")
        response.append("• Women's Health Helpline: 1-800-994-9662")
        response.append("• NAMI HelpLine: 1-800-950-NAMI")
        
        return "\n".join(response)
    
    def _execute(self, query: str) -> str:
        """Execute wellness resource search.

        Args:
            query: User query about wellness support

        Returns:
            Curated wellness resources and support
        """
        query = query.lower()
        
        # Determine wellness category
        category = None
        if "mental" in query or "anxiety" in query or "stress" in query:
            category = "Mental Health"
        elif "work life" in query or "balance" in query:
            category = "Work-Life Balance"
        elif "physical" in query or "health" in query or "exercise" in query:
            category = "Physical Wellness"
        elif "support" in query or "community" in query:
            category = "Support Networks"
        elif "career" in query or "professional" in query:
            category = "Career Wellness"
        else:
            category = "General Wellness"  # default
            
        # Try to load cached data
        data = self._load_wellness_data(category)
        
        # If no cache or expired, fetch new data
        if not data:
            data = self._fetch_wellness_data(category)
            self._save_wellness_data(category, data)
            
        # Format and return response
        return self._format_response(category, data) 