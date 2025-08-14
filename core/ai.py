from __future__ import annotations

import json
import os
from typing import Dict, Iterator, List, Optional, Tuple

import requests

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CHAT_URL = f"{OLLAMA_HOST}/api/chat"


DEFAULT_TIMEOUT_SYNC: Tuple[float, float] = (3.05, 120.0)
DEFAULT_TIMEOUT_STREAM: Tuple[float, float] = (3.05, 300.0)


class AIError(RuntimeError):
    """Kullanıcıya gösterilebilir AI/HTTP hataları."""

    pass


def to_ollama_messages(
    state_messages: List[Dict],
    system_text: Optional[str] = None,
) -> List[Dict]:

    out: List[Dict] = []
    if system_text:
        out.append({"role": "system", "content": system_text})

    for m in state_messages:
        role = m.get("role", "")
        if role == "bot":
            role = "assistant"
        out.append({"role": role, "content": m.get("content", "")})
    return out


def chat_sync(
    model: str,
    messages: List[Dict],
    *,
    options: Optional[Dict] = None,
    timeout: Tuple[float, float] = DEFAULT_TIMEOUT_SYNC,
) -> str:

    payload: Dict = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if options:
        payload["options"] = options

    try:
        resp = requests.post(CHAT_URL, json=payload, timeout=timeout)
    except requests.exceptions.ConnectionError as exc:
        raise AIError("Ollama'a bağlanılamadı. Ollama servisi çalışıyor mu?") from exc
    except requests.exceptions.Timeout as exc:
        raise AIError("Ollama isteği zaman aşımına uğradı.") from exc

    if resp.status_code >= 400:
        try:
            data = resp.json()
            msg = data.get("error") or data
        except Exception:
            msg = resp.text
        raise AIError(f"Ollama hata döndürdü (HTTP {resp.status_code}): {msg}")

    try:
        data = resp.json()
        content = data["message"]["content"]
    except Exception as exc:
        raise AIError("Ollama yanıtı beklenen biçimde değil.") from exc

    return content
