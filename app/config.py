import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL") 
QDRANT_URL = os.getenv("QDRANT_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")