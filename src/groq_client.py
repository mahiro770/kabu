import os
from typing import Generator

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

_client = None


def is_available() -> bool:
    return bool(os.environ.get("GROQ_API_KEY"))


def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def stream_groq(prompt: str, model: str) -> Generator[str, None, None]:
    client = _get_client()
    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content
