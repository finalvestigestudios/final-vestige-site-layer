# Final Vestige Audio Mastering Lane v1

Deterministic final-mix and mastering lane for the Final Vestige podcast and faceless YouTube documentaries.

## What this fixes

The editor timeline is no longer the source of truth. A final master passes only when the **exported file** is rendered from an explicit cue sheet, measured, and QC-checked.

## Locked house narration assumptions

- Narrator: Bryan Rhodes PVC.
- Default synthesis model: ElevenLabs `eleven_multilingual_v2` until a later model passes founder-audible identity + performance QD.
- No pitch or formant manipulation.
- Narration is generated as short story-beat stems.
- Strategic pauses are controlled by explicit inter-stem gaps, not by accidental TTS hesitation.
- Vocal mastering chain is consistent across podcast and YouTube.

## Final lane

1. Input narration stems, score(s), ambience/SFX, and `mix.json`.
2. Measure each narration stem duration with `ffprobe`.
3. Assemble exact narration timing from explicit producer-set gaps.
4. Apply a fixed corrective vocal chain (HPF, subtle warmth/mud/presence/air EQ, de-essing, gentle bus compression). Never pitch-shift.
5. Loop/trim score to the exact episode duration and apply transparent speech-keyed sidechain ducking.
6. Place SFX at exact event times with explicit gain and provenance.
7. Render a 48 kHz floating-point premaster.
8. Run EBU R128 / two-pass `loudnorm` mastering.
9. Output 24-bit WAV + 192 kbps MP3 + 192 kbps AAC/M4A.
10. Run QC and fail closed on loudness or peak failures.

## Loudness profiles

- Podcast stereo: **-16 LUFS integrated**, **<= -1 dBTP**.
- YouTube: **-14 LUFS integrated**, **<= -1 dBTP**.

Targets are not claimed unless measured on the rendered export.

## Sound design rules

Music and effects are scene-responsive, not generic filler. Examples include documented gunfire, fire/alarm textures, weather, engines, ship structure, radio/telephone, crowds, doors, footsteps, paper/documents, machinery, and battlefield ambience.

Every SFX entry carries provenance. Generated/reconstructed audio must never be represented as archival audio. Effects may not imply an event or condition unsupported by the evidence.

## Run

```bash
python3 src/master_audio.py examples/mix.example.json --profile podcast --out-dir build/podcast
python3 src/master_audio.py examples/mix.example.json --profile youtube --out-dir build/youtube
```

## Required final QD

A final episode/video is not ready merely because the render command succeeded. QD must audition the actual exported master on normal headphones/speakers and confirm:

- Bryan remains clear and dominant.
- Music is audibly present where intended.
- Required SFX are audibly present at the correct story beats.
- Ducking is natural.
- Strategic pauses feel intentional; no accidental TTS hesitation remains.
- No broken joins, clipped consonants, clicks, or tonal discontinuities.
- Measured loudness/true peak meet the selected profile.

## Fail-closed performance QC

The lane also rejects narration stems containing an unexplained internal silence longer than the configured threshold (default 0.70 seconds). Long story pauses belong **between** stems, where the producer controls them exactly.

Pause classes are explicit and testable:

- `punch`: 0.12–0.32 s
- `thought`: 0.25–0.45 s
- `reveal`: 0.50–0.75 s
- `chapter`: 0.80–1.60 s

The renderer exports isolated voice/music/SFX diagnostics and mathematically subtracts narration from the actual premaster. Required score/SFX fail QC if they are below the audibility floor or do not survive into the real mix.

## Source-quality ceiling

For a true high-end master, upstream narration should use the highest-quality lossless/PCM output available. The mastering lane cannot reconstruct detail discarded by a low-bitrate source. It will preserve and master whatever source it receives without pitch/formant alteration.
