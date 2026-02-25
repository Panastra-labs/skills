# Timeline Integration

## Purpose

Structuring generated TTS audio into a multi-chunk narration track — covering chunking strategy, duration fitting, and timeline sync.

## Chunking Strategy

### Why Chunk?
- Long narration as one file is hard to time-align with specific moments.
- Per-scene or per-segment chunks allow independent timing adjustments.
- If one chunk sounds wrong, you regenerate only that chunk, not the entire narration.

### Chunk Sizing
| Sync Requirement | Chunk Size | Use When |
|-----------------|------------|----------|
| Strict sync (must match exact moments) | 1–2 sentences | Timed narration over specific scenes |
| Moderate sync | 2–4 sentences | General voiceover with loose timing |
| Relaxed sync | 4+ sentences | Intro/outro narration, podcast-style |

### File Naming Convention
Use predictable, sequential file names:
```
audio/scene-01-line-01.wav
audio/scene-01-line-02.wav
audio/scene-02-line-01.wav
```

Or by purpose:
```
audio/intro.wav
audio/chapter-1.wav
audio/outro.wav
```

## Duration Fitting Workflow

Getting TTS duration to match a target video/scene duration:

### Step 1: Generate
```python
result = generate_speech(
    text="Our journey begins in the heart of the Amazon rainforest.",
    output_path="audio/scene-01.wav",
    voice_name="Sulafat",
    style_prompt="Slow, cinematic documentary narrator."
)
```

### Step 2: Measure
```python
info = get_asset_info("audio/scene-01.wav")
print(info["duration_seconds"])  # e.g. 4.2
```

### Step 3: Compare to Target
If the scene needs 5 seconds and audio is 4.2s:
- **0.8s short** → options below.

### Step 4: Adjust

**If too short (audio shorter than target):**
- Extend the script text slightly (add a word or two).
- Or add intentional pauses: `"Our journey begins... in the heart of the Amazon rainforest."`
- Or adjust pacing in `style_prompt`: `"Speak more slowly."`
- Regenerate.

**If too long (audio longer than target):**
- Trim the script text (remove words or simplify).
- Or speed up pacing: `"Speak at a brisk, efficient pace."`
- Regenerate.

**If close (within ~10% / 0.5s):**
- Apply light ffmpeg speed correction:
  ```bash
  ffmpeg -i scene-01.wav -filter:a "atempo=1.05" scene-01-adjusted.wav
  ```
- Stay within 0.9x–1.1x tempo range. Beyond that, quality degrades.

### Step 5: Add Fades
To prevent click artifacts at chunk boundaries:
```bash
ffmpeg -i scene-01.wav -af "afade=t=in:st=0:d=0.05,afade=t=out:st=<end-0.05>:d=0.05" scene-01-faded.wav
```

Short fades (50ms) are usually sufficient.

---

## Video Editor Integration

Once your WAV chunks are ready and measured, place them on the timeline of your video editor. Most video editors support placing audio at an exact timestamp. The examples below use a React-based editor (Remotion) — adapt as needed for your own tool.

### Basic Placement Pattern
```tsx
// Example using Remotion — adapt for your video editor's API
import { Sequence, Audio, staticFile } from 'remotion';

<Sequence from={startFrame} durationInFrames={durationFrames}>
  <Audio src={staticFile("assets/tts/scene-01.wav")} />
</Sequence>
```

### Computing Frames from Timestamps
```tsx
const fps = 30;

// Scene starts at 00:05, ends at 00:10
const startFrame = 5 * fps;      // 150
const durationFrames = 5 * fps;  // 150
```

### Layering Voiceover with Music
```tsx
// Example using Remotion
{/* Background music — ducked under voiceover */}
<Audio
  src={staticFile("assets/music/bg.mp3")}
  volume={(f) => {
    if (f >= voiceoverStart && f <= voiceoverEnd) return 0.2;
    return 0.8;
  }}
/>

{/* Voiceover layer */}
<Sequence from={voiceoverStart} durationInFrames={voiceoverDuration}>
  <Audio src={staticFile("assets/tts/narration.wav")} />
</Sequence>
```

### Multiple Chunks in Sequence
```tsx
// Example using Remotion
const chunks = [
  { file: "scene-01-line-01.wav", startSec: 2,  durationSec: 3.5 },
  { file: "scene-01-line-02.wav", startSec: 6,  durationSec: 4.2 },
  { file: "scene-02-line-01.wav", startSec: 12, durationSec: 5.1 },
];

{chunks.map((chunk) => (
  <Sequence
    key={chunk.file}
    from={Math.round(chunk.startSec * fps)}
    durationInFrames={Math.round(chunk.durationSec * fps)}
  >
    <Audio src={staticFile(`assets/tts/${chunk.file}`)} />
  </Sequence>
))}
```
