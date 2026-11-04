# EX2 seven-chapter focus admission — release HOLD (2026-11-04)

Parent draft PR #924 exact SHA `40e20fbcc0b046dcc77fe323ad60131e8ebf0674`; independent branch. Frozen PR #49 remains untouched. No production, staging CMS, analytics, affiliate, or marketing changes.

## Reproducible failure / repair

The seven chapter navigation links and the header “Skip to the evidence room” target non-interactive `<h1>`, `<h2>` and `<section>` nodes **without** programmatic-focus support. In Chromium, activating a fragment link with the keyboard scrolls but leaves `document.activeElement` on `<body>`; assistive keyboard users lack a reliable, visible focused landmark. This matters for moving from the first screen to the authentic evidence and its source links.

The actual seven-chapter source now adds `tabindex="-1"` to exactly seven existing chapter targets. This is not a new Tab stop. A scoped `:focus-visible` indicator supplies a visible antique-gold outline, with system `Highlight` in forced-colors mode. All seven chapter links, the skip link, the hero, and the existing Focus action remain; no JavaScript is required.

## Independent executed browser evidence (not WordPress)

Headless system Chromium, JavaScript **disabled**, 3 viewport/height pairs: 390×844, 720×450 (small viewport **approximation**, not physical 200% zoom) and 1440×900. Controlled seven-target DOM reproduction, without production network traffic:

- Baseline targets lacking `tabindex`: **0/21** expected focused landmarks.
- Repaired targets with `tabindex="-1"` and visible focus rules: **21/21** targeted landmarks focused and visibly outlined.
- Receipt: `/mnt/data/fv_chapter_focus_browser_proof.json` (local run attachment; not a GitHub Action artifact).
- This proof validates the keyboard-fragment mechanism in Chromium, **not** whole-source/WordPress rendering.

A new committed `tests/verify_chapter_keyboard_focus.py` tests the full actual `index.html` + all six actual source stylesheets with external network blocked, JavaScript disabled and a 21-case seven-target keyboard admission. `--smoke` provides a synthetic negative control. **Its exact-source branch run and WordPress/Assembler qualification are not yet completed; neither is claimed PASS.**

## Business conversion relevance

**OFFER:** Existing, free 52-page Focus Fieldbook. **FUNNEL:** social/organic visitor -> monumental evidence -> investigate sources/observer -> contextual Fieldbook. **BLOCKER:** keyboard users activating chapter links may scroll without meaningful focus transition or visible locator. **CHANGE:** semantic chapter programmatic targets + keyboard focus ring. **EVIDENCE:** 0/21 vs 21/21 controlled Chromium; branch exact-source test remains gated. **OWNER:** interim homepage engineering; Claude retains live attribution and commerce; Grok/Praxxis own acquisition. No confirmed lead, paid order, or net revenue is inferred.

## Still mandatory before release

Native WordPress/Assembler anonymous rendering in *isolated* no-cost Playground or equivalent; all 72 exact published Margins; Jetpack/Focus protection; whole-document axe WCAG 2.2 AA (including known serious header finding); no-JS/touch/manual keyboard; physical 200% zoom; real media network transfers, provenance and reuse permissions; measured Lighthouse and independent QD/founder visual review. An isolated developer fixture is not WordPress.com Atomic/Jetpack parity. GitHub Actions failure before runners is not a code test result. Do not merge or publish.
