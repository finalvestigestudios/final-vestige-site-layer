# Mind & Perception Studio — Milestone 79: executed verification record

**Run:** 2026-11-02 · **Branch:** `feature/mind-visible-gorilla-zen12-evidence-r79-20261102` · **Scope:** added-only `mind/the-visible-gorilla-r79/` · **Release:** DRAFT / HARD HOLD.

## Proof from executed original sources (not assertions about unrun CI)

**GitHub exact committed source read-back via authenticated connector:** `tests.mjs`, `attribution.mjs`, `zen12-guide-core.html`, variants A/B, `investigation.md`, `claim-source-matrix.json`, `film-captions.vtt`, `render_film.py` were read by their Git blobs, not inferred from a summary. Recorded blobs:

- Tests `52f65b841f2a7d74a09690e1fbb88bddb8753edd`
- Attribution `6a9bbef0dea0eec73c3592816300e2cd6c6a86be`
- Guide core `85a9a095120a5e1678788ac930a571d5e9de0a71`
- Variant A `b39ae0249fadc2b2f029826cfc9aaab723a7eecd`
- Variant B `000444574449a39d0579ff8f0fb49ed5d2faf24d`
- Investigation `8232ad44cd9210c4187e7bb6c6826c0ac08ee0b5`
- Matrix `5f751eb7de4a8b5c8fc0bc906fb1e85ad3d27a10`
- WebVTT `2f48eea83e8814d3497775ca39cdd13262aa6791` (matches actual local captions Git blob).
- Full native renderer `12be1f383c4496addc5cb60b44ccea07b308c68f` (matches exact locally executed script Git blob). Initial incorrect 7-minute VTT timing was **found and corrected** before this verification. Final six intervals cover exactly 0–40 seconds.

**V8 JS-compatible adapter against GitHub source:** 10/10 committed `tests.mjs` test bodies PASS. Thirteen further independent checks PASS, total **23/23**. Includes complete byte-identical A/B guide, native disabled button in both positions, adjacent commission notice in both, no live purchase links / scripts / iframe / form / video autoplay, B-only original six-cue transcript, 21 real source URLs, 48 matrix decisions, 12 FALSE release gates, no collecting real visitor data, native categorical validation and n<20 suppression. **Six adversarial implementation mutations detected**: native disabled removal, near-CTA commission notice removal, checkout link injection, new subscription form injection, guide divergence, tracker insertion. This is **NOT native Node invocation or hosted GitHub CI**; those remain unverified.

**Native video engineering:** Python Pillow + FFmpeg renderer ran locally, ffprobe confirms **40.000 s, 540×960, H.264, 12fps and 480 frames**. Six contiguous timestamped VTT captions validated with Python. Original PNG poster validated at 540×960; archive `zip.testzip()` PASS; packaged VTT bytes equal actual local caption source. File SHA256: MP4 `a543298de88832bdd91fbc20147fd3158c5634a1b93fc1f2d9c9db6cf6396246`; poster `9c9a0b4edee13502006ff3d237194fb25443f49c8314f3cf5ce80bd6e9a69d78`; ZIP **`2dc8d66f6a70ec8757deaec752d4dc241702b3c7a41f3f71358089217f778345`**.

**Actual headless Chromium:** system `/usr/bin/chromium` was used with JS off and offline review player's HTML `page.set_content` to verify **5/5 responsive widths 360/390/768/1440/1920**, no horizontal overflow, actual native video-controls DOM, one caption track, no autoplay, preload none and complete no-JS transcript. Browser `file://` navigation is admin-blocked (not a production defect). A second Chromium run injected the *actual 103,897-byte MP4 and actual VTT* as `data:` sources into an HTML5 player. Browser returned duration **40**, video dimensions **540×960**, readyState **4**, **one text track with six cues**, and at t=14.5s the expected active caption `AN UNEXPECTED VISITOR A LARGE SHAPE CAN STILL BE MISSED.`. **This is an actual local-data video/caption playback test, NOT hosted WordPress rendering or first-party CDN verification.**

**Authenticated WordPress READ-ONLY:** 61 published investigation posts and 79 published pages; published Puységur #1377 and existing Focus #1579 read without changes. No live CMS write, email, subscription, media upload, tracking, merchant click or deployment occurred.

## Still unverified
- Full native Node CI / hosted GitHub workflow at exact final commit; WordPress Gutenberg sanitization/staging/theme, accessibility audit including real screen-reader + keyboard, Lighthouse/Core Web Vitals; actual first-party hosted video and captions; external merchant current legal refund terms, checkout submission and data practices.
- Final independent article/product source review, written FV-specific Inspire3 affiliate acceptance and authorized earning-link/channel permissions (website, TikTok, EMAIL separately), permissible creatives, buyer data privacy, and explicit founder publication approval.
- No conversion experiment has actually run. Video lift remains only a **test hypothesis**. Affiliate purchases cannot be inferred from an outbound intent event.

## Publication firewall
The only source-repo changes are under this new directory. Homepage PR #49 and agent-owned Issue #150, authoritative Mind hub PR #172, site QA #126, Dispatch #174, and existing Focus/Jetpack subscriber path are not modified. Source draft A/B and hub are NOT live WordPress drafts or published site routes. All 12 activation/release gates remain false. **DRAFT PR ONLY, no merge, no deploy.**

**Key links:** https://doi.org/10.1068/p281059 ; https://doi.org/10.1177/0956797613479386 ; https://doi.org/10.1073/pnas.2214930120 ; https://zen12.com/hnp ; https://zen12.com/about ; https://zen12.com/research ; https://zen12.com/getstarted ; https://inspire3.com/privacy/ ; https://doi.org/10.1371/journal.pone.0286023 ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
