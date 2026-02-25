# Models and Limits

## Supported TTS Models

| Model | ID | Single-Speaker | Multi-Speaker | Best For |
|-------|-----|:-:|:-:|----------|
| Flash TTS | `gemini-2.5-flash-preview-tts` | ✓ | ✓ (up to 2) | Most tasks. Fast iteration, dialogue. |
| Pro TTS | `gemini-2.5-pro-preview-tts` | ✓ | ✗ | Highest quality single-speaker narration. |

> **Note**: Both models are in preview. Model IDs may change when they reach GA.

## Model Selection Rules

1. **Default to Flash** (`gemini-2.5-flash-preview-tts`):
   - Faster generation.
   - Supports both single-speaker and multi-speaker.
   - Good quality for most narration use cases.

2. **Use Pro** (`gemini-2.5-pro-preview-tts`) only when:
   - Maximum single-speaker vocal quality is required.
   - The request explicitly asks for highest-quality audio.
   - Multi-speaker is NOT needed (Pro does not support it).

## Hard Constraints

- **Input**: Text only. No audio, image, or video inputs are accepted by TTS models.
- **Output**: Audio only. No text, image, or video outputs.
- **Context window**: 32,000 tokens maximum per request.
- **Output format**: Raw PCM audio data, 24 kHz sample rate, 16-bit, mono.
- **Multi-speaker limit**: Maximum 2 speakers per request (Flash only).
- **Status**: Preview capability — behavior may change.

## Output Audio Specs

The tool saves output as WAV (PCM):
- Sample rate: 24,000 Hz
- Channels: 1 (mono)
- Sample width: 2 bytes (16-bit)
- Format: WAV

## Rate Limits and Practical Considerations

- TTS generation speed depends on text length — longer text takes longer.
- For long narration (many paragraphs), chunk into segments of 1–4 sentences.
- Each chunk is a separate API call.
- If generation fails with timeout, try shorter text or retry.
- Very long single prompts (approaching 32k tokens with style instructions) may degrade quality — keep prompts focused.

## API Key

Set `GOOGLE_API_KEY` in your environment or a `.env` file. The tool uses `genai.Client()` which automatically picks it up.
