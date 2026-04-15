"""Voice transcription via OpenAI Whisper API."""

from __future__ import annotations

import os
import tempfile
from typing import Optional

from openai import OpenAI


def transcribe_audio_with_whisper(
    audio_bytes: bytes,
    *,
    lang: str,
    api_key: str,
) -> Optional[str]:
    """
    Transcribe audio using OpenAI Whisper. lang: fr | ar | en (Darija uses ar).
    """
    if not audio_bytes or not api_key.strip():
        return None

    lang_map = {"fr": "fr", "ar": "ar", "en": "en"}
    whisper_lang = lang_map.get(lang, "fr")

    client = OpenAI(api_key=api_key.strip())

    suffix = ".webm"
    if audio_bytes[:4] == b"RIFF":
        suffix = ".wav"
    elif audio_bytes[:3] == b"ID3" or audio_bytes[:2] == b"\xff\xfb":
        suffix = ".mp3"

    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=whisper_lang,
                response_format="text",
            )

        if isinstance(result, str):
            return result.strip() or None
        text = getattr(result, "text", None)
        if text:
            return str(text).strip()
        return str(result).strip() or None
    except Exception:
        return None
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
