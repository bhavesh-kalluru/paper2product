from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_chat_model: str = "gpt-4o-mini"
    openai_embed_model: str = "text-embedding-3-small"

    perplexity_api_key: str | None = None
    pplx_model: str = "sonar-pro"

def get_settings() -> Settings:
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openai_key:
        raise RuntimeError("Missing OPENAI_API_KEY (set it in .env or in your hosting environment).")

    pplx_key = os.getenv("PERPLEXITY_API_KEY", "").strip() or None

    return Settings(
        openai_api_key=openai_key,
        openai_chat_model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini").strip(),
        openai_embed_model=os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small").strip(),
        perplexity_api_key=pplx_key,
        pplx_model=os.getenv("PPLX_MODEL", "sonar-pro").strip(),
    )
