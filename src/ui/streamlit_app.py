"""Streamlit interface for Asha AI."""

import os
import sys
from pathlib import Path
import logging

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import streamlit as st
from src.agent.orchestrator import Orchestrator
from src.config import KNOWLEDGE_BASE_PATH

import json
import time
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_query_with_retry(orchestrator, prompt: str, max_attempts: int = 2) -> str:
    """Process query with retry logic and token management.
    
    Args:
        orchestrator: The orchestrator instance
        prompt: User's prompt
        max_attempts: Maximum number of retry attempts
        
    Returns:
        Formatted response string
    """
    attempt = 0
    last_error = None
    
    while attempt < max_attempts:
        try:
            # Process query without token management (handled by LLM)
            response = orchestrator.process_query(prompt)
            return format_response(response)
            
        except Exception as e:
            last_error = str(e)
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            
            # If it's a token length error, we can't retry since token management 
            # is handled by the LLM class
            if "max_length" in str(e).lower() or "token" in str(e).lower():
                break
                
        attempt += 1
    
    # If all attempts failed, return error message
    error_message = "I apologize, but I encountered an error while processing your request. "
    if "max_length" in str(last_error).lower() or "token" in str(last_error).lower():
        error_message += "Your question might be too long. Please try asking a shorter question."
    else:
        error_message += "Please try rephrasing your question or try again later."
    return error_message

def initialize_session_state():
    """Initialize session state variables."""
    if 'orchestrator' not in st.session_state:
        try:
            # Ensure knowledge base directory exists
            knowledge_base_dir = Path(KNOWLEDGE_BASE_PATH)
            knowledge_base_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize orchestrator
            st.session_state.orchestrator = Orchestrator(KNOWLEDGE_BASE_PATH)
            logger.info("Successfully initialized orchestrator")
        except Exception as e:
            logger.error(f"Error initializing orchestrator: {str(e)}")
            st.error("Failed to initialize the AI system. Please try refreshing the page.")

def format_response(response):
    """Format the response for display."""
    if isinstance(response, dict):
        formatted = []
        for key, value in response.items():
            if isinstance(value, list):
                formatted.append(f"**{key}:**")
                for item in value:
                    formatted.append(f"- {item}")
            else:
                formatted.append(f"**{key}:** {value}")
        return "\n\n".join(formatted)
    return str(response)

def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Asha AI Career Assistant",
        page_icon="👩‍💻",
        layout="wide"
    )
    
    st.title("👩‍💻 Asha AI Career Assistant")
    st.markdown("""
    Welcome to Asha AI! I'm here to help you with your career journey. 
    Ask me about career paths, skills development, job opportunities, or any career-related questions.
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # Create two columns for chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat history
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User input
        if prompt := st.chat_input("What would you like to know?"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process query with retry logic
            with st.spinner("Thinking..."):
                response = process_query_with_retry(st.session_state.orchestrator, prompt)
            
            # Display response
            with st.chat_message("assistant"):
                if "error" in response.lower():
                    st.error(response)
                else:
                    st.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
    
    with col2:
        st.markdown("### Quick Tips")
        st.markdown("""
        - Ask about career paths in tech
        - Get skill development advice
        - Learn about job opportunities
        - Get career transition guidance
        - Find women-friendly workplaces
        """)
        
        st.markdown("### About Asha AI")
        st.markdown("""
        Asha AI is designed to support women in tech by providing:
        - Career guidance
        - Skill recommendations
        - Job search assistance
        - Success stories
        - Wellness resources
        """)

if __name__ == "__main__":
    main()