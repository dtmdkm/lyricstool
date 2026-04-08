from __future__ import annotations
import os
from typing import Callable, Optional

# Use Asian mirror — significantly faster for VN/China users
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

# Cache loaded models to avoid reloading between files in a session
_model_cache: dict = {}

_MODEL_SIZES_MB = {
    "tiny": 39, "base": 74, "small": 244, "medium": 769, "large-v3": 1500,
}


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    model_size: str = "small",
    progress_callback: Optional[Callable[[float, float], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
    status_callback: Optional[Callable[[int, str], None]] = None,
) -> tuple[list[dict], str]:
    """
    Transcribe audio using faster-whisper.
    status_callback(pct, text) — updates the file-row status label.
    """
    from faster_whisper import WhisperModel

    cache_key = (model_size, "cpu")
    if cache_key not in _model_cache:
        mb = _MODEL_SIZES_MB.get(model_size, "?")
        msg = f"Đang tải model '{model_size}' (~{mb} MB) lần đầu..."
        if log_callback:
            log_callback(f"  → {msg}")
        if status_callback:
            status_callback(12, msg)

        _model_cache[cache_key] = WhisperModel(
            model_size, device="cpu", compute_type="int8",
        )
        if log_callback:
            log_callback(f"  → Model '{model_size}' sẵn sàng")
        if status_callback:
            status_callback(22, "Đang nhận dạng giọng nói...")

    model = _model_cache[cache_key]

    kwargs: dict = {"beam_size": 5}
    if language:
        kwargs["language"] = language

    segments_gen, info = model.transcribe(audio_path, **kwargs)
    total_duration: float = info.duration or 0.0

    segments: list[dict] = []
    for seg in segments_gen:
        text = seg.text.strip()
        if not text:
            continue
        segments.append({"start": seg.start, "end": seg.end, "text": text})
        if progress_callback and total_duration > 0:
            progress_callback(seg.end, total_duration)

    return segments, info.language
