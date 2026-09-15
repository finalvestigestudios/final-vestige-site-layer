# Final Vestige Podcast — ElevenLabs Egress Bridge

This lane retrieves **already-generated** ElevenLabs Flow TTS media by exact immutable generation ID. It exists so Final Vestige never has to regenerate approved narration just to move bytes between systems.

## Safety invariants

- Never calls an ElevenLabs synthesis endpoint.
- Accepts an exact selected-generation manifest.
- Fetches each generation using `GET /v1/flows/text-to-speech/{generation_id}`.
- Requires `status=completed`, exact returned generation identity, and audio MIME type.
- Downloads the short-lived signed media URL immediately but never persists or logs that URL.
- Rejects unsafe filenames, duplicate generation IDs, missing files, implausibly small files, and duration drift beyond the manifest tolerance.
- Emits per-file SHA-256, byte count, duration, source generation ID, and a final ZIP SHA-256.
- API credentials exist only as GitHub Actions secrets and are never committed or printed.

## POD-001

The governed manifest `manifests/pod001-selected.json` contains the exact 56 selected narration generations for **The Textbook Found Open in the Ruins | New London, 1937**. It preserves the five approved retakes (S12, S22, S50, S52, S56) and keeps the original S21.

## One-time founder setup

In GitHub, add a repository Actions secret named:

`ELEVENLABS_API_KEY`

Use the ElevenLabs API key directly in GitHub's secret UI. Never paste it into ChatGPT, an issue, a commit, Notion, logs, or screenshots.

After the secret exists, the AI control lane can commit a tiny file under `tools/podcast-egress/run/` to trigger the governed POD-001 egress workflow. The workflow returns a GitHub Actions artifact containing:

- `POD001-selected-narration.zip`
- `POD001-selected-narration-receipt.json`

The ZIP then becomes the input to the deterministic mastering lane. No new TTS spend occurs.

## Local invocation

```bash
export ELEVENLABS_API_KEY='set-outside-source-control'
python3 egress.py \
  --manifest manifests/pod001-selected.json \
  --out-dir build/pod001/stems \
  --zip build/POD001-selected-narration.zip \
  --receipt build/POD001-selected-narration-receipt.json
```

`ffprobe` must be installed so duration readback is measured from the downloaded bytes.
