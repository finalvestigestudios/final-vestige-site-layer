# R43 original film — executed offline proof (1 November 2026)

- **Actual film produced:** original, silent six-scene educational explainer `troxler-evidence-40s.mp4`, rendered with Pillow + FFmpeg. This is an OFFLINE review artifact, not uploaded to GitHub, WordPress, CDN, or merchant pages.
- **Reproducible exact source:** `render_troxler.py`, committed Git blob **e67911b9604fa6160c91215c9729a2d83b07b858**. Local `git hash-object` of the actually executed renderer returned the exact same SHA. Python/Pillow/FFmpeg process exited successfully.
- **Actual ffprobe output:** H.264, 540×960, 12 fps, **480 frames**, **40.000000 seconds**, **100,166 bytes**.
- **Actual MP4 SHA256:** `5d1e6bf19e858133635199c6f3d3e16d8361087e973ccaf87e7402e6143db873`.
- **Original offline PNG poster** generated from the MP4; all six scene-card source images assembled into a contact sheet and visually inspected. Titles, footers, body text and central schematic fit the layout at full 540×960. No borrowed footage/music, no staged product testimonials or user-experience claims.
- **VTT and full B transcript** now match the exact six original scene body texts and 0–6/6–13/13–20/20–27/27–34/34–40-second cues. Actual player cue synchronization **not browser-tested** because no hosted MP4 exists.
- **A/B invariant:** A and B remain identical outside the optional B `<aside class="film">` region. B has no `<video>` tag, fake play control, autoplay or external embed. The MP4 is not accessible from the live website.
- **Source QA prior to film update:** 13/13 actual committed readbacks, 48/48 assertions and 3/3 synthetic injected vendor-link mutations caught in isolated V8; 14th full article HTML independently created and inspected. After film status edits, rerun full source assertions and record exact final SHA.
- **Not executed:** production browser/keyboard/screen-reader/no-JS/a11y/CWV testing, hosted VTT cue synchronization, CI, conversion tracking, WordPress staging, actual Zen12 purchase, merchant fulfillment or affiliate activation.
- **No live changes:** WordPress navigation/settings/Jetpack signup/Focus welcome, PR #49, PR #172, Issue #150, Issue #174 all preserved. Explicit founder and partner release gates remain HARD HOLD.
