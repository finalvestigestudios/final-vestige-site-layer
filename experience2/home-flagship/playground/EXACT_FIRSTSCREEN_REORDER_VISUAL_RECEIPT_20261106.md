# EX2 exact-source first-screen lift — 2026-11-06 — REVIEW ONLY

**Parent source:** PR #1282 exact HEAD `1857968e8b81bf7c7fcf47de79e9637c56c2641d`, Blueprint Git blob `d6f9efe9e7cf0e82c3362f730f9476018a02297e`.

**Change:** Relocate the entire unchanged 72-record `Hidden in the Margins` rail from the *top of the document* into the source-controlled seven-chapter review shortcode **between the opening hero and chapter 02**. The historical fragments and all source notes remain present, scrollable, keyboard-focusable and readable with no JavaScript. Preserve optional motion and reduced-motion behavior. No new chapters, images, affiliate offers, instrumentation or external dependencies.

**Reason:** The exact original candidate's top rail occupied about **220 CSS px at 390px**, ahead of the founder's visual promise. At 390×900 the contextual hero Focus action started at **y=932.97** (off screen). At 320×900 it started at **y=1002**. The conversion destination existed, but competed with above-the-fold archival material and review chrome.

## Measured BEFORE → AFTER, exact source (Chromium static local rendering)

| Width, 900px viewport height | Baseline contextual Focus CTA top | Candidate CTA top | Improvement | Candidate nav Focus CTA top |
| --- | ---: | ---: | ---: | ---: |
| 320 | 1002px | 782px | 220px earlier | 131px |
| 360 | Browser measurement in attached local receipt | Browser measurement in attached local receipt | approximately 220px | 131px |
| 390 | 932.97px | 712.97px | 220px earlier | 131px |
| 768 | 772.61px | 582.61px | 190px earlier | 84px |
| 1440 | 948.02px | 830.02px | 118px earlier | 84px |
| 1920 | 972.09px | 854.09px | 118px earlier | 84px |

These measurements are **browser observations**, not conversion uplift or CWV field data. A 900px test viewport does not prove visibility on a shorter phone. The 44px masthead Focus CTA remains the immediate mobile alternative.

## Reproducibility and admission

- Original Blueprint exported read-only from authenticated GitHub, byte-for-byte Git blob hash confirmed locally.
- Exact embedded PHP plugin extracted, syntax checked with PHP 8.4; JavaScript checked with Node 22.
- Proposed Blueprint regenerated; resulting local Git blob **matches GitHub committed blob** `03441eccfa9e64003321e205bc3671017db75932`.
- Actual (not synthetic) PHP-heredoc HTML, CSS and JS tested in **native Chromium** static wrapper; seven widths (320/360/390/768/1024/1440/1920) for BOTH baseline and candidate; no document horizontal overflow.
- 18 browser cases PASS: 14 viewport cases and JS interactions, no-JS, reduced-motion and CSS-zoom 200% candidate cases. Real cases exercised chronicle tabs, case selector, perception frame switch and deliberate motion opt-in.
- Source admission verifies seven chapter anchors, 72 public records exactly unchanged, two archival images, five Focus URLs; nine deliberately modified cases rejected using the committed source verifier.
- Local screenshots: 320/360/390/768/1024/1440/1920 first-screen before and after, plus 390/1440 full page, browser results JSON, Python test and extracted code in founder evidence bundle.

## Non-negotiable limitations

**Not WordPress runtime/staging.** WordPress Playground/Assembler PHP theme rendering, real WordPress scripts and CSS cascade, Jetpack signup, first-party archive image downloads, actual CDN-selected bytes, axe-core (unavailable), screen-reader WCAG 2.2 AA, Lighthouse, Safari and field CWV all remain **UNTESTED**. The browser fixture adds only a local `<main>` wrapper; no claimed WordPress markup parity beyond the source. Media requests were intentionally aborted in the offline fixture, so images cannot be certified.

**Rights:** No media substitutions; Apollo 473 and Franklin 474 references unchanged. NYPL 1258 remains excluded pending specific digital-capture rights confirmation. Historical record text preserved; no fabricated sources.

**Conversion experiment:** Offer = free 52-page Focus Fieldbook. Step = homepage evidence → contextual action. Blocker = first-screen displacement. Change = postpone 72-record rail until AFTER hero. Evidence = actual exact-source position gain, no layout overflow, preserved routes. **Business impact unknown**: only verified lead and paid-merchant order reports can establish new net revenue.

**Owner:** interim homepage engineering, read-only QA; Claude owns attribution/checkout; Grok/Praxxis retain social acquisition. No advertising activation, spending or live changes.

**Release HOLD:** frozen PR #49 untouched. No merge, production page/theme/navigation/configuration write, WordPress plugin install, affiliate activation, or test subscriber. Independent QD and CI still required at exact head before release, in addition to genuine isolated WordPress/Assembler browser + axe + Lighthouse and host-specific acceptance.
