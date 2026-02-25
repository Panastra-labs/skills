---
name: gemini-tts
description: Generate AI voiceover audio using Gemini TTS. Use when generating speech, narration, or dialogue audio: single-speaker narration, multi-speaker conversations, voice selection, style/tone prompting, audio duration measurement, and audio quality inspection.
---

## Setup

**Install dependencies:**
```bash
pip install -r scripts/requirements.txt
```

**API key** — set `GOOGLE_API_KEY` in your environment or a `.env` file:
```
GOOGLE_API_KEY=your_key_here
```

**Import tools:**
```python
from scripts.tts_tools import generate_speech, get_asset_info, inspect_asset
```

---

## Quick Start — Simple TTS

```python
generate_speech(text="Welcome to our product tour.")
```

Output saved to `./tts_output/tts-<timestamp>.wav` by default.

### Specifying Output Path

```python
generate_speech(
    text="Welcome to our product tour.",
    output_path="audio/intro.wav"
)
```

### Choosing a Voice

Pick a voice that fits the tone:

| Use Case              | Recommended Voices                      |
|-----------------------|-----------------------------------------|
| Neutral narration     | Kore (Firm), Charon (Informative), Schedar (Even), Sadaltager (Knowledgeable) |
| Energetic / upbeat    | Puck (Upbeat), Fenrir (Excitable), Laomedeia (Upbeat) |
| Warm storytelling     | Sulafat (Warm), Achird (Friendly), Vindemiatrix (Gentle) |
| Serious / authoritative | Kore (Firm), Orus (Firm), Alnilam (Firm), Gacrux (Mature) |
| Soft / calm           | Achernar (Soft), Enceladus (Breathy) |
| Casual / conversational | Zubenelgenubi (Casual), Callirrhoe (Easy-going), Umbriel (Easy-going) |

Full 30-voice list → `references/voices.md`

### Adding Style

```python
generate_speech(
    text="This is the moment everything changed.",
    voice_name="Sulafat",
    style_prompt="Speak slowly and dramatically, like a documentary narrator building suspense."
)
```

### Multi-Speaker Dialogue

```python
generate_speech(
    text="""Alex: Hey, did you see the new release?
Sam: Yeah, it looks incredible!""",
    speakers=[
        {"name": "Alex", "voice_name": "Kore"},
        {"name": "Sam",  "voice_name": "Puck"}
    ]
)
```

- Max 2 speakers per request.
- Speaker names must exactly match the labels used in the text.
- Multi-speaker only works with `gemini-2.5-flash-preview-tts`.

Full multi-speaker details → `references/multi-speaker.md`

---

## Core Workflow

1. **Generate** with `generate_speech(...)` → saves WAV to your output path.
2. **Measure** with `get_asset_info(...)` → get exact duration.
3. **Adjust** — if duration doesn't match target, rewrite text shorter/longer and regenerate.
4. **Validate** with `inspect_asset(...)` → check pronunciation, pacing, emotional fit.
5. **Iterate** chunk by chunk until satisfied.

---

## Tool Reference

### `generate_speech`

```python
generate_speech(
    text: str,                    # Required.
    output_path: str = None,      # Optional. Absolute or relative path, e.g. "audio/intro.wav"
    output_dir: str = None,       # Optional. Base dir for auto-named files (default: ./tts_output)
    voice_name: str = "Kore",     # Optional. Any of the 30 prebuilt voices.
    style_prompt: str = "",       # Optional. Natural-language delivery instructions.
    model: str = "gemini-2.5-flash-preview-tts",  # Optional.
    speakers: list = None         # Optional. For multi-speaker: [{"name": ..., "voice_name": ...}]
)
```

Returns: `{ success, path, voice_name, model, duration_seconds, sample_rate_hz, channels, size_bytes, text_characters }`
On error: `{ error: "..." }`

Output is always 24 kHz mono WAV (PCM 16-bit).

### `get_asset_info`

```python
get_asset_info(asset_path: str)
```

Returns file metadata. For WAV files, reads duration without ffprobe. For video/audio, uses ffprobe if installed.

Returns: `{ path, size_bytes, mime_type, duration_seconds, ... }`

### `inspect_asset`

```python
inspect_asset(
    asset_path: str,
    prompt: str = "",    # Optional. What to analyze.
    model: str = None,   # Optional. Defaults to GEMINI_MODEL env var or "gemini-2.0-flash".
)
```

Uploads the file to Gemini and returns an analysis (tone, pacing, quality issues, etc.).

---

## Models

| Model                              | Single | Multi | Notes |
|------------------------------------|:------:|:-----:|-------|
| `gemini-2.5-flash-preview-tts`     | ✓ | ✓ | Default. Fast. Use for most tasks. |
| `gemini-2.5-pro-preview-tts`       | ✓ | ✗ | Higher quality single-speaker only. |

> **Note**: Both models are in preview. Model IDs may change when they reach GA.

---

## Prompting Quick Guide

For simple tasks, a one-line `style_prompt` is enough:
- `"Read in a calm, professional tone."`
- `"Excited sports announcer style."`
- `"Whisper softly, like telling a secret."`

For complex performances, structure the prompt:
1. **Audio Profile** — Who is speaking (name, role, character).
2. **Scene** — Environment, mood.
3. **Director's Notes** — Style, pacing, accent.
4. **Transcript** — The actual text.

Full prompting guide → `references/prompting-style-and-flow.md`

---

## When to Read References

| Situation | Reference |
|-----------|-----------|
| Selecting a voice | `references/voices.md` |
| Multi-speaker dialog | `references/multi-speaker.md` |
| Complex style / accent control | `references/prompting-style-and-flow.md` |
| Non-English languages | `references/languages.md` |
| Model selection or API constraints | `references/models-and-limits.md` |
| Duration fitting, chunking, timeline sync | `references/timeline-integration.md` |

## References

- [references/models-and-limits.md](references/models-and-limits.md)
- [references/voices.md](references/voices.md)
- [references/languages.md](references/languages.md)
- [references/prompting-style-and-flow.md](references/prompting-style-and-flow.md)
- [references/multi-speaker.md](references/multi-speaker.md)
- [references/timeline-integration.md](references/timeline-integration.md)
