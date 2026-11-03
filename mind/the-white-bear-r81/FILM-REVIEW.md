# R81 original 40-second film — verification and hosting hold

**Film:** *The Bear You Can't Unthink* — original silent schematic white-bear illustration (not research footage; not a product efficacy demonstration). Produced November 2, 2026.  

**Actual local reviewer assets (not uploaded to WordPress or GitHub binary storage):**
- `the-bear-you-cant-unthink-40s.mp4` — **299,847 bytes**; SHA256 `d9c122a16d835079388b460e511a7b5adaf92d53be4088e69b7d24ea859150b3`
- `poster.png` — **33,332 bytes**; SHA256 `8e4c7f3f84cc25806c74999a77d9269709192c020a441b7de10c1825f3f2c865`
- `offline-review.zip` — **512,608 bytes**; SHA256 `823c03b4257f2dacceafed014ccb1d24c1eca740cacf8f7b3a19547fdf553747`
- `six-scenes.png` — original contact sheet, inspected for clipping and legibility.

**Source control:** `render_film.py` Git blob `f5b4aa38f3e7c4627f94ab95eac6c91df424c069` exactly matches local executed renderer's `git hash-object`; `film-captions.vtt` Git blob `c30611cb526735332d67cddebf69450aa27af3cf` exactly matches local VTT. Source script uses Pillow and ffmpeg; neither font binaries nor MP4 binary are committed.

**Actual native verification:** ran Python renderer and ffprobe. `40.000000` seconds, H.264, 540×960, 12 frames/sec, **480 frames**; poster dimensions 540×960; six VTT intervals cover 00:00:00–00:00:40 without gaps; ZIP integrity verified. Contact sheet actually viewed.

**Actual browser verification (offline stand-in, not WP staging):** `/usr/bin/chromium` via Playwright; localhost navigation blocked by administrator. Instead HTML document was injected through `page.set_content` and actual MP4 and VTT through data URLs. Static no-JS checks at **360, 390, 768, 1440, 1920 CSS pixels** passed (no horizontal overflow, native video controls, caption-track markup, complete six-cue transcript). Chromium decoded actual MP4 at duration 40, width 540, height 960. Actual native caption track contained **six cues**, with the correct third cue active at 15s. Mobile screenshot captured.

**Known limits:** data-injected testing does NOT prove first-party hosted playback, WordPress sanitizer compatibility, screen-reader experience or Lighthouse performance. No actual engagement or conversion experiment. No merchant rights. The WordPress candidate B intentionally shows a **poster + full transcript, not a fake playable media element**, until licensed first-party hosting and final QA. A is full text guide, same substantive core. Never represent a 40-second film as demonstrating Zen12 efficacy.

**Release blockers:** owner media hosting decision and CDN file rights; real host plus caption MIME and CORS validation; WP renderer and 5 widths; keyboard, no JS, screen reader, contrast/reduced-motion; core web vitals; founder-specific release approval. No production CMS mutation, mail, attribution or purchasing links performed.
