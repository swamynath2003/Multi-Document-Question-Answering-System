# Configuration file for API keys and constants

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys - Configure these directly in the code or via environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyC3Pw3KxmnBm4HxRTeuPRXQektKO8TwwXE")

# User information 
CURRENT_USER = os.getenv("USER", "shivasaijuluri")

# Model configuration
DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"