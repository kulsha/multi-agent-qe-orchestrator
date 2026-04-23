# config/llm_config.py
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

load_dotenv()

# ── Model capability definitions ──────────────────────────────
# AutoGen 0.7.x requires explicit model_info for non-OpenAI models.
# This tells AutoGen what the model supports — context window,
# whether it supports vision, function calling, JSON output etc.

GROQ_MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=True,
    json_output=True,
    family="unknown",
    context_window=8192,
    structured_output=False,
)

GROQ_MIXTRAL_INFO = ModelInfo(
    vision=False,
    function_calling=True,
    json_output=True,
    family="unknown",
    context_window=32768,
    structured_output=False,
)

# ── Provider configs ───────────────────────────────────────────

PROVIDERS = {
    "groq": {
        "model":      "llama-3.3-70b-versatile",
        "api_key":    os.getenv("GROQ_API_KEY"),
        "base_url":   "https://api.groq.com/openai/v1",
        "model_info": GROQ_MODEL_INFO,
    },
    "groq_fast": {
    "model":      "llama-3.1-8b-instant",
    "api_key":    os.getenv("GROQ_API_KEY"),
    "base_url":   "https://api.groq.com/openai/v1",
    "model_info": ModelInfo(
        vision=False,
        function_calling=True,
        json_output=True,
        family="unknown",
        context_window=8192,
        structured_output=False,
    ),
},
    "groq_code": {
        "model":      "mixtral-8x7b-32768",
        "api_key":    os.getenv("GROQ_API_KEY"),
        "base_url":   "https://api.groq.com/openai/v1",
        "model_info": GROQ_MIXTRAL_INFO,
    },
    "openai": {
        "model":   "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
        # No model_info needed — OpenAI models are natively known
    },
    "gemini": {
        "model":      "gemini-2.0-flash",
        "api_key":    os.getenv("GEMINI_API_KEY"),
        "base_url":   "https://generativelanguage.googleapis.com/v1beta/openai/",
        "model_info": ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family="unknown",
        context_window=1048576,
        structured_output=False,
    ),
},
    "ollama": {
        "model":      "mistral",
        "api_key":    "ollama",
        "base_url":   "http://localhost:11434/v1",
        "model_info": ModelInfo(
            vision=False,
            function_calling=False,
            json_output=True,
            family="unknown",
            context_window=8192,
            structured_output=False,
        ),
    },
}


def get_client(provider: str = "groq") -> OpenAIChatCompletionClient:
    """
    Returns an OpenAIChatCompletionClient for the given provider.
    Defaults to Groq if provider not found.

    Usage:
        from config.llm_config import get_client
        client = get_client(provider='groq')
        client = get_client(provider='openai')
        client = get_client(provider='ollama')
    """
    cfg = PROVIDERS.get(provider, PROVIDERS["groq"])
    return OpenAIChatCompletionClient(**cfg)