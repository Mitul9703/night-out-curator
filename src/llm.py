"""Provider-agnostic LLM factory.

Swap providers with env vars — NO code change. Set LLM_PROVIDER (and optionally
LLM_MODEL); each provider reads its own key from the environment (.env):

    provider        LLM_PROVIDER    key env var          example LLM_MODEL          free / no-card?
    --------------  --------------  -------------------  -------------------------  ----------------
    OpenAI          openai          OPENAI_API_KEY       gpt-4o-mini                no (paid)
    Anthropic       anthropic       ANTHROPIC_API_KEY    claude-3-5-haiku-latest    no (paid)
    Google Gemini   google_genai    GOOGLE_API_KEY       gemini-2.0-flash           YES (free tier)
    Ollama (local)  ollama          (none)               llama3.1                   YES (local)

Uses LangChain's init_chat_model, so any provider it supports also works.
"""
import os
from langchain.chat_models import init_chat_model

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "google_genai": "gemini-2.0-flash",
    "ollama": "llama3.1",
}


def get_llm(temperature: float = 0.0):
    provider = os.getenv("LLM_PROVIDER", "openai").strip()
    model = os.getenv("LLM_MODEL", "").strip() or DEFAULT_MODELS.get(provider, "gpt-4o-mini")
    return init_chat_model(model, model_provider=provider, temperature=temperature)
