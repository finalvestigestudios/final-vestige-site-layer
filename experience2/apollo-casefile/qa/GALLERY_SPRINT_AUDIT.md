## Verified source-linked gallery and local accessibility audit — 2026-10-30

This stacked draft adds a separate **six-record source gallery**, not archival photographs. It reuses the six already-verified NASA metadata URLs and links every record back to its documentary stage and evidence limitation. No NASA image files are downloaded, copied, or served, and no Atlas points are fabricated.

### QA run evidence (local headless Chromium, not WordPress)
- Playwright interaction and responsive smoke PASS at 320, 360, 390, 768, 1024, 1440, 1920. Gallery has 6 records at all widths; 6 history stages and 6 Atlas posts remain visible.
- Keyboard/Enter opens both stage and gallery native source drawers, gallery returns directly to its stage, search/filters and empty/reset state work. Missing or throwing IntersectionObserver and disabled JS preserve all chapters, gallery and Atlas.
- New touch-geometry smoke: 66 visible interactive targets tested at each width; no rendered clickable target smaller than 24px in either dimension after CSS adjustment. Labels, unique IDs, aria-labelledby targets, HTTPS source URLs and skip-link keyboard focus pass the *limited local checks*. **Not an axe audit or WCAG conformance certification.**
- Synthetic local Playwright metrics from in-memory, no-photo prototype: LCP ~180ms, CLS 0. These are **not p75 field Core Web Vitals or WordPress performance numbers**.
- Renderer build SHA-256 is `beb070b214104316b75863121b677f67ed3340330d5a30d8ef16cd6c2453ea3e`, checked twice byte-identical locally. Screenshot SHA-256/byte sizes are recorded in `qa/QA_RESULTS.json`, but PNG binaries remain in local screenshots and are not stored in GitHub (oversized artifacts).
- `qa/axe_runner.py` is a **real axe-core evaluator** gated on `AXE_JS_PATH`. It was attempted, but not run: axe bundle unavailable offline (`AXE_NOT_RUN`). Do not report an axe pass. Independent QD, actual WordPress staging, manual Safari/VoiceOver/NVDA, media-bytes and legal review, and hosted CI are outstanding.

Exact source governance: NASA Board https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; NASA image metadata pages are enumerated in records.json. NASA official [usage guidelines](https://www.nasa.gov/nasa-brand-center/) bar implying NASA endorsement and require scrutiny of third-party/photo-person rights.

Stacked on the unmerged [Apollo casefile PR #181](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/181); independent from [Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), frozen homepage PR #49, and any WordPress release.