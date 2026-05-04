import os
from dotenv import load_dotenv

load_dotenv()

provider = os.getenv('INFERENCE_MODE') or os.getenv('LLM_PROVIDER') or 'local'
provider = provider.strip().lower()
if provider == 'ollama':
    provider = 'local'

INFERENCE_MODE = provider
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL') or os.getenv('OLLAMA_URL') or 'http://localhost:11434'
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:0.6b')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '150'))
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.3'))
CORS_ORIGINS = [origin.strip() for origin in os.getenv('CORS_ORIGINS', '*').split(',')]
