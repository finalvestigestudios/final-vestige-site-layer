# R89 browser/preview verification — honest scope

**Local Chromium / Playwright probe (2026-11-03):**
- A real headless Chromium browser was launched using the installed `/usr/bin/chromium`.
- Direct navigation to the local `file:///mnt/data/fv_mind_r89/review.html` returned **`net::ERR_BLOCKED_BY_ADMINISTRATOR` at all 5 viewport sizes**, including actual media playback. Therefore **no playback or caption synchronization assertion is warranted**.
- Independent `page.set_content(..., java_script_enabled=False)` with the exact local `review.html` string rendered the static offline reviewer DOM. Viewports **360 / 390 / 768 / 1440 / 1920** had no horizontal overflow; each contained 1 native `video[controls]`, 1 `track[kind=captions]` and 6 visible transcript list items. **5/5 static viewport checks passed**.
- A 390px static screenshot was captured in the local offline reviewer artifacts. Its video rectangle is not proof of successful playback; relative local media cannot load via blocked file access.

**Native media checks:** FFprobe: H.264, 540×960, 480 frames at 12fps, 40.000000s. Original Python renderer and VTT Git blob identities match actual executed/local files; 6 VTT cues contiguous to 40.000s; ZIP integrity PASS.

**Not tested:** the actual `zen12-a.blocks.html`, `zen12-b.blocks.html` or `mind-hub-noncanonical.blocks.html` inside real WordPress/Gutenberg or a production browser; browser video playback, hosted VTT sync, Lighthouse, end-to-end tracking, live conversion, human usability, WCAG 2.2 AA/screen-reader acceptance or native Node test runner. Keep all release gates FALSE. Distinguish structural/adapter checks from real feature acceptance.
