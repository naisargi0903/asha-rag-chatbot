"""Tool registry for managing available tools."""

import logging
from typing import Dict, Type, Any
from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """Registry for managing available tools."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the tool registry."""
        if not hasattr(self, 'tools'):
            self.tools: Dict[str, BaseTool] = {}
            self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available tools."""
        try:
            # Import tools here to avoid circular imports
            from .career_path import CareerPathTool
            from .skill_gap import SkillGapTool
            from .success_stories import SuccessStoriesTool
            from .job_search import JobSearchTool
            from .interview_preparation import InterviewPreparationTool
            from .event_recommender import EventRecommenderTool
            from .web_search import WebSearchTool
            from .web_scraper import WebScraperTool
            from .women_wellness import WomenWellnessTool
            
            # Register tools
            self.register(CareerPathTool())
            self.register(SkillGapTool())
            self.register(SuccessStoriesTool())
            self.register(JobSearchTool())
            self.register(InterviewPreparationTool())
            self.register(EventRecommenderTool())
            self.register(WebSearchTool())
            self.register(WebScraperTool())
            self.register(WomenWellnessTool())
            
            logger.info(f"Initialized {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Error initializing tools: {str(e)}")
    
    def register(self, tool: BaseTool):
        """Register a new tool.
        
        Args:
            tool: Tool to register
        """
        try:
            if not isinstance(tool, BaseTool):
                raise ValueError(f"Tool must be an instance of BaseTool, got {type(tool)}")
            
            if tool.name in self.tools:
                logger.warning(f"Tool {tool.name} already registered, overwriting")
            
            self.tools[tool.name] = tool
            logger.debug(f"Registered tool: {tool.name}")
            
        except Exception as e:
            logger.error(f"Error registering tool: {str(e)}")
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool instance
        """
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all registered tools.
        
        Returns:
            Dictionary of tool names to tool instances
        """
        return self.tools.copy()

def get_registry() -> ToolRegistry:
    """Get the tool registry instance.
    
    Returns:
        Tool registry instance
    """
    return ToolRegistry()

def register_tool(tool_class: Type[BaseTool]):
    """Decorator for registering tools.
    
    Args:
        tool_class: Tool class to register
    """
    def decorator(cls):
        tool_instance = cls()
        get_registry().register(tool_instance)
        return cls
    return decorator

# Export the registry and related classes/functions
__all__ = ['BaseTool', 'ToolRegistry', 'get_registry', 'register_tool']