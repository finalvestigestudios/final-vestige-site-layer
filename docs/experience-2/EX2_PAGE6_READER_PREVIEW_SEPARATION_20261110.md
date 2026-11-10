# FV Experience 2 — scoped reader/preview separation (2026-11-10)

**DRAFT; NO WORDPRESS WRITES; NO RELEASE APPROVAL.** Stack parent: PR #1914 commit `b3b25915655f0839eeffa681ada9a52586637e4c`. Frozen PR #49 is untouched. Issue #150 / conversion coordination #820. This change only affects the scoped Page 6 composition produced by `tools/experience-2/compose_page6_flagship.py`; all 11 pinned original source files remain byte-identical.

## Confirmed integration issue

The WordPress-specific candidate inherited an internal **Art direction options** toolbar from the standalone design-study prototype. It occupied roughly 63–65 CSS px above the editorial headline in a simulated Assembler shell. That is undesirable reader-facing UI and delays the evidence and Focus conversion paths. More importantly, simply deleting the toolbar would stop case-switching: the pinned `flagship.js` initializes its case interaction only if it finds the preview selector.

## Implemented

1. Require exactly one expected three-option founder preview toolbar in the pinned original source; fail closed if the template changes. Remove only that toolbar from the scoped WordPress output, not the standalone study.
2. Inside the scoped, generated `flagship.js` text, make the direction control optional. Preserve the case selectors and no-JS meaning. All five source JS substitutions check an exact one-occurrence contract before proceeding. Do not modify the original `flagship.js` Git blob.
3. Preserve all three named art directions (`dossier`, `museum`, `observatory`) via root attributes and private-preview `?direction=` selection. Founder approval is still required to choose one for release.
4. Preserve the native Focus / Jetpack / 72 Margins outside the replacement boundary. No affiliate pitches, new instrumentation, historical claim changes or source URL rewrites.

## Source-equivalent local Chromium evidence

A **synthetic** WordPress-like 74px header and synthetic Margins/Jetpack markers were used; this is not an Assembler runtime and provides no subscription confirmation. Source was pinned against the existing eleven legacy blobs.

| CSS viewport | Heading top before | After | Closer to first screen |
|---:|---:|---:|---:|
| 320px | 401px | 336px | 65px |
| 360px | 386px | 321px | 65px |
| 390px | 371px | 306px | 65px |
| 768px | 351px | 288px | 63px |
| 1024px | 526px | 463px | 63px |
| 1440px | 456px | 393px | 63px |
| 1920px | 450px | 387px | 63px |

**Local Chromium test:** 7 widths × JS enabled/disabled = **14 after scenarios PASS**, with simulated source-preservation markers, 7 chapter anchors, native Focus href, no root overflow, 44px+ Focus rail, no-JS full cases, reduced-motion, JS case-switch-to-Franklin, 3/3 directions, and unchanged source image `src`/`alt` attributes. **2/2 local synthetic negative controls correctly rejected** altered original picker/JS contracts. Screenshots at 390/1440px and machine-readable results are supplied separately in the offline QA archive.

**Not measured/accepted:** genuine WordPress/Assembler rendering, real Jetpack signup/confirmation, actual archival-image network bytes, independent rights clearance, axe/WCAG 2.2 AA, native 200% browser zoom, Safari, Lighthouse/CWV, PR exact-head independent CI/QD, paid sales/net revenue. These must remain release blockers. Current WordPress.com Personal plan has no native clone; an isolated Playground/local WP with public content only is the correct free test route (not equivalent to hosted WordPress.com Atomic).

## Conversion decision

**Offer:** free 52-page Seven Day Focus Fieldbook. **Step:** above-fold contextual resource CTA. **Blocker:** internal art-direction editor UI delaying evidence/CTA and coupled to real source interaction. **Change:** scoped removal + independent case enhancement. **Evidence:** measured layout improvement and local browser interaction tests; no verified sales lift. **Owner:** interim homepage engineer; Claude owns production/attribution, Grok/Praxxis own acquisition, founder owns release.

**Release decision: HOLD.** No merge, production writes, new tracking, affiliate activation or spend. The target WP page's native external content must be confirmed on private WordPress before acceptance.
