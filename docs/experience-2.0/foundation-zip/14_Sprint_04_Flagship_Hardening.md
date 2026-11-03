# Sprint 04 — Apollo 1 flagship progressive-enhancement hardening

**Status:** implemented and browser-tested locally; isolated R&D only.

## Confirmed edge case

The original desktop prototype would add `.enhanced` even when the browser lacked `IntersectionObserver`. Its CSS then hid the six chapter-specific figure elements and showed only a sticky evidence viewer that never advanced beyond exhibit 01. That could silently show the wrong source image as visitors read subsequent chapters. This is a credible mismatch between evidence and narrative, not just an animation glitch.

## Applied fix

- Require `IntersectionObserver` before applying the enhanced reading mode. If unavailable, retain six normal source figures with full alt text, captions and original NASA record links; no fake/stale viewer state.
- The existing thrown-observer fault-injection test still verifies that a partially initialized enhancement fails open to the static article.
- Added a real Chromium test for the **missing API** path (different from the existing exception scenario).
- Connected the Apollo 1 source inspector to an exact source record in the Research Desk, via local relative URL and anchor. The prototyping package's extraction layout preserves that link; this is not a live WordPress route.
- Added a footer entry point to the full Research Desk prototype.

## Validation

- Real Chromium at 360, 390, 768, 1024, 1440 and 1920; no overflow, six chapters, primary photo alt text and source anchors; source modal, focus return and keyboard source link checks pass.
- No JS: six normal source figures remain visible.
- Missing observer API: no enhanced class; six figures and six source links remain available.
- Observer constructor crash: same static fallback; no dead modal buttons.
- Cross-prototype relative filenames and specific source card anchor verified on disk.

**Still open:** real loaded-image visual QA, source media rights, screen-reader testing, mobile Safari, WordPress staging, CWV, independent QD and hosted CI. No production code touched.
