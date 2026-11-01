# Mind Studio R54 — Invisible Gorilla + evidence-first Zen12 warm-up

**Date:** 2026-11-01. **Owner:** Issue #171 only. **DRAFT/HARD HOLD.** No live WP changes, new mailing lists, publisher navigation, merchant link activation, promotions or deployment. The default /mind/ PR #172, homepage PR #49, Issue #150, QA #126 and Dispatch #174 remain untouched.

## New source-controlled deliverables
- Original ~2k-word investigation `investigation.md` and self-contained WordPress-ready scoped `investigation.wp.html` (no seller mentions in scientific article).
- Original independent Zen12 exact-offer guide `zen12-guide.md`, plus fully readable A/B HTML: same `guide-core` byte-for-byte, B adds original 40-second poster/transcript concept; no fake playback control.
- Noncanonical hub `mind-archive-noncanonical.html`; `claims-permissions.csv` with 48 source-to-copy/authorization decisions; `source-ledger.md`; `navigation-plan.md`.
- Original silent 40-second storyboard `film-storyboard.md` and six-cue `film.vtt`. Video render is a separate offline review asset; it is NOT hosted or activated on either WordPress candidate. If render not confirmed, do not claim it finished.
- Privacy-off local attribution `attribution.mjs` and reproducible `verify.test.mjs`.

## Source boundary
Official Inspire3 catalog and exact Zen12 `/hnp`, `/about`, `/research`, `/getstarted` read on 2026-11-01; published Puységur ID1377 and Focus ID1579 read via authenticated WP read-only. 1999 Simons & Chabris and 2013 Drew/Võ/Wolfe original studies; 2024 individual-differences meta-analysis and perceptual/cognitive load review; NCCIH meditation evidence; 2023 binaural review. Source ledger contains links and limitations. Merchant claims never substitute for independent evidence.

## Release gates
Written named Final Vestige-specific affiliate acceptance, approved exact link/tracking terms, EMAIL rights, vetted creatives, checkout/refund/payment terms, editor/source claims review, founder approval; 360/390/768/1440/1920 layouts & zoom, WCAG 2.2 AA keyboard/reduced-motion/contrast, WordPress sanitizer, no-JS, security, CWV/Lighthouse and real video hosting+caption sync; privacy-approved instrumentation before an A/B rollout. Unsupported brainwave/medical/financial claims excluded. A/B lift unmeasured. No source-only unit test qualifies as an actual browser audit.

## Run tests
`node --test mind/invisible-gorilla-zen12-r54/verify.test.mjs` in a native Node environment with repo access. Tests are restricted to their own folder and have no WP API calls. Separately run browser and WordPress staging tests before any release.