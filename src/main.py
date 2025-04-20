import os
import logging
from dotenv import load_dotenv
from src.utils.logger import logger
from src.registry.tool_registry import ToolRegistry
from src.knowledge_base.knowledge_base import KnowledgeBase
from src.orchestrator.orchestrator import Orchestrator

def setup_environment():
    """Set up the application environment."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Create necessary directories
        os.makedirs(os.getenv('KNOWLEDGE_BASE_PATH', 'data'), exist_ok=True)
        os.makedirs(os.getenv('VECTOR_DB_PATH', 'data/vector_db'), exist_ok=True)
        os.makedirs(os.getenv('CACHE_DIR', 'data/cache'), exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO if not os.getenv('DEBUG') else logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info("Environment setup completed successfully")
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        raise

def initialize_components():
    """Initialize application components."""
    try:
        # Initialize tool registry
        tool_registry = ToolRegistry()
        
        # Initialize knowledge base
        knowledge_base = KnowledgeBase()
        
        # Initialize orchestrator
        orchestrator = Orchestrator(tool_registry, knowledge_base)
        
        logger.info("Components initialized successfully")
        return orchestrator
    except Exception as e:
        logger.error(f"Error initializing components: {str(e)}")
        raise 