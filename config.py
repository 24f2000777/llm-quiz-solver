"""Centralized configuration for the quiz solver."""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Environment variables
EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Validation
if not all([EMAIL, SECRET, GOOGLE_API_KEY]):
    raise ValueError("Missing required environment variables: EMAIL, SECRET, or GOOGLE_API_KEY")

# Agent settings
RECURSION_LIMIT = 200  # Max steps for quiz chain
AGENT_TIMEOUT = 600  # 10 minutes max per quiz chain
LLM_RATE_LIMIT = 9 / 60  # 9 requests per minute for Gemini

# File settings
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)
