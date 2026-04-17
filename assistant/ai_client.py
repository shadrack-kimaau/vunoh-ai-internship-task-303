import os
from typing import Optional

import requests


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v not in (None, "") else default


def get_ai_config():
    """
    Reads AI configuration from environment variables.

    Supported env vars:
    - AI_API_KEY (preferred)
    - OPENAI_API_KEY (fallback)
    - AI_BASE_URL (openai-compatible base, default: https://api.openai.com/v1)
    - AI_MODEL (default: gpt-4o-mini)
    """

    api_key = _env("AI_API_KEY") or _env("OPENAI_API_KEY")
    base_url = _env("AI_BASE_URL", "https://api.openai.com/v1")
    model = _env("AI_MODEL", "gpt-4o-mini")
    return api_key, base_url, model


def extract_json_from_text(text: str) -> str:
    """
    Best-effort extraction of the first JSON object from a model output.
    Helps when the model wraps JSON in extra text.
    """

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return text
    return text[start : end + 1]


def chat_completion_json_only(system_prompt: str, user_prompt: str, *, timeout_s: int = 60):
    """
    Calls an OpenAI-compatible /chat/completions endpoint and returns the parsed JSON.

    Returns:
      dict (parsed)

    Raises:
      Exception if request fails or JSON cannot be parsed.
    """

    api_key, base_url, model = get_ai_config()
    if not api_key:
        raise RuntimeError("Missing AI API key (set AI_API_KEY or OPENAI_API_KEY).")

    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}

    # Note: not all providers support OpenAI's response_format. We ask for JSON only in the prompt
    # and then parse the string content.
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
    }

    res = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    res.raise_for_status()
    data = res.json()

    content = (
        (data.get("choices") or [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    if not content:
        raise RuntimeError("AI response contained empty content.")

    json_text = extract_json_from_text(content)
    import json

    return json.loads(json_text)

