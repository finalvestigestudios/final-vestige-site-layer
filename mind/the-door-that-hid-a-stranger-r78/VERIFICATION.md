# R78 verification, limitations, release gates — 2026-11-02

## Verified artifacts and test execution

- **36 of 36** exact source-controlled `tests.mjs` bodies passed against **independently fetched GitHub file contents**, executed through a small V8 `node:test`-compatible adapter (the native-Node imports and file reader were adapted; assertion behavior was replicated). **This is NOT a native `node --test` run** and must not be represented as hosted CI or complete production QA.
- **Eight of eight actual adversarial mutations were detected** in the above executable test harness: removing native disabled button; deleting near-action disclosure; injecting live Zen12 checkout href; switching outbound attribution to enabled; altering the B guide relative to A; inserting a signup form; adding a fake matrix source; and truncating the film transcript's last cue. An initial no-op “guide mutation” and an undetected caption mutation were corrected before the final 8/8 test; this is not concealed.
- **Original 40.000-second film actually rendered locally** via Python/Pillow/ffmpeg with original schematic artwork. Native `ffprobe`, Python, caption and ZIP integrity assertions passed. H.264, portrait 540×960, 12 fps, 480 frames, silent, 106,216 bytes. MP4 SHA256 `c4983447e6acf6e57835f46d6dd2eecc4fefa6c6ee05ebff874a1b16a2a6dff9`.
- Film `offline-review.zip` with **7 actual review files**, ZIP integrity passed, SHA256 `a3aa2777ea78660761cb346895ff01eed331c219796c5d9d35cc11b3deb5312f`. Poster, contact sheet, six original scenes, original MP4, exact renderer, exact VTT, HTML5 offline review player; video binaries not in GitHub or WordPress.
- **Exact source-controlled film parity:** script Git blob `f5801f4172a69559ce4bb029e5709b3c6a8d4c2e` equals Git blob of locally executed `render_door_film.py`; caption Git blob `7d37c3319a517d0484e2181ba7f4e40c020c5027` equals the actual local `film-captions.vtt`. Caption cues 00:00–00:40 contiguous.
- Actual **headless Chromium static DOM layout checks passed 5/5** with JavaScript disabled using `page.set_content` for the *offline review player markup only*: widths 360, 390, 768, 1440, 1920 px; no horizontal overflow; `video[controls]`, `preload=none`, single captions track, accessible six-item transcript, no autoplay. Browser navigation to `file:` and `http://127.0.0.1` was blocked by the environment; **browser check does NOT verify video file loading, caption synchronization or WordPress theme rendering.** A 390px static player screenshot was recorded locally.
- Authenticated WordPress **read-only** list returned 61 published investigations and 79 published pages; inspected actual source-oriented Puységur page #1377 and original Focus fieldbook page #1579. No CMS writes.
- Source register: **22 exact URLs**, **39 claim/permission decisions**, **12 false activation gates**. Two real sales-page variants embed the byte-identical full guide; the B figure is optional, and neither version has affiliate purchase anchors or tracking.

## Current safety and compliance posture

**HARD HOLD**. No claimed real conversion results, real product use, medical/wealth guarantees or merchant authorization. No activation of affiliate earning URLs, email/TikTok/website partner links, visitor data, third-party embeds, extra forms, scripts, autoplay, cookies or email funnels. First-party media not hosted. Existing Focus/Jetpack welcome and subscriber list untouched. Draft guide contains a prospective commission disclosure immediately before a native-disabled CTA. Independent article has no commercial link.

## Still required, independent of this sprint
1. Written Final Vestige-specific Inspire3 acceptance and precise approved Zen12 destination, authorized creative use and website/TikTok/email rights. Public affiliate recruitment is NOT permission.
2. Verify current merchant checkout, term/refund details and purchaser-data-sharing policy; `https://inspire3.com/terms/` was inaccessible. Legal/privacy decision before accepting any merchant buyer information.
3. Independent editorial and claims substantiation review (FTC health/endorsement), and buyer-facing compliance approval.
4. Review exact edited WP Gutenberg sanitizer output and CSS in staging; WCAG 2.2 AA, keyboard, NVDA/VoiceOver, responsive layouts, Lighthouse/LCP/CLS/INP.
5. Upload/host MP4+VTT first-party only with approval, test actual caption synchronization and poster fallback, and verify no heavy network preloads or autoplay.
6. Execute committed native Node suite in exact repo checkout, inspect GitHub Actions/CI status, and pre-register a lawful privacy-reviewed A/B experiment before claiming lift.
7. Explicit founder release approval before any publication, merging, deployment, CMS edits, menu changes or affiliate activation.

## Separation and handoffs
Homepage flagship PR #49 / Issue #150, canonical Mind hub PR #172, independent Site QA Issue #126, Dispatch Issue #174 and all six planned newsletter drafts remain unchanged. No newsletter content or Jetpack configuration was edited. Handoff: **QA** should review seller/refund language, disclosure vs CTA, WordPress sanitizer/a11y, actual MP4 hosting; **art lead** should treat the alternate Mind hub as noncanonical and review visual direction only; **Dispatch** must keep Zen12 / Total Focus buyer-guide email slots on HOLD_MERCHANT with no links, no sends, no changes to existing Focus welcome.

This record distinguishes *executed* checks from *unverified* deployment prerequisites.
