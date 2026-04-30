# config/llm_config.py
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

load_dotenv()

# ── Model capability definitions ──────────────────────────────

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

OLLAMA_MODEL_INFO = ModelInfo(
    vision=False,
    function_calling=False,
    json_output=True,
    family="unknown",
    context_window=8192,
    structured_output=False,
)

CLAUDE_MODEL_INFO = ModelInfo(
    vision=True,
    function_calling=True,
    json_output=True,
    family="unknown",
    context_window=200000,
    structured_output=False,
)

# ── Provider configs (OpenAI-compatible) ───────────────────────

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
        "model_info": GROQ_MODEL_INFO,
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
        "model_info": OLLAMA_MODEL_INFO,
    },
}


def get_client(provider: str = "groq"):
    """
    Returns the right LLM client for the given provider.
    Claude uses its own native Anthropic client.
    All others use OpenAIChatCompletionClient.

    Usage:
        from config.llm_config import get_client
        client = get_client(provider='groq')
        client = get_client(provider='claude')
        client = get_client(provider='ollama')
    """
    if provider == "claude":
        return _get_claude_client()

    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Available: {list(PROVIDERS.keys()) + ['claude']}"
        )

    cfg = PROVIDERS[provider]
    print(
        f"  [llm_config] {provider} → "
        f"{cfg['model']} @ "
        f"{cfg.get('base_url', 'api.openai.com')}"
    )
    return OpenAIChatCompletionClient(**cfg)


def _get_claude_client():
    """
    Returns a native Anthropic client for Claude Haiku.
    Requires: pip install anthropic
    """
    try:
        from autogen_ext.models.anthropic import AnthropicChatCompletionClient
    except ImportError:
        raise ImportError(
            "Anthropic extension not available. "
            "Run: pip install anthropic"
        )

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY not found in .env file. "
            "Add it: ANTHROPIC_API_KEY=sk-ant-..."
        )

    print(
        "  [llm_config] claude → "
        "claude-haiku-4-5 @ api.anthropic.com"
    )

    return AnthropicChatCompletionClient(
        model="claude-haiku-4-5",
        api_key=api_key,
    )