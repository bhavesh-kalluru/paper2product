from __future__ import annotations
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class Clients:
    openai: OpenAI

def make_clients(openai_api_key: str) -> Clients:
    return Clients(openai=OpenAI(api_key=openai_api_key))
