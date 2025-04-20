"""Base class for all tools."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from .utils.response_formatter import ResponseFormatter

class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str):
        """Initialize the tool.
        
        Args:
            name: Name of the tool
            description: Description of what the tool does
        """
        self.name = name
        self.description = description
        self.formatter = ResponseFormatter()
    
    @abstractmethod
    def _execute(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool's core functionality.
        
        Args:
            query: User query
            **kwargs: Additional tool-specific parameters
            
        Returns:
            Raw tool execution results
        """
        pass

    def execute(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool and format the response.
        
        Args:
            query: User query
            **kwargs: Additional tool-specific parameters
            
        Returns:
            Dictionary containing both raw data and formatted conversational response
        """
        # Get raw results from tool execution
        raw_results = self._execute(query, **kwargs)
        
        # Format results in a conversational way
        return self.formatter.wrap_response(
            raw_data=raw_results,
            tool_name=self.name,
            title=self.get_response_title(query)
        )
    
    def get_response_title(self, query: str) -> str:
        """Get an appropriate title for the response based on the query.
        
        Args:
            query: User query
            
        Returns:
            Title string for the response
        """
        return f"Here's what I found about {query[:50]}..." if len(query) > 50 else f"Here's what I found about {query}"