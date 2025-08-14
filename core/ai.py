# core/ai.py
# Ollama ile sohbet için sarmalayıcı:
# - chat_sync: tek seferde yanıt
# - chat_stream: parça parça (stream) yanıt
# - to_ollama_messages: state.messages -> Ollama chat "messages" biçimi
# - AIError: anlaşılır hata sınıfı

from __future__ import annotations

import json
import os
from typing import Dict, Iterator, List, Optional, Tuple

import requests

# -------------------------- Ayarlar --------------------------

# Ortam değişkeni ile özelleştirilebilir; varsayılan yerel servis
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
CHAT_URL = f"{OLLAMA_HOST}/api/chat"

# Varsayılan zaman aşımları: (bağlanma, okuma)
DEFAULT_TIMEOUT_SYNC: Tuple[float, float] = (3.05, 120.0)
DEFAULT_TIMEOUT_STREAM: Tuple[float, float] = (3.05, 300.0)


# -------------------------- Hatalar --------------------------


class AIError(RuntimeError):
    """Kullanıcıya gösterilebilir AI/HTTP hataları."""

    pass


# ---------------------- Yardımcı Dönüştürücü ----------------------


def to_ollama_messages(
    state_messages: List[Dict],
    system_text: Optional[str] = None,
) -> List[Dict]:
    """
    state.messages (role, content, ts) -> Ollama chat formatı (role, content).
    Not: state'teki 'bot' rolünü Ollama tarafında 'assistant' olarak eşler.
    """
    out: List[Dict] = []
    if system_text:
        out.append({"role": "system", "content": system_text})

    for m in state_messages:
        role = m.get("role", "")
        if role == "bot":
            role = "assistant"
        out.append({"role": role, "content": m.get("content", "")})
    return out


# ---------------------- Senkron (bloklu) ----------------------


def chat_sync(
    model: str,
    messages: List[Dict],
    *,
    options: Optional[Dict] = None,
    timeout: Tuple[float, float] = DEFAULT_TIMEOUT_SYNC,
) -> str:
    """
    Ollama /api/chat'e senkron istek atar, tek metin döndürür.
    - model: "llama3.2:3b" gibi
    - messages: [{"role":"user|system|assistant","content":"..."}]
    - options: Ollama jenerasyon ayarları (temperature, num_ctx, vb.)
    """
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


# ---------------------- Akışlı (stream) ----------------------
"""

def chat_stream(
    model: str,
    messages: List[Dict],
    *,
    options: Optional[Dict] = None,
    timeout: Tuple[float, float] = DEFAULT_TIMEOUT_STREAM,
) -> Iterator[str]:
    
    #stream=true ile Ollama'dan parça parça metin üretimi.
    #Kullanım: for chunk in chat_stream(...): ...
    
    payload: Dict = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if options:
        payload["options"] = options

    try:
        with requests.post(
            CHAT_URL, json=payload, timeout=timeout, stream=True
        ) as resp:
            if resp.status_code >= 400:
                try:
                    data = resp.json()
                    msg = data.get("error") or data
                except Exception:
                    msg = resp.text
                raise AIError(f"Ollama hata döndürdü (HTTP {resp.status_code}): {msg}")

            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                # Bazı çıktılar "data: {...}" ile gelir; varsa temizle
                if line.startswith("data:"):
                    line = line[5:].strip()

                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # gürültüyü atla

                # İçerik parçası
                msg = obj.get("message") or {}
                piece = msg.get("content", "")
                if piece:
                    yield piece

                # Bitti sinyali
                if obj.get("done"):
                    break

    except requests.exceptions.ConnectionError as exc:
        raise AIError("Ollama'a bağlanılamadı. Ollama servisi çalışıyor mu?") from exc
    except requests.exceptions.Timeout as exc:
        raise AIError("Ollama isteği zaman aşımına uğradı.") from exc

"""
