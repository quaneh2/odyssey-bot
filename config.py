"""
Configuration file for Ask The Odyssey RAG application.
Loads environment variables and defines application settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')

# Embedding settings
VOYAGE_MODEL = "voyage-3"
EMBEDDING_DIMENSION = 1024

# Chunking settings
CHUNK_SIZE = 800  # tokens
CHUNK_OVERLAP = 100  # tokens

# Retrieval settings
TOP_K_RESULTS = 5

# Claude settings
CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 2000
