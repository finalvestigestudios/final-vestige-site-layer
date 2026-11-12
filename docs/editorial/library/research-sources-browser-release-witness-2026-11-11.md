# Research Sources browser release witness — November 11, 2026

**Owner:** FV Library editorial lane. **Target:** published WordPress page [#1338](https://finalvestige.com/free-resources/research-sources/). **Issue:** [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788). **State: HOLD — no live write authorized.**

## Fresh independent findings

On 2026-11-11 (America/Los_Angeles), the Library and Editorial Standards were opened anonymously, and public Research Sources still displayed **60** in static lead, badge, search label and category filters. The authenticated WordPress source for public #1338 (last modified 2026-11-03T22:12:43, SHA-1 content hash `19a43f2e15f1cba1adc12bd0243d1278d0f248df`) contains **90** card entries, not 60, split into **12 declassified, 24 accountability, 21 engineering, 25 archives, 8 navigation**. Staging draft #2354 (last modified 2026-11-10T12:36:48) contains the 90-count correction and remains unpublished/noindex. Do not publish #2354 as a duplicate.

One candidate for additional editorial research, a guide to historical magnetic declination, was cancelled after the GitHub duplicate check found existing [The North in the Margin / draft #2298, issue #1712](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1712). No competing page created.

## New substantial deliverable: Library Research Sources Release Witness v1.0

Prepared as a **conversation ZIP/PDF release candidate** with 9 files; not uploaded to WordPress and not claimed to be hosted in this repository. Contents:
- `qa_research_sources_live.py`, read-only Playwright/Chromium browser QA, capturing 320/390/768/1440 images and JSON; checks card/URL uniqueness, five group counts, static labels, source search, Accountability filter, keyboard focus styling, overflow, JS errors, public canonical and indexability.
- `test_release_gate.py`, **two** regression fixtures (corrected labels and deliberately stale 60 labels), 2/2 PASS. The fixtures are synthetic and the historical source baseline has not been reverified from each institution; local pass is *not* a production pass.
- `Research_Sources_Release_Witness.pdf`, original three-page readable print/QA signoff (rendered and visually inspected).
- `Research_Sources_90_Baseline_20261109.csv`, prior source URLs with original observation dates and **uncertain category labels on supplemental rows preserved**; not a new live source audit.
- `QA_SUMMARY.json`, blocked browser evidence, README, and SHA-256 manifest.

The production Chrome/Playwright navigation attempt returned **`ERR_BLOCKED_BY_ADMINISTRATOR`**, and the WordPress screenshot tool exposed a URL but no inspectable site pixels. Result `BLOCKED_SITE_NOT_RENDERED`; do not classify the site as broken or claim browser acceptance.

## How to clear publication gate

Run from an approved network-enabled machine (no account credentials needed):

```bash
python -m pip install playwright
python -m playwright install chromium
python qa_research_sources_live.py --output actual-public-witness
```

Inspect four screenshots **by eye**, test actual keyboard Tab navigation, the search returning the supplemental U.S. Coast Guard Light List, Accountability showing exactly 24 cards, no page-wide overflow, no overlay hiding page controls, and responsive readability. Read the JSON and fill the three-page release witness PDF. Separately inspect underlying source links, access restrictions and item-level rights—URL existence alone is insufficient.

Only if that passes, obtain a **fresh optimistic-locking hash** and make scoped existing-page #1338 changes: initial text/count labels from 60 to 90; correct the JS total map's Accountability 23→24 and Archives 26→25. Keep all 90 cards, rights notices, SEO, scripts, shared UI and paths. After the change, independently read back WordPress and inspect the real public URL again at all four widths. Do not send subscriber emails, initiate social posts, spend money, modify site-wide templates, or take over other editorial lanes.

**Sources inspected 2026-11-11:** [The Library](https://finalvestige.com/free-resources/), [Research Sources](https://finalvestige.com/free-resources/research-sources/), [Editorial Standards](https://finalvestige.com/editorial-standards/), [issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788), [site QA issue #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589).

**Rights:** The release witness PDF diagram, worksheet, and QA script are new original FV materials; no third-party copyrighted source scans/photographs reproduced. Existing linked collections remain link-only and independently rights-governed.

**Suggested future Grok concept only:** “A directory that says 60, but holds 90: why static source labels matter.” Not distributed.
