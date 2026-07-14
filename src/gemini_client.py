import os
from typing import Generator

from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

_client = None


def is_available() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY"))


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def stream_gemini(prompt: str, model: str) -> Generator[str, None, None]:
    client = _get_client()
    for chunk in client.models.generate_content_stream(model=model, contents=prompt):
        if chunk.text:
            yield chunk.text
