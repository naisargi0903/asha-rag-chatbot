"""Utility for formatting tool responses."""

from typing import Dict, Any, Optional

class ResponseFormatter:
    """Formats tool responses in a conversational way."""
    
    def wrap_response(self, raw_data: Dict[str, Any], tool_name: str, title: str) -> Dict[str, Any]:
        """Wrap raw tool data in a formatted response.
        
        Args:
            raw_data: Raw data from tool execution
            tool_name: Name of the tool that generated the data
            title: Title for the response
            
        Returns:
            Dictionary containing both raw data and formatted response
        """
        formatted_response = self._format_response(raw_data, tool_name, title)
        
        return {
            "raw_data": raw_data,
            "formatted_response": formatted_response
        }
    
    def _format_response(self, data: Dict[str, Any], tool_name: str, title: str) -> str:
        """Format the response in a conversational way.
        
        Args:
            data: Raw data to format
            tool_name: Name of the tool
            title: Title for the response
            
        Returns:
            Formatted response string
        """
        response_parts = [title]
        
        # Format different types of data
        if "learning_resources" in data:
            response_parts.append("\nLearning Resources:")
            for resource in data["learning_resources"][:3]:  # Show top 3
                response_parts.append(f"- {resource['title']}: {resource['description']}")
        
        if "market_trends" in data:
            response_parts.append("\nMarket Trends:")
            for trend in data["market_trends"][:3]:  # Show top 3
                response_parts.append(f"- {trend['title']}: {trend['description']}")
        
        if "success_stories" in data:
            response_parts.append("\nSuccess Stories:")
            for story in data["success_stories"][:3]:  # Show top 3
                response_parts.append(f"- {story['title']}: {story['description']}")
        
        if "career_advice" in data:
            response_parts.append("\nCareer Advice:")
            for advice in data["career_advice"][:3]:  # Show top 3
                response_parts.append(f"- {advice['title']}: {advice['description']}")
        
        # Add a closing message
        response_parts.append("\nWould you like to know more about any of these topics?")
        
        return "\n".join(response_parts)