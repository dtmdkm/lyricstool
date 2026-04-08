from __future__ import annotations
from typing import Callable, Optional

# Cache loaded models to avoid reloading between files in a session
_model_cache: dict = {}


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    model_size: str = "small",
    progress_callback: Optional[Callable[[float, float], None]] = None,
    log_callback: Optional[Callable[[str], None]] = None,
) -> tuple[list[dict], str]:
    """
    Transcribe audio file using faster-whisper.

    Returns:
        (segments, detected_language)
        segments: list of {"start": float, "end": float, "text": str}
    """
    from faster_whisper import WhisperModel

    cache_key = (model_size, "cpu")
    if cache_key not in _model_cache:
        if log_callback:
            log_callback(f"  → Đang tải model '{model_size}' lần đầu (~vài phút, chỉ 1 lần)...")
        _model_cache[cache_key] = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )
        if log_callback:
            log_callback(f"  → Model '{model_size}' đã sẵn sàng")

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
