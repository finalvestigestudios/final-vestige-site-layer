# Apollo 204 Recommendation-to-Response Trace — DRAFT / HOLD (30 Oct 2026)

Tracks [Experience 2.0 Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), stacked on Apollo evidence comparison PR #202, independent of frozen homepage PR #49 and the WordPress Research Desk PR #158.

## This increment
A new source-first, accessible Aftermath Trace chapter shows **six original, Board-documented recommendations** beside NASA's later account of changes. Verifiable themes: 100% oxygen test designation, material controls, hatch/egress, emergency training/gear, independent safety oversight, and fire/oxygen protection. Each source pair has precise report locators, links to NASA's primary text and an explicit caveat that the *1968 historical status account* does **not** establish final implementation of each remedy.

The whole set is pre-rendered HTML. An optional filter for hardware/procedures only activates after successful JS setup; any filter failure reveals all original content. A hash link to a hidden record resets the filter and focuses the record. Six-record CSV/JSON exports are generated deterministically from the same reviewed source rows. No new mapped coordinates, NASA photo bytes, paid SaaS, third-party fonts/scripts or promotional offers.

## Source records (checked 30 Oct 2026)
- NASA Apollo 204 Review Board report, Part VI, Findings 2/4/5/9/10/11: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA Response (1968 Senate-report excerpt, as reproduced by NASA): https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/
- NASA brand/media restrictions (editorial uses and no implied endorsement): https://www.nasa.gov/nasa-brand-center/images-and-media/

## Evidence and release barriers
The separate local staging package contains complete browser tests and screenshot results at 320–1920px (including no JS, injected filter error, 200%-style zoom and reduced motion) and recorded a **real touch-target problem** before fixing it with >=44px scoped link height. Local CDP accessibility-tree smoke covers 28 controls across five widths; **axe-core was unavailable and NOT RUN**. Local Chromium offline synthetic LCP/CLS cannot establish field p75 CWV; real site WordPress/Assembler + shortcode integration, assets URL routing, Safari/NVDA/VoiceOver, verified image usage, axe, independent exact-head QD and green hosted GitHub CI remain open. No merge, deployment or WordPress changes authorized.

## Reproduce
```sh
cd experience2/apollo-casefile
python render.py
python qa/verify_determinism.py
python qa/response_contract.py
```
Relative export URL paths are only appropriate for the offline fixture; they must be rewritten and HTTP-verified on WordPress staging before production. The code package in GitHub and the independent local browser fixture require a **byte-parity review** before interpreting old local browser QA as exact-head certification.