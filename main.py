"""Main entry point for Asha AI."""

import os
import sys
import argparse
import logging
from typing import Optional
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import required components
from src.agent.knowledge_base import KnowledgeBase
from src.agent.orchestrator import Orchestrator
from src.tools.tool_registry import ToolRegistry

# Import tools to ensure they are registered
from src.tools.career_path import CareerPathTool
from src.tools.skill_gap import SkillGapTool
from src.tools.success_stories import SuccessStoriesTool
from src.tools.job_search import JobSearchTool
from src.tools.interview_preparation import InterviewPreparationTool
from src.tools.event_recommender import EventRecommenderTool
from src.tools.web_search import WebSearchTool
from src.tools.web_scraper import WebScraperTool
from src.tools.women_wellness import WomenWellnessTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asha_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_environment() -> None:
    """Set up the environment variables and paths."""
    try:
        # Add src directory to Python path
        src_path = str(Path(__file__).parent / 'src')
        if src_path not in sys.path:
            sys.path.append(src_path)
        
        # Create necessary directories
        data_dir = Path(__file__).parent / 'data'
        data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories with exist_ok=True
        kb_dir = data_dir / 'knowledge_base'
        kb_dir.mkdir(exist_ok=True)
        
        vector_db_dir = data_dir / 'vector_db'
        vector_db_dir.mkdir(exist_ok=True)
        
        cache_dir = data_dir / 'cache'
        cache_dir.mkdir(exist_ok=True)
        
        # Set environment variables for open-source models
        os.environ['MODEL_TYPE'] = 'open_source'  # Use open-source models
        os.environ['EMBEDDING_MODEL'] = 'all-MiniLM-L6-v2'  # Free sentence transformer model
        os.environ['LLM_MODEL'] = 'gpt2'  # Free base model (can be changed to other open-source models)
        
        # Set knowledge base path
        os.environ['KNOWLEDGE_BASE_PATH'] = str(kb_dir)
        os.environ['VECTOR_DB_PATH'] = str(vector_db_dir)
        os.environ['CACHE_DIR'] = str(cache_dir)
        
        logger.info("Environment setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up environment: {str(e)}")
        raise

def run_ui_mode() -> None:
    """Run the application in UI mode using Streamlit."""
    try:
        logger.info("Starting Streamlit UI...")
        # Check if streamlit is installed
        try:
            import streamlit
        except ImportError:
            logger.error("Streamlit not found. Please install it with: pip install streamlit")
            print("Error: Streamlit not found. Please install it with: pip install streamlit")
            sys.exit(1)
            
        os.system("streamlit run src/ui/streamlit_app.py")
    except Exception as e:
        logger.error(f"Error starting Streamlit UI: {str(e)}")
        sys.exit(1)

def run_cli_mode() -> None:
    """Run the application in CLI mode."""
    try:
        # Initialize components
        knowledge_base = KnowledgeBase()
        tool_registry = ToolRegistry()
        orchestrator = Orchestrator(tool_registry, knowledge_base)
        
        logger.info("Starting Asha AI in CLI mode...")
        print("\n" + "="*50)
        print("Asha AI - Your Career Assistant (Open Source Version)")
        print("="*50)
        print("\nType 'help' for available commands or 'exit' to quit.")
        
        # Print available tools
        tools = tool_registry.get_all_tools()
        print("\nAvailable tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        
        print("\nAsha AI: Hi! I'm Asha AI, your open-source career assistant. How can I help you today?")
        
        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nAsha AI: Goodbye! Have a great day.")
                    sys.exit(0)
                elif user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("- help: Show this help message")
                    print("- tools: List available tools")
                    print("- exit/quit/bye: Exit the program")
                    print("- clear: Clear the screen")
                    print("- debug: Toggle debug mode")
                    continue
                elif user_input.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                elif user_input.lower() == 'tools':
                    print("\nAvailable tools:")
                    for tool in tools:
                        print(f"- {tool.name}: {tool.description}")
                    continue
                elif user_input.lower() == 'debug':
                    current_level = logging.getLogger().getEffectiveLevel()
                    new_level = logging.DEBUG if current_level != logging.DEBUG else logging.INFO
                    logging.getLogger().setLevel(new_level)
                    print(f"\nDebug mode {'enabled' if new_level == logging.DEBUG else 'disabled'}")
                    continue
                
                # Process query
                response = orchestrator.process_query(user_input)
                print(f"\nAsha AI: {response}")
                
            except KeyboardInterrupt:
                print("\n\nAsha AI: Goodbye! Have a great day.")
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error processing query: {str(e)}")
                print(f"\nAsha AI: I'm sorry, I encountered an error. Please try again.")
                print("If the problem persists, check the log file for details.")
    
    except ImportError as e:
        logger.error(f"Error importing required modules: {str(e)}")
        print("Error: Required modules not found. Please check your installation.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error in CLI mode: {str(e)}")
        print("An unexpected error occurred. Please check the log file for details.")
        sys.exit(1)

def main() -> None:
    """Main entry point for the Asha AI application."""
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Asha AI - Open Source Agentic RAG Chatbot')
        parser.add_argument('--mode', type=str, default='ui', choices=['ui', 'cli'],
                          help='Run mode: ui (Streamlit UI) or cli (Command Line Interface)')
        parser.add_argument('--debug', action='store_true',
                          help='Enable debug logging')
        parser.add_argument('--model', type=str,
                          help='Specify the LLM model to use (e.g., gpt2, gpt2-medium)')
        args = parser.parse_args()
        
        # Set up environment
        setup_environment()
        
        # Override model if specified
        if args.model:
            os.environ['LLM_MODEL'] = args.model
            logger.info(f"Using custom LLM model: {args.model}")
        
        # Set debug logging if requested
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        
        # Run in selected mode
        if args.mode == 'ui':
            run_ui_mode()
        else:
            run_cli_mode()
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        print("A fatal error occurred. Please check the log file for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()