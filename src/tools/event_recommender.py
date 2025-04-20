"""Event recommender tool with real-time tech event data integration."""

from typing import Dict, Any, List, Optional
from src.tools.tool_registry import BaseTool, register_tool
from src.tools.web_search import WebSearchTool
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@register_tool
class EventRecommenderTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="event_recommender",
            description="Recommends tech events, conferences, and networking opportunities with real-time data"
        )
        self.web_search = WebSearchTool()
        self.cache_dir = Path.home() / ".cache" / "asha_ai" / "events"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_cache_path(self, category: str, location: str = "global") -> Path:
        """Get cache file path for an event category and location."""
        return self.cache_dir / f"{category.lower()}_{location.lower().replace(' ', '_')}.json"
        
    def _load_event_data(self, category: str, location: str = "global") -> Optional[Dict]:
        """Load cached event data if fresh."""
        cache_file = self._get_cache_path(category, location)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                # Check if data is less than 12 hours old for events
                last_update = datetime.fromisoformat(data['timestamp'])
                age = datetime.now() - last_update
                if age.total_seconds() < 12 * 3600:  # 12 hours for event data
                    return data
            except Exception as e:
                logger.error(f"Error loading event data: {str(e)}")
        return None
        
    def _save_event_data(self, category: str, location: str, data: Dict):
        """Save event data to cache."""
        cache_file = self._get_cache_path(category, location)
        try:
            data['timestamp'] = datetime.now().isoformat()
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Error saving event data: {str(e)}")
            
    def _fetch_event_data(self, category: str, location: str = "global") -> Dict:
        """Fetch real-time event data using web search."""
        data = {
            'upcoming_events': [],
            'conferences': [],
            'workshops': [],
            'networking_events': [],
            'hackathons': [],
            'women_tech_events': [],
            'virtual_events': []
        }
        
        # Search queries for different aspects
        location_query = f"in {location}" if location.lower() != "global" else ""
        year = datetime.now().year
        queries = {
            'upcoming_events': f"upcoming {category} events {location_query} {year}",
            'conferences': f"{category} conferences {location_query} {year}",
            'workshops': f"{category} workshops training sessions {location_query}",
            'networking_events': f"{category} networking meetups {location_query}",
            'hackathons': f"{category} hackathons coding competitions {location_query}",
            'women_tech_events': f"women in tech events {category} {location_query}",
            'virtual_events': f"virtual online {category} events webinars {year}"
        }
        
        # Fetch data for each aspect
        for aspect, query in queries.items():
            results = self.web_search.execute(query)
            data[aspect] = results

            return data

    def _format_response(self, category: str, data: Dict, location: str) -> str:
        """Format event recommendations response."""
        response = []
        
        # Introduction
        if location.lower() != "global":
            response.append(f"🎯 Tech Events & Opportunities in {location} - {category}\n")
        else:
            response.append(f"🎯 Global Tech Events & Opportunities - {category}\n")
        
        # Upcoming Events
        response.append("📅 Upcoming Events:")
        for event in data['upcoming_events'][:3]:
            response.append(f"• {event}")
        
        # Conferences
        response.append("\n🎤 Notable Conferences:")
        for conf in data['conferences'][:3]:
            response.append(f"• {conf}")
        
        # Workshops
        response.append("\n📚 Workshops & Training:")
        for workshop in data['workshops'][:3]:
            response.append(f"• {workshop}")
        
        # Networking Events
        response.append("\n🤝 Networking Opportunities:")
        for event in data['networking_events'][:2]:
            response.append(f"• {event}")
        
        # Hackathons
        response.append("\n💻 Hackathons & Competitions:")
        for hackathon in data['hackathons'][:2]:
            response.append(f"• {hackathon}")
        
        # Women in Tech Events
        response.append("\n👩‍💻 Women in Tech Events:")
        for event in data['women_tech_events'][:2]:
            response.append(f"• {event}")
        
        # Virtual Events
        response.append("\n🌐 Virtual Events & Webinars:")
        for event in data['virtual_events'][:2]:
            response.append(f"• {event}")
        
        # Event Participation Tips
        response.append("\n✨ Event Participation Tips:")
        response.append("1. Register early for popular events")
        response.append("2. Prepare questions for speakers")
        response.append("3. Update your LinkedIn and business cards")
        response.append("4. Research attendees and companies")
        response.append("5. Follow up with new connections")
        
        return "\n".join(response)
    
    def _execute(self, query: str) -> str:
        """Execute event recommendation.

        Args:
            query: User query about tech events

        Returns:
            Curated event recommendations
        """
        query = query.lower()
        
        # Determine category
        category = None
        if "data science" in query or "machine learning" in query:
            category = "Data Science & AI"
        elif "web" in query or "frontend" in query or "backend" in query:
            category = "Web Development"
        elif "cloud" in query or "devops" in query:
            category = "Cloud & DevOps"
        elif "cybersecurity" in query or "security" in query:
            category = "Cybersecurity"
        elif "product" in query or "ux" in query:
            category = "Product & Design"
        elif "blockchain" in query or "crypto" in query:
            category = "Blockchain"
        else:
            category = "Technology"  # default
            
        # Extract location (basic implementation)
        location = "global"
        common_locations = ["us", "uk", "canada", "australia", "india", "europe", "asia"]
        for loc in common_locations:
            if loc in query:
                location = loc.title()
                    break

        # Try to load cached data
        data = self._load_event_data(category, location)
        
        # If no cache or expired, fetch new data
        if not data:
            data = self._fetch_event_data(category, location)
            self._save_event_data(category, location, data)
            
        # Format and return response
        return self._format_response(category, data, location) 