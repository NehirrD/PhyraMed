"""Groq API (OpenAI uyumlu endpoint)."""

import os
import re

from openai import OpenAI

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
TEXT_MODEL = "llama-3.3-70b-versatile"
# Llama 4 Scout Groq'ta 2026-07-17'de kaldırıldı; güncel vision modeli:
VISION_MODEL = "qwen/qwen3.6-27b"


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


def extract_model_text(content: str) -> str:
    """Qwen thinking bloklarını ayıkla; yanıt sadece thinking içindeyse içeriği koru."""
    if not content:
        return ""

    text = content.strip()
    tag_pairs = [
        ("<think>", "</think>"),
        ("<" + "think" + ">", "</" + "think" + ">"),
    ]
    for open_tag, close_tag in tag_pairs:
        after = re.sub(
            rf"^{re.escape(open_tag)}.*?(?:{re.escape(close_tag)}|$)",
            "",
            text,
            count=1,
            flags=re.DOTALL,
        ).strip()
        if after:
            return after

        inside = re.search(
            rf"{re.escape(open_tag)}(.*?)(?:{re.escape(close_tag)}|$)",
            text,
            flags=re.DOTALL,
        )
        if inside and inside.group(1).strip():
            return inside.group(1).strip()

    return text


def vision_completion(client, messages: list, *, max_tokens: int = 400, temperature: float = 0.1):
    """Vision model çağrısı — Qwen thinking modunu kapatır."""
    return client.chat.completions.create(
        model=VISION_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        extra_body={"reasoning_effort": "none"},
    )