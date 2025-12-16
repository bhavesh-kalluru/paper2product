from __future__ import annotations

from typing import Any, Dict, List
import httpx

PPLX_CHAT_URL = "https://api.perplexity.ai/chat/completions"

class PerplexityError(RuntimeError):
    pass

def web_signals(
    api_key: str,
    *,
    model: str,
    theme_summary: str,
    timeout_s: float = 45.0,
) -> str:
    if not api_key:
        raise PerplexityError("Missing PERPLEXITY_API_KEY")

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": "You are a concise tech news analyst. Provide links."},
        {"role": "user", "content": (
            "Based on these research themes, find 6-10 recent web items (news/posts/docs) that matter. "
            "Return a bullet list. Each bullet: Title — URL — 1 sentence why it matters.\n\n"
            f"Themes:\n{theme_summary}"
        )},
    ]

    body: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 900,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        with httpx.Client(timeout=timeout_s) as client:
            r = client.post(PPLX_CHAT_URL, headers=headers, json=body)
    except httpx.HTTPError as e:
        raise PerplexityError(f"Perplexity network error: {e}") from e

    if r.status_code >= 400:
        raise PerplexityError(f"Perplexity HTTP {r.status_code}: {r.text}")

    data = r.json()
    try:
        return data["choices"][0]["message"]["content"] or ""
    except Exception:
        return ""
