"""Configuration settings for Asha AI."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"
VECTOR_DB_PATH = DATA_DIR / "vector_db"

# Export knowledge base path
KNOWLEDGE_BASE_PATH = str(KNOWLEDGE_BASE_DIR)

# Model settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt2")

# RAG settings
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 5

# Agent settings
MAX_ITERATIONS = 5
TEMPERATURE = 0.7