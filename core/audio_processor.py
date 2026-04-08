import subprocess
from pathlib import Path


def convert_to_wav(input_path: str, output_path: str) -> None:
    """Convert any audio/video file to 16kHz mono WAV using bundled FFmpeg."""
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe,
        "-i", input_path,
        "-ar", "16000",   # 16 kHz sample rate (required by Whisper)
        "-ac", "1",       # mono
        "-c:a", "pcm_s16le",
        "-y",             # overwrite output
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error:\n{result.stderr[-500:]}")
