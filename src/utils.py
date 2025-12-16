from __future__ import annotations
import hashlib
from typing import Iterable

def stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def clip(s: str, n: int = 120) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else (s[: n - 1] + "…")

def join_nonempty(parts: Iterable[str], sep: str = " — ") -> str:
    xs = [p.strip() for p in parts if (p or "").strip()]
    return sep.join(xs)
