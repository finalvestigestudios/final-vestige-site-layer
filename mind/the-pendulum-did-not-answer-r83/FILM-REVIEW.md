# R83 ACTUAL offline film review — 2026-11-02

**Title:** The Hand Below the Pendulum. An original 40.000-second silent educational animation, **not** an experimental reconstruction or product endorsement. Source-controlled `render_film.py` exactly matches the local actually executed renderer: Git blob `c2fceae017f08b3ace0ecbcf8d76d2521455c4b2` equals local native `git hash-object`. Pillow 12.3.0, local Lato OS fonts and ffmpeg used. No font files, stock art, merchant videos or purchased assets included.

## Offline artifacts (conversation review package, NOT published/hosted nor stored as binary in Git)
- `the-hand-below-the-pendulum-40s.mp4` SHA256 `4d447f7284d2de5f17bc7517df84d0334c7ec2194c8edd71cfcd6bbfaeb3da61`, **173,707 bytes**. ffprobe **H.264, 540×960, 12fps, 480 frames, duration 40.000000 seconds**.
- `poster.png` SHA256 `78ed3bfc6810fc22cbbe13f7a6dccedf5e7001ea2b507ab11f7dba9bd6f635df`, Pillow verified **540×960**.
- `contact-sheet.png` SHA256 `8ef51e501f5a572ec1b204503135c20cdbda8d71ece21756c263369e8b26942b`, sampled six scenes, **810×960** and visually inspected.
- `offline-review.zip` SHA256 `9f91afa4060509aa3d1ee459fcdd33bb88dd9ee2e70ebbcbc337083ffb5e9`, ZIP integrity **PASS**, 7 original assets: MP4, poster, contact sheet, `film-captions.vtt`, exact renderer, static offline HTML5 player and review README.
- Six contiguous timecoded WebVTT cues: **0–6, 6–13, 13–19, 19–26, 26–33, 33–40 seconds**; caption content matches reviewer transcript in meaning. No autoplay, trackers or external embeds in review player.

## Actual executed checks
- Native local Python/Pillow film render **PASS**.
- Native ffprobe video identity/duration/fps/frame-count **PASS**.
- Native Pillow poster and contact sheet dimensions **PASS**.
- Local hash matching source-controlled Git blob **PASS**.
- ZIP integrity and contents **PASS**.
- Visual six-scene contact sheet and poster review **PASS**.
- Static browser playback checks **BLOCKED**: Chromium/Playwright `page.goto` was denied by the sandbox's `net::ERR_BLOCKED_BY_ADMINISTRATOR` for both loopback localhost and data: URLs. Do **not** claim 5/5 browser viewport, video decoding, caption sync, keyboard WCAG, or hosted WordPress testing from this session. Browser test harness `browser_qa.py` is in the offline working folder but not included in the release package; the failed check is honestly recorded.
- Source-structure and synthetic privacy checks against exact committed GitHub sources **28/28 PASSED** in V8/JS evaluation, not native Node. Separate `test.mjs` exists but no native Node/Actions execution confirmed.

## Website release rule
The B WordPress Custom HTML remains a **poster + complete transcript preview only**, despite an actual offline MP4 now existing. No active `<video src>`, merchant link, CMS asset upload or outbound tracking is in either variant. A real first-party video source should only be added after approved hosting, native captions and accessibility/security tests, and founder release authorization. The film does not imply any product-specific Zen12 benefit.