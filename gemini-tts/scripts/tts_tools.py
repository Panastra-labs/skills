"""
Gemini TTS Tools — Standalone
==============================
Three tools for generating and inspecting AI voiceover audio using the Gemini API.

Requirements:
    pip install google-genai python-dotenv

API Key:
    Set GOOGLE_API_KEY in your environment or in a .env file.

Tools:
    generate_speech(text, ...)         → Generate WAV audio from text
    get_asset_info(asset_path)         → Get metadata (duration, codec, size) for any media file
    inspect_asset(asset_path, prompt)  → Analyze a media file using Gemini multimodal
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import subprocess
import time
import wave
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ---------------------------------------------------------------------------
# Output directory defaults
# ---------------------------------------------------------------------------

def _resolve_output_path(output_path: Optional[str], output_dir: Optional[str] = None) -> Path:
    """Resolve the output path for a generated WAV file.

    Priority:
    1. explicit output_path (absolute or relative to CWD)
    2. output_dir / tts-<timestamp>.wav
    3. ./tts_output / tts-<timestamp>.wav
    """
    if output_path and output_path.strip():
        p = Path(output_path.strip())
        if not p.is_absolute():
            p = Path.cwd() / p
        if p.suffix.lower() != ".wav":
            p = p.with_suffix(".wav")
        return p

    base = Path(output_dir).resolve() if output_dir else Path.cwd() / "tts_output"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return base / f"tts-{stamp}.wav"


def _write_wave_file(
    filename: Path,
    pcm_data: bytes,
    channels: int = 1,
    rate: int = 24000,
    sample_width: int = 2,
) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(filename), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


# ---------------------------------------------------------------------------
# generate_speech
# ---------------------------------------------------------------------------

def generate_speech(
    text: str,
    output_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    voice_name: str = "Kore",
    style_prompt: str = "",
    model: str = "gemini-2.5-flash-preview-tts",
    speakers: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """Generate TTS audio from text and save as a WAV file.

    Args:
        text:         The narration text. For multi-speaker, format as
                      "SpeakerName: dialogue" lines.
        output_path:  Where to save the WAV (absolute or relative path).
                      Auto-generated as tts_output/tts-<timestamp>.wav if omitted.
        output_dir:   Base directory for auto-generated file names.
                      Ignored when output_path is given.
        voice_name:   Prebuilt voice for single-speaker (default "Kore").
                      Ignored when speakers is provided.
        style_prompt: Natural-language delivery instructions prepended to text.
                      Controls tone, pacing, accent, etc.
        model:        TTS model to use. Options:
                        "gemini-2.5-flash-preview-tts" (default, single + multi)
                        "gemini-2.5-pro-preview-tts"   (highest quality, single only)
        speakers:     For multi-speaker dialogue (max 2). List of dicts:
                        [{"name": "Alex", "voice_name": "Kore"},
                         {"name": "Sam",  "voice_name": "Puck"}]
                      Speaker names must match labels used in text.

    Returns:
        dict with keys: success, path, voice_name, model, duration_seconds,
                        sample_rate_hz, channels, size_bytes, text_characters
        On error: {"error": "<message>"}

    Output: 24 kHz, 16-bit, mono WAV.
    """
    if not text or not text.strip():
        return {"error": "text is required"}

    target = _resolve_output_path(output_path, output_dir)

    prompt_text = text.strip()
    if style_prompt.strip():
        prompt_text = f"{style_prompt.strip()}\n\nRead this text exactly:\n{prompt_text}"

    is_multi = bool(speakers and isinstance(speakers, list) and len(speakers) >= 2)

    if is_multi:
        if len(speakers) > 2:
            return {"error": "Multi-speaker TTS supports a maximum of 2 speakers."}
        if "pro" in model.lower():
            return {"error": "Multi-speaker is only supported on gemini-2.5-flash-preview-tts, not Pro."}
        speaker_configs = []
        for spk in speakers:
            spk_name = spk.get("name", "").strip()
            spk_voice = spk.get("voice_name", "Kore").strip()
            if not spk_name:
                return {"error": "Each speaker must have a 'name' matching labels in the text."}
            speaker_configs.append(
                types.SpeakerVoiceConfig(
                    speaker=spk_name,
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=spk_voice)
                    ),
                )
            )
        speech_cfg = types.SpeechConfig(
            multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                speaker_voice_configs=speaker_configs
            )
        )
    else:
        speech_cfg = types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
            )
        )

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model=model,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=speech_cfg,
            ),
        )
    except Exception as exc:
        return {"error": f"TTS request failed: {exc}"}

    try:
        part = response.candidates[0].content.parts[0]
        data = getattr(getattr(part, "inline_data", None), "data", None)
        if not data:
            return {"error": "TTS response did not include audio data"}
        pcm_data = base64.b64decode(data) if isinstance(data, str) else data
        _write_wave_file(target, pcm_data)
        with wave.open(str(target), "rb") as wf:
            duration = wf.getnframes() / float(wf.getframerate() or 24000)
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
    except Exception as exc:
        return {"error": f"Failed to save audio: {exc}"}

    return {
        "success": True,
        "path": str(target),
        "voice_name": voice_name,
        "model": model,
        "duration_seconds": round(duration, 3),
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "size_bytes": target.stat().st_size,
        "text_characters": len(text),
    }


# ---------------------------------------------------------------------------
# get_asset_info
# ---------------------------------------------------------------------------

def get_asset_info(asset_path: str) -> Dict[str, Any]:
    """Get metadata for a media file (audio, video, image).

    Uses ffprobe for duration, resolution, and codec info when available.
    Falls back to basic file info if ffprobe is not installed.

    Args:
        asset_path: Absolute or relative path to the file.

    Returns:
        dict with keys: path, size_bytes, mime_type, and optionally
        duration_seconds, width, height, video_codec, audio_codec.
        On error: {"error": "<message>"}
    """
    target = Path(asset_path)
    if not target.is_absolute():
        target = Path.cwd() / target

    if not target.exists() or not target.is_file():
        return {"error": f"File not found: {asset_path}"}

    size = target.stat().st_size
    mime, _ = mimetypes.guess_type(str(target))
    info: Dict[str, Any] = {
        "path": str(target),
        "size_bytes": size,
        "mime_type": mime or "application/octet-stream",
    }

    # For WAV files, read duration directly without ffprobe
    if target.suffix.lower() == ".wav":
        try:
            with wave.open(str(target), "rb") as wf:
                info["duration_seconds"] = round(wf.getnframes() / float(wf.getframerate()), 3)
                info["sample_rate_hz"] = wf.getframerate()
                info["channels"] = wf.getnchannels()
                info["sample_width_bytes"] = wf.getsampwidth()
            return info
        except Exception:
            pass

    # General media info via ffprobe
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration:stream=width,height,codec_name,codec_type",
            "-of", "json",
            str(target),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            probe_data = json.loads(result.stdout)
            if "format" in probe_data and "duration" in probe_data["format"]:
                info["duration_seconds"] = round(float(probe_data["format"]["duration"]), 3)
            streams = probe_data.get("streams", [])
            video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
            if video_stream:
                info["width"] = video_stream.get("width")
                info["height"] = video_stream.get("height")
                info["video_codec"] = video_stream.get("codec_name")
            if audio_stream:
                info["audio_codec"] = audio_stream.get("codec_name")
    except FileNotFoundError:
        info["note"] = "Install ffprobe for duration and codec info."
    except Exception:
        info["note"] = "ffprobe failed; only basic file info available."

    return info


# ---------------------------------------------------------------------------
# inspect_asset
# ---------------------------------------------------------------------------

def inspect_asset(
    asset_path: str,
    prompt: str = "",
    model: Optional[str] = None,
) -> str:
    """Analyze a media file (video, audio, image) using Gemini multimodal.

    The file is uploaded to the Gemini Files API, then analyzed with the
    provided prompt. Useful for auditing generated audio quality, verifying
    pacing, or reviewing video content.

    Args:
        asset_path: Absolute or relative path to the file.
        prompt:     What to analyze. Defaults to a general content/mood breakdown.
        model:      Gemini model to use. Defaults to GEMINI_MODEL env var or
                    "gemini-2.0-flash".

    Returns:
        Gemini's analysis as a string. On error, returns an error string.
    """
    target = Path(asset_path)
    if not target.is_absolute():
        target = Path.cwd() / target

    if not target.exists() or not target.is_file():
        return f"Error: File not found: {asset_path}"

    if not prompt.strip():
        prompt = (
            "Analyze this media file for voiceover/audio production purposes:\n"
            "1. Describe the overall content and mood.\n"
            "2. Note tone, pacing, and clarity of any speech.\n"
            "3. Identify any background noise, artifacts, or quality issues.\n"
            "4. Suggest any improvements if applicable."
        )

    _model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    try:
        client = genai.Client()
        uploaded = client.files.upload(file=str(target))

        # Wait for the file to be processed (required for video/audio)
        for _ in range(60):
            try:
                uploaded = client.files.get(name=uploaded.name)
            except Exception:
                pass
            state = getattr(getattr(uploaded, "state", None), "name", "")
            if state == "ACTIVE":
                break
            time.sleep(1)

        state = getattr(getattr(uploaded, "state", None), "name", "")
        if state != "ACTIVE":
            return "Error: File is still processing. Try again in a few seconds."

        response = client.models.generate_content(
            model=_model,
            contents=[uploaded, prompt],
        )
        return response.text or "(No response text)"
    except Exception as exc:
        return f"Error: {exc}"


# ---------------------------------------------------------------------------
# CLI — quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/tts_tools.py speak \"Your text here\"")
        print("  python scripts/tts_tools.py info path/to/file.wav")
        print("  python scripts/tts_tools.py inspect path/to/file.wav")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "speak" and len(sys.argv) >= 3:
        result = generate_speech(text=" ".join(sys.argv[2:]))
        print(json.dumps(result, indent=2))

    elif cmd == "info" and len(sys.argv) >= 3:
        result = get_asset_info(sys.argv[2])
        print(json.dumps(result, indent=2))

    elif cmd == "inspect" and len(sys.argv) >= 3:
        prompt_arg = sys.argv[4] if len(sys.argv) >= 5 else ""
        result = inspect_asset(sys.argv[2], prompt=prompt_arg)
        print(result)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
