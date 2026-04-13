# config/llm_config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Primary model — best for reasoning, test case design, review
llama3_config = {
    "config_list": [{
        "model": "llama3-70b-8192",
        "api_key": GROQ_API_KEY,
        "base_url": "https://api.groq.com/openai/v1",
        "api_type": "openai"
    }],
    "temperature": 0.3,
}

# Secondary model — better for longer code generation
mixtral_config = {
    "config_list": [{
        "model": "mixtral-8x7b-32768",
        "api_key": GROQ_API_KEY,
        "base_url": "https://api.groq.com/openai/v1",
        "api_type": "openai"
    }],
    "temperature": 0.2,
}