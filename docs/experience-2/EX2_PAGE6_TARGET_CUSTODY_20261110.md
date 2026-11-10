# EX2 Page 6 — integrated evidence-link target custody (2026-11-10)

**Status: isolated draft, release HOLD.** Parent PR #1886 at `1d03d9b0440e24628844b71a84eb75ec80dc9989`. Frozen PR #49 unchanged. No production WordPress changes, deployment, install, affiliate activation, new tracking, or expense.

## Specific conversion/accessibility defect

The source-pinned seven-chapter candidate, composed into a **simulated** Assembler header, left many freestanding evidence links and the native `<details><summary>` source-inspection control with touch rectangles shorter than the W3C WCAG 2.2 SC 2.5.8 **24 CSS px** target minimum. On the 320px browser fixture **18** interactive rectangles were under 24px in one dimension; 360px **19**, 390px **18**, 768px **19**, 1024px **18**, 1440px **19**, 1920px **19**. Some can qualify under the WCAG spacing, equivalent, or inline exceptions; do not label every rectangle a formal failure without full manual assessment.

Evidence/provenance controls are core product trust surfaces: readers must be able to inspect archival sources, follow the investigation, or reach the existing Focus path without mistaps. This is **not a paid-conversion result**.

## Scoped change

Only `tools/experience-2/compose_page6_flagship.py` adds WordPress-integration-specific CSS. Standalone hero, original art-direction files, media, and all eleven source-pinned Git blobs remain unchanged. Select **standalone** evidence, source, and outbound links and raise their minimum touch rectangle to 28 CSS px while preserving in-paragraph/inline citations. Raise the source-inspection `summary` to at least 44px without suppressing its native disclosure marker. Preserve the original 44px Focus resource link and the **external Page 6 native /focus/ CTA, native Jetpack, and 72 Margins items** through existing composer admission.

## Actual local measurements (Chromium; synthetic header; external network aborted)

| CSS viewport | Before: sub-24px controls | After | Source summary before → after | Root overflow after |
|---:|---:|---:|---:|---:|
| 320 | 18 | 0 | 21.44 → 44px | 0 |
| 360 | 19 | 0 | 21.44 → 44px | 0 |
| 390 | 18 | 0 | 21.44 → 44px | 0 |
| 768 | 19 | 0 | 21.44 → 44px | 0 |
| 1024 | 18 | 0 | 21.44 → 44px | 0 |
| 1440 | 19 | 0 | 21.44 → 44px | 0 |
| 1920 | 19 | 0 | 21.44 → 44px | 0 |

Locally reproduced composer: **23/23 Python unit tests PASS**. Before/after Chromium comparison: **28/28** normal-width cases PASS across seven widths × JavaScript enabled/disabled × before/after. New committed source-pinned admission harness has a tighter **14-case** after-only contract and must be run from an exact commit checkout. Keyboard Enter on source disclosure works in local Chromium. The first-screen heading did not shift in six of seven tested widths (1024px: ~7px higher). Focus stays 44px high.

**Reflow caveat:** exploratory `documentElement.style.zoom='2'` at 768px produced one *very narrow* footer disclosure link (13.64px wide) due to a synthetic forced flex wrap; this is **not manual browser zoom or a WCAG claim**. Genuine 200% browser zoom remains an independent release gate and should inspect that footer carefully.

The verification suite fails when Chromium/Playwright is missing. It blocks external image requests intentionally; image loading/actual transfer bytes, Assembler runtime, Jetpack subscription completion, native WP parse/storage, axe, manual WCAG 2.2 AA, Lighthouse/CWV and independent CI/QD remain **NOT TESTED**.

## Source and rights checkpoints

WordPress media read-only IDs: Apollo #473 NASA image S67-19766, metadata 78,346 bytes; Franklin #474 Victory Point note scan of an 1869 reproduction, metadata 466,043 bytes; NYPL #1258 Brooklyn transit map, metadata 5,553,669 bytes original with derivatives. Attribution/captions are present but **metadata ≠ independent rights clearance nor downloaded image-byte verification**. The candidate retains the existing linked museum/NASA/NYPL claims without adding new history.

## Offer → funnel → blocker → experiment → evidence → owner

**Offer:** existing free 52-page Seven Day Focus Fieldbook, no new commercial promise. **Step:** evidence engagement → contextual Focus action → verified subscriber → independent paid order. **Blocker:** undersized stand-alone evidence links and source disclosure can impede source verification and trust before conversion. **Experiment:** integration-only target-size hardening (no new CTA or analytics), compare measured click-target geometry and keyboard semantics. **Evidence:** synthetic Chromium passes above; *no confirmed email, checkout, commission or net revenue delta*. **Owner:** interim homepage engineering; Claude for hosted integration and attribution, Grok/Praxxis for campaign traffic.

## Admission still required

Execute the existing seven-chapter scoped Gutenberg swap in a truly **isolated WordPress Playground/local Assembler** installation with **public content only**; verify 72 items, functional Jetpack separately (without unauthorized signup), no-JS content, keyboard/touch/actual 200% zoom/reduced motion and manual plus axe a11y; load first-party images while measuring transfer bytes and checking rights; run Lighthouse and field CWV if available; obtain exact-HEAD CI/QD and founder visual/release approval. WordPress.com Personal does not offer a native staging clone; a local Playground is **not** WordPress.com Atomic certification. Do not sync a staging database to production or deploy this PR without explicit approval.
