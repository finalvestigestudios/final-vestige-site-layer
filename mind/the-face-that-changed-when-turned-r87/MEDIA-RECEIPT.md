# R87 original media reproduction & verification receipt
**Scope:** Offline 40-second original schematic illustration. NOT a public video, not a product demo, not merchant creative.

- Title: *The Face Was Always Altered*. Reproducible source in `render.py`; original SVG in `original-film-poster.svg`; original VTT source in `original-film-captions.vtt`.
- Render command: `python render.py` using Pillow 12.3.0 and `ffmpeg` H.264; **no outside art/footage/downloads**.
- Local MP4: `the-face-was-always-altered-40s.mp4` in the offline review artifact, not yet GitHub/WordPress media. 40.000 seconds; 540 × 960; 12 fps; 480 frames; H.264 yuv420p; **223,231 bytes** by FFprobe.
- **Exact renderer Git blob identity:** `d95d6c96539bd17f5a5fc26724af909c84286dda`, matched to the locally executed `render.py` via `git hash-object`. Local SHA-256: `f589bf687a0e9d2b07e306579fcb941c1369aba5214fa603a49aab9edb431d0f`.
- **Exact caption Git blob identity:** `241204042afa6e97f43f4ed7c11e147302b7bee3`, matched to local `original-film-captions.vtt`; verified six consecutive intervals from 0 to 40 seconds.
- Offline review ZIP includes actual MP4, local poster PNG, contact-sheet JPEG, captions, the exact renderer and self-contained HTML5 no-autoplay reviewer. This ZIP is attached separately for founder review; binary MP4 is deliberately not added to Git history absent media-hosting approval.
- HTML5 reviewer has native `video controls playsinline preload="none"` and complete always-visible no-JS transcript. Source-controlled B candidate uses inline SVG poster and transcript only. It never claims embedded video is already hosted.
- Read-only native FFprobe and PIL rendering PASSED; ZIP integrity and caption time range PASSED.
- Localhost browser video playback request FAILED with `net::ERR_BLOCKED_BY_ADMINISTRATOR`; **not** a codec failure. Static Chromium `page.set_content` no-JS viewport checks PASSED at **360, 390, 768, 1440, 1920 pixels**, no horizontal overflow. Actual video browser decodability and track synchronization NOT verified; required later via first-party staging.
- Reproducible native Node test source `tests.mjs` was read back from authenticated GitHub and executed through a V8 JavaScript-compatible adapter: **19/19 passed**, with a mutation of native disabled control independently detected. Additional **45/45 exact-source structural assertions** passed. **Native Node itself was not run**, and GitHub Actions has not been invoked here.
- Media and buyer-guide release gates remain CLOSED. No WordPress file upload or change, Jetpack/subscription actions, active merchant URL or visitor telemetry.

**Security/accessibility:** No scripts, tracked pixels, remote embeds, autoplay or user identifiers in the offline playback HTML. Transcripts stay visible; original vector artwork is not a photograph of a real person or a journal figure. Pending manual screen-reader, contrast, Gutenberg sanitization, hosted VTT and actual performance checks.

**Source research:** https://doi.org/10.1068/p090483 ; https://doi.org/10.1068/p6659 . The illustration is schematic and is not represented as a controlled psychology experiment.
