# EX2 — Single WordPress main landmark admission (2026-11-04)

**Release: HOLD; isolated PR stacked on #948 at exact parent `f248993e634352b0a23361012b91e4de72cde120`.**
This is a source-controlled WordPress/Assembler *integration* correction, not an additional chapter or a change to the live WordPress site. Frozen PR #49, Apollo PR #158, 72 published Margins entries, Focus Fieldbook/Jetpack, art direction, historical image source/rights inventory, campaign attribution and payment integrations remain untouched.

## Defect and constrained correction

`experience2/home-flagship/index.html` is valid **standalone** HTML, including exactly one `<main>`. Its verified Git blob is `71511fec93f724a3a2123cd863d654014f030d7e` and has not changed. The existing Gutenberg candidate generator copied the entire standalone body into a custom HTML block **inside** WordPress/Assembler's theme-owned `<main>`. This creates a second, nested main landmark in the WordPress render path. The previous admission harness used `!!root.querySelector('main')` as a positive assertion, so it would mistakenly accept a nested landmark as proof of correctness.

The generator now strictly requires the standalone source's single opening and closing main boundary, then substitutes ONLY the embedded copy with `<div data-fv-embedded-main="wordpress-assembler">…</div>`. Original source SHA stays intact, including all history, headings, seven chapter routes and Focus links. Six original CSS files contain no selectors depending on an HTML `main` element, so the substitution is not expected to change layout. In the actual isolated WordPress render gate, exactly one document `main` must exist, contain the adapted flagship, and have no nested `main`. A missing Assembler-owned main or another nested main fails closed.

**The CI/source test suite also contained three stale literal assertions** that would fail if run: a three-argument viewport callback after adding published-Margins input, a viewport-failure guard after adding anonymous-guest failures, and an outdated isolated return-type constant. These now check the actual committed runtime; a new static main-landmark contract and generator mutation tests were added. These are test-consistency fixes, not claims that the blocked CI ran.

## Executed independent controlled Chromium study (not WordPress staging)

A reproducible local Python/Playwright fixture models a WordPress outer main containing the same source `<main>` vs the adapted inner div, without any external HTTP fetch. Headless Chromium, JavaScript disabled, reduced motion enabled, measured **390×844** and **1440×900**:

| Check | Before (nested main) | Proposed adapted embed |
|---|---:|---:|
| Browser-accessible main landmarks | 2 | **1** |
| Nested `main` descendants in flagship | 1 | **0** |
| Preserved Focus destination count | 1 | **1** |
| Horizontal overflow | none | none |
| Pixel difference, full-page screenshots | — | **0 pixels** |

These tests establish only that the semantics of the controlled structure are corrected without a screenshot change. They **do not** prove the exact Gutenberg source has been saved and rendered in WordPress/Assembler, do not constitute axe/JAWS/VoiceOver certification, and do not measure real conversions or Lighthouse/CWV.

## Exact-source custody / next admission

Source-controlled changes are limited to the offline Gutenberg candidate adapter, existing Assembler runtime gate, and their two regression files. No new third-party media, network hosts, licensing claims, analytics, tracking, forms, purchases or UI chapters.

Next: run `python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_source_flagship_playground_candidate.py -v`, `... -p test_full_document_axe_gate.py -v` and `node --test experience2/home-flagship/qa/release-candidate/test_assembler_nav_native_fixture.mjs` on **this exact head**. Then complete Gutenberg Save → anonymous Assembler WordPress Playground rendering with all source hashes, actual image HTTP bodies/decodes, full-document axe and native navigation, 320/360/390/720/768/1440/1920 and physical 200% zoom, mobile Focus clickability, no-JS, keyboard, Lighthouse and human WCAG inspection. The WordPress.com Personal plan cannot create a native one-click staging clone; local Playground does not establish WordPress.com-host-specific/Jetpack equivalence.

Business hypothesis: fewer accessibility errors and more credible source/Focus navigation improve *qualified* reader experience; **no attributable confirmed signups, Payhip orders, affiliate commissions or net revenue were observed**. Claude owns production measurement and commerce, Grok/Praxxis own acquisition/independent editorial QA, founder retains all release and spending approval.

**No merge, deployment, production CMS/plugin/theme/navigation/settings write, affiliate activation, email, social posting, or spending authorized or performed.**
