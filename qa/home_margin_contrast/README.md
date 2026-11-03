# Hidden in the Margins — independent contrast remediation fixture (DRAFT / HOLD)

**Scope:** A source-controlled **candidate CSS only** and self-contained offline QA, developed independently of the active homepage editorial lane. No production patch, injected stylesheet, plugin, WordPress write, merge, build/deploy, subscription or network request is part of these files. This is a **review fixture, not release authorization**.

## Trigger and evidence

On Nov 2, 2026 the homepage lead's authenticated **real anonymous public Chromium** [Issue #150 / draft PR #739](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/739) reported a serious axe-core `color-contrast` violation on `span.fv-margin-strip__item` at 390px and 1440px; the CI *job* passed, the accessibility *gate* failed. Fresh read-only WordPress saved page 6 confirms the 72 entries, `color:#d8d2c7` on `background:#0f100f`, and keyframe `opacity:.46` / `.42` with blur while visible. That is a plausible mechanism, not established root cause of the original axe observation. With the original palette on its solid strip background, contrast is approximately **12.68:1 at full opacity** and around **3.49:1 / 3.10:1 at .46 / .42**, below the 4.5:1 normal-text threshold. Real browser CSS inheritance/overlay may alter the result.

## Candidate

`margin_strip_candidate.css` deliberately scopes an **override prototype** to `.fv-margin-strip--rotator .fv-margin-strip__item`. It preserves the 360-second loop, 72 x 5-second stagger and first-fact reduced-motion fallback, and replaces gradual alpha/blur with discrete opacity/visibility changes and constant sharp high-contrast glyphs whenever visible. The intended visual difference is **brief cuts instead of crossfades**, a founder/art-direction decision, not an approved styling change. This is not a literal drop-in for WordPress until it is reconciled against the current live CSS and approved.

## Evidence and reproducibility

Run standard-library guard with `python -m unittest -v test_margin_contrast.py` (10 tests: static contrast, no intermediate-alpha keyframes, cadence, reduced motion, mutation detection, no network). Optionally run `python test_browser_margin.py` with Python Playwright and Chromium available; it builds a synthetic 72-item local document, samples **11 animation instants** at **320/390/1440**, verifies every visible item has computed `opacity=1`, `filter=none`, and asserts no document horizontal overflow; then checks one visible entry and no JavaScript in reduced-motion mode at those widths. The local fixture deliberately uses generic placeholder entries, not copied editorial content. These tests **cannot** claim live hosted WCAG, perceived legibility on actual imagery, screen-reader semantics, image rights, Focus signup, mobile CWV, source/CSP compatibility or QD approval.

## Safe next gates for homepage owner and QD

1. Review the animation art direction and confirm rights/authorization for the already-published homepage independently. Never make an unreviewed live CSS change.
2. Integrate a *copy* into a disposable isolated WordPress/Gutenberg fixture, rerun exact-host anonymous tests at 390/1440 and across animation time; separately test hover/focus pause, 200% zoom, forced-colors, reduced motion and no-JS; record axe pass/fail, incomplete rules and measured colors. Avoid sampling only a fully opaque frame.
3. Independently conduct manual NVDA/VoiceOver, keyboard and physical-device verification and obtain founder/QD publication authorization. All unresolved image-specific rights, hosted performance and Focus delivery gates remain HOLD.

Do not edit frozen homepage PR #49, active #739, the published WordPress page, navigation, or subscriber settings as part of this standalone QA.
