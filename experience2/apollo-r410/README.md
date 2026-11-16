# Apollo Experience 2.0 — R410 semantic provenance gate (draft; no production release)

**Scope:** `experience2/apollo-r410/` only. Stacks exclusively on R409 PR #2755; does not modify homepage PR #49, Research Desk PR #158, WordPress, social content or commercial/analytics systems. No maps, pins, edges, third-party assets or tracking are added.

## Defect addressed

R409's read-only gate verified the six record headings were *somewhere* in the rendered page, that its six Atlas cards had category values, and that NASA links existed. It did **not** prove that a record's NASA-linked historical text matched the immutable original PR #158 ledger, that each Atlas question pointed to its own record and correct official NASA publication, or that each card retained its *own* limitation. That permits evidence drift and misleading source attribution despite a seemingly intact gallery.

`qa/semantic_custody.py` adds a per-record original-template comparison (normalized meaningful text, ordered headings, exact link destinations, hidden/aria-hidden protection), plus six ordered Atlas-to-record bindings, class and limitation checks and per-card primary NASA publication check. Production comparison requires the original #158 `ledger.html` blob `403d128c57b9bc82dac7c619651689070edef86c`. The override is *test-only* and **not exposed by the CLI**. The earlier R409 gate remains a required separate check. No tool here can authorize a release.

## Run this QA (source-checkout only)

```bash
python experience2/apollo-r410/qa/test_semantic_custody.py -v
python experience2/apollo-r409/qa/test_source_custody.py -v
php experience2/apollo-r408/qa/test_php.php
python experience2/apollo-r408/qa/test_browser.py -v
python experience2/apollo-r410/qa/semantic_custody.py \
  --original experience2/research-desk/templates/ledger.html \
  --rendered /path/to/approved-https-staging-capture.html \
  --output /path/to/R410_semantic_staging.json
```

Use an **unmodified exact PR #158 original**; do not replace it with synthetic records or claim local fixture coverage proves historical content. Do not use the production CLI until real authorized HTTPS staging exists. The reference test runs on an ancestor synthetic PHP fixture only. Existing R408 Playwright tests exercise actual Chromium, but use `set_content`; they are **not navigated HTTP**, **not axe-core**, and don't produce trustworthy **LCP/CLS**. The local environment blocked browser navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`); therefore no navigated performance metric was fabricated. Independent axe-core, WCAG, screen reader, native zoom, CSP and installed WordPress tests stay in HOLD.

## Source and rights desk

- NASA Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — ignition initiator not conclusively identified (electrical arcing was considered most probable).
- NASA later deliberate flammability tests: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — 102 Command Module ignitions between **December 1967 and February 1968**, *after* January 27, 1967.
- NASA media and advertising restrictions: https://www.nasa.gov/nasa-brand-center/ — no implied NASA endorsement of FV or an eventual product; no NASA branding or photos in R410.

## Controlled acquisition → trust → purchase hypothesis

**One high-intent audience:** U.S. history/science educators or homeschool teachers seeking a primary-source, inquiry-based Apollo 1 lesson. **One proposed offer:** an *unlisted, not-yet-available* original 45–60 minute Apollo evidence-dossier lesson kit with chronology and source analysis. Pricing, rights, SKU, checkout, and fulfillment **unverified**, so **NO buy button**, implied endorsement or affiliate destination is authorized. Do not insert the offer inside the historical evidence record.

**Single nonintrusive next action:** from the source-backed Atlas to the [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). Later, only after approved commercial/rights checks, a context-matched separate educator product may be tested on a downstream page. Grok controls video/Shorts/posting; Praxxis controls external creator review; Claude controls site/measurement. Suggested hypothesis: better per-record source integrity and predictable deep links increase *qualified* source-to-free-article progression without disrupting editorial trust; purchase impact is not yet measurable.

Measurement only via Claude's existing consent-compliant funnel: `asset_id` / `utm_campaign` → qualified-human session → Atlas-to-free-article click → optional confirmed lead → independently verified paid order or affiliate conversion → refunds/fees → net revenue; 7/30-day cohorts with tiny-sample notes. **Net revenue per 1,000 qualified human sessions = 1000 × realized net revenue / qualified-human sessions** only when both inputs are verified. Zero observed data is **UNKNOWN**, not zero revenue. No new trackers or customer outreach.

## Release blockers and ownership

- **Apollo QA / QD:** install exact staging build under approved page, run actual HTTPS/CSP/network tests, Playwright 320–1920, no-JS, keyboard/touch, axe-core, native 400% zoom and p75 LCP/CLS/INP when traffic permits; verify exact HEAD and original NASA template and independent rights/readability.
- **Founder / Claude:** verify one rights-cleared payable educator SKU, checkout, merchant fulfillment and refunds *before* any commercial CTA; separately authorize release.
- **Grok / Praxxis:** confirm approved published `asset_id`/campaign, destination continuity and post permissions; do not overwrite TASK-008 or social content.
- **Commerce:** verify merchant-confirmed orders, fees, refunds, and qualified 7/30-day cohort before net-revenue claims.

Status: **BUILT + TESTED (local synthetic evidence only)**. **LIVE = NO; VERIFIED paid conversions = UNKNOWN; release = HOLD.**
