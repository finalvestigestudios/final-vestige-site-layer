# EX2 short-phone primary evidence CTA — 2026-11-08

**RELEASE HOLD.** This is a source-only review stacked on #1595 at `450d65f392f3a1f0587b2671dc1e3141b3f88577`. It is NOT published, merged, or installed. Frozen #49 (`10495883299d53596992c26a8987f629b2904670`) untouched.

## Reproduced user-visible conversion/mission blocker
Tested the actual PHP-rendered preview output from the existing PR #1515 private Playground artifact (`fv-ex2-official-playground-web-review.zip`) in Chromium, with external network unavailable. At **320×568**, primary **Enter the evidence room** anchor begins at y=583 and ends y=627: completely below the first screen. The header's secondary **Free Focus Fieldbook** remains visible at y=95–139. This reverses the intended evidence-first CTA hierarchy on short phones, despite earlier 900px-tall mobile tests passing.

## Narrow, reversible source change
Append **only** a short-viewport media query to the canonical `experience2/home-flagship/flagship.css`: it trims unnecessary vertical gaps in the mobile masthead/eyebrow, first-screen padding, headline spacing, and deck line-height. It does not hide chapter navigation, abbreviate evidence, move Focus behind a popup, alter facts/images, reorder the focus tree, or introduce network/scripts/affiliate links. The original monumental Franklin folio remains unchanged.

## Measured browser comparison — offline HTML rendered by PHP preview
| Viewport | Primary evidence CTA before (top/bottom) | After | Horizontal overflow | Result |
| --- | --- | --- | --- | --- |
| 320×568 | 583/627 | **513/557** | 0 | **Previously outside; now wholly visible** |
| 360×640 | 541/585 | **474/519** | 0 | More space below CTA |
| 390×667 | 526/570 | 526/570 | 0 | Identical |
| 768×1024 | 553/597 | 553/597 | 0 | Identical |
| 1440×900 | 804/849 | 804/849 | 0 | Identical |
| 1920×1080 | 828/873 | 828/873 | 0 | Identical |

**6/6 browser viewport comparisons PASS** using the executable Python test in this PR and an offline, source-derived HTML snapshot; all retain 72 Margins records, seven chapter links, five Focus links, and zero measured horizontal overflow. The test fails closed if the source changes so baseline cannot be reproduced; it never sends a network request. Screenshots are stored separately in the handoff evidence package. This is a Chromium viewport result, **not** an exact-source WordPress/Assembler test or an A/B conversion result. We did NOT execute genuine no-JS, axe/WCAG, Jetpack, Lighthouse or live media-byte validation in this particular change.

## Integration caution
The protected PR #1515 preview ZIP embeds an older inline CSS snapshot. **The new canonical CSS does not automatically update that existing binary artifact.** Before WordPress Playground QA, regenerate its private bundle from the exact approved stylesheet and verify source fingerprints; do not apply this to production or silently treat an offline injected style as a deployed staging fix.

## Evidence/rights and commercial gate
NASA Apollo #473, Franklin #474 and NYPL #1258 source metadata were re-read without changes. Image delivery bytes and the exact NYPL edited-derivative rights remain unverified; no original archival asset or editorial claim altered. Existing Jetpack and the free 52-page Fieldbook must survive any eventual integration, and the Focus success-query spoof correction remains outstanding. Net revenue per 1,000 qualified human sessions and paid conversion are unmeasured; first-fold geometry is a **testable hypothesis**, not a sale.

**Offer → funnel step → blocker → change → evidence → owner**: Free Focus Fieldbook supports the historical archive; initial mobile evidence-room entry → primary historical action entirely below short phone fold → narrowly scoped CSS spacing correction → browser y-coordinates and preserved source counts → interim homepage engineering; Claude retains commercial attribution/Jetpack and Grok/Praxxis acquire traffic.

Pending: refreshed Playground artifact, genuine WordPress/Assembler acceptance, real bytes, independent WCAG 2.2 AA/axe, measured Lighthouse/CWV, Jetpack outcome, CI/QD, founder preview and explicit release approval.
