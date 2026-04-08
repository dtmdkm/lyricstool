from __future__ import annotations
import re


def _fmt_ts(seconds: float) -> str:
    """Format seconds → SRT timestamp HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        ms = 999
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def segments_to_srt(segments: list[dict]) -> str:
    """Convert Whisper segments list to SRT string."""
    lines: list[str] = []
    index = 1
    for seg in segments:
        text = seg["text"].strip()
        if not text:
            continue
        start = _fmt_ts(seg["start"])
        end = _fmt_ts(seg["end"])
        lines.append(f"{index}\n{start} --> {end}\n{text}\n")
        index += 1
    return "\n".join(lines)


def save_srt(segments: list[dict], output_path: str) -> None:
    """Write SRT file to disk (UTF-8)."""
    content = segments_to_srt(segments)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
