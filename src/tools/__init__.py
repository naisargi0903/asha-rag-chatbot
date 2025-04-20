"""Tools module for Asha AI."""

from src.tools.tool_registry import get_registry
from src.tools.job_search import JobSearchTool
from src.tools.skill_gap import SkillGapTool
from src.tools.career_path import CareerPathTool
from src.tools.event_recommender import EventRecommenderTool
from src.tools.interview_preparation import InterviewPreparationTool
from src.tools.success_stories import SuccessStoriesTool
from src.tools.women_wellness import WomenWellnessTool
from src.tools.web_scraper import WebScraperTool

# Initialize and register all tools
registry = get_registry()
registry.register(JobSearchTool())
registry.register(SkillGapTool())
registry.register(CareerPathTool())
registry.register(EventRecommenderTool())
registry.register(InterviewPreparationTool())
registry.register(SuccessStoriesTool())
registry.register(WomenWellnessTool())
registry.register(WebScraperTool())

# Export commonly used functions and classes
__all__ = [
    'get_registry',
    'JobSearchTool',
    'SkillGapTool',
    'CareerPathTool',
    'EventRecommenderTool',
    'InterviewPreparationTool',
    'SuccessStoriesTool',
    'WomenWellnessTool',
    'WebScraperTool'
]