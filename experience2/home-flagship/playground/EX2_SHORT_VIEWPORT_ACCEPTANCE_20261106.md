# Experience 2.0 — short-viewport first-screen review (2026-11-06)

**Status: DRAFT ONLY / NO WORDPRESS RELEASE.** Parent: draft PR #1288 at exact head `8b2b4008ed1988031e97a57e50f8ffbbd5e686d8`. Frozen PR #49 remains untouched. Source of truth: Issue #150; commercial charter Issues #818/#820. Apollo R&D stays in PR #158. No WP, analytics, subscription, production theme, publishing, merge or affiliate writes.

## Problem and controlled change

At a **realistic 390 × 667 CSS-pixel browser viewport**, the existing exact-source static candidate's contextual **Explore the free 52-page Focus Fieldbook** action began at **y=712.97**, entirely below the initial screen. A 900px test viewport concealed this short-viewport problem. The masthead Focus link remained available, but the second action supporting the flagship editorial promise was below fold. This review-only CSS adjustment reduces mobile **staging-label, masthead and chapter-trail vertical chrome**, and gently tightens opening whitespace, without compressing copy size, clipping evidence, or moving historical records.

| Static Chromium viewport | Before Focus y | Proposed Focus y | Difference | Important result |
| --- | ---: | ---: | ---: | --- |
| 320 × 568 | 782.00 | 684.00 | -98px | Contextual CTA still below fold; masthead CTA visible |
| 360 × 640 | 739.98 | 641.98 | -98px | Contextual CTA remains below fold; masthead CTA visible |
| **390 × 667** | **712.97** | **614.97** | **-98px** | **44px-tall contextual CTA now fully visible (bottom 658.97)** |
| 390 × 844 | 712.97 | 614.97 | -98px | Earlier contextual CTA |
| 768 × 900 | 582.61 | 582.61 | 0px | Larger layout preserved |
| 1440 × 900 | 830.02 | 830.02 | 0px | Desktop preserved |

The `DESIGN CANDIDATE · NOT LIVE` banner remains visible and the chapter trail retains native links even without JavaScript. No change to historical narrative, order of seven chapters, underlying inline image references, original archival folio, 72 Margins records, mobile Focus URL, Jetpack signup or tracking implementation. No additional chapter, affiliate URL or unsupported merchant claim.

## Verified code identity and tests

- Parent Blueprint Git blob: `03441eccfa9e64003321e205bc3671017db75932`.
- Updated Blueprint Git blob: **`455c6cccbf8a00e6ecc4c2524775010d7ee1762c`**, computed from the actual replacement bytes and confirmed by GitHub contents API.
- Only the PHP Blueprint's inline CSS heredoc was appended; existing HTML, JS, public historical text, other Blueprint steps and media tags were untouched.
- Source-exact local static Chromium comparison against the original Blueprint: **44 passing browser scenarios**, including 10 widths/heights × JS/no-JS before and after, plus reduced-motion and 200% CSS-zoom cases. The local test retained the actual Blueprint HTML/CSS/JS and aborted all media network requests.
- Committed fail-closed executable `verify_short_viewport_browser.py`: **18/18 PASS locally** across 7 widths × JS/no-JS, reduced motion and 200% CSS zoom. Tests 72 margins, 7 chapter links, 5 Focus references, no document overflow, minimum 44px height for the key navigation/CTA targets, preservation of the non-live label, and actual Franklin selector/case-button interactions.
- Screenshots of **before** and **after** 390 × 667 and after 390 × 900 / 1440 × 900 were generated and visually inspected from that exact extracted source. Artifact package distributed to founder outside the repository; image pixels are not claimed to represent hosted WordPress.

## Safety, accessibility and rights limitations

**This is NOT WordPress/Assembler execution.** In this runtime, WordPress Playground CLI couldn't be installed (no registry DNS access), and WordPress.com Personal does not provide a native staging clone. The only connected WP site is production ID 256784396; it was read only. No source-controlled fixture can establish WordPress.com Atomic-specific headers, Jetpack function, subscribers, external redirects, consent, hosted LCP/INP/CLS, or user conversions. Real hosted browser axe/WCAG 2.2 AA, Safari, authentic loaded-source image transfer bytes and Lighthouse/CWV remain **NOT TESTED**; no certification implied. Test Chromium bounds and no horizontal scrolling are insufficient by themselves for accessibility conformance.

Image rights remain independently gated: Apollo photograph may not imply NASA endorsement; Franklin hero is a labeled editorial typesetting, not a facsimile of the original; the capture-level NYPL permission is unresolved and its map remains excluded. See the source/rights ledger in PR #1237 and consolidated review #1258. Media network is intentionally blocked in this local fixture, so no downloaded-byte assertion.

## Conversion decision

**Offer → step → blocker → experiment → evidence → owner:** Free 52-page Focus Fieldbook → qualified historical homepage visitor reading the opening promise → short-screen contextual CTA below visible area → review-only compact composition → **98px earlier; complete 44px action visible at 390×667**, without sacrificing the primary evidence CTA → interim homepage engineer + independent QA. Claude/Focus workstream owns verified opt-in, checkout and attribution. Grok/Praxxis own creator acquisition. Founder owns all release decisions.

**No verified subscriber, paid purchase or net revenue improvement is claimed.** Funnel measurement of qualified `asset_id`/campaign sessions through confirmed subscriber/confirmed orders/refunds/net revenue awaits existing commercial engineering; no new instrumentation is included here.

## Admission gates still outstanding

1. Execute full unified seven-chapter Blueprint in **isolated WordPress Playground with pinned Assembler**; inspect actual screenshots at 320/360/390/768/1440/1920, at short heights and 200% zoom, no-JS/keyboard/touch/reduced motion. Never import subscribers or production database.
2. Independent axe-core/WCAG 2.2 AA audit, real image network response/bytes/decodes/hashes, Safari when available, and measured Lighthouse/CWV. Fail closed when tools missing.
3. Verify actual hosted Jetpack/Focus opt-in and genuine paid-order attribution independently. Playground cannot certify hosted Jetpack.
4. Exact-head independent QD PASS and working CI, followed by explicit founder release approval. **Release remains HOLD.**

