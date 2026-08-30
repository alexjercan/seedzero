---
name: voiceover
description: Generate and verify narration audio with the local speech API when producing a short.
---

# Voiceover

Speak an approved narration file and verify it by round-trip transcription:

```bash
scripts/voiceover.sh projects/<name>/narration.txt media/<name>/voice.wav
```

The script posts to `http://localhost:10300/v1/audio/speech` with the only
supported settings (`piper-1`, `en_US-lessac-medium`, wav), then sends the
audio back through `/v1/audio/transcriptions` and fails when the normalized
words differ from the narration file.

Rules:

- Plain text only. No control characters, no markup, no emoji.
- Write numbers, units, and symbols as words: "nine hundred twenty four to
  one", not "924:1". This fixes both pronunciation and the round trip.
- Target 100 to 150 words for a 30 to 45 second short. The voice reads at
  roughly three and a third words per second (measured).
- On mismatch, first fix spelling-out issues in the narration; if the voice
  mispronounces a word, rephrase it. Never accept unverified audio.
- Record the round-trip result in the task evidence.
