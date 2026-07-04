"""Groq API (OpenAI uyumlu endpoint)."""

import os

from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
TEXT_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def get_groq_key():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None
    key = key.strip().strip('"').strip("'")
    return key or None


def get_groq_client():
    key = get_groq_key()
    if not key:
        return None
    return OpenAI(base_url=GROQ_BASE_URL, api_key=key)
