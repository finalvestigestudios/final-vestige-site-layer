# Apollo Experience 2.0 — R239 PHP-to-Chromium release bridge

**STAGING HOLD. No WordPress installation, theme merge, live CMS edit, social publish, analytics change, affiliate link or paid purchase.**

## Scope and ancestry

- Isolated branch stacked on R238 draft PR #1747, exact parent commit `3b07c82be181a0df8391a509cd4bd8e584354c07`.
- No modification to existing files, PR #49, research-desk PR #158, or other agents' production lanes.
- Input is R238's generated *complete* Apollo Atlas source set, protected manifest SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`. All manifest file hashes must match before acceptance.
- The test invokes the **real staged R224 PHP shortcode adapter** with its source-controlled WP-function shim, and then loads the exact PHP-emitted HTML with its pinned CSS into Chromium. It does not invent a new synthetic version of the historical text.

## Run in an offline QA environment

Requires Python 3 + `playwright`, PHP CLI, and a Chromium binary at `/usr/bin/chromium`. Extract a verified R238 generated bundle to `/path/to/generated-r238-A`, then:

```bash
python experience2/apollo-r239/qa/r239_php_dom_accept.py \
  --atlas /path/to/generated-r238-A --out /tmp/apollo-r239-qa-A
python experience2/apollo-r239/qa/r239_php_dom_accept.py \
  --atlas /path/to/generated-r238-A --out /tmp/apollo-r239-qa-B
sha256sum /tmp/apollo-r239-qa-{A,B}/receipt.json
php -l /path/to/generated-r238-A/fv-ex2-apollo-r224.php
```

The runner refuses to overwrite existing receipts. It records **10 Chromium browser contexts** (320, 390, 768, 1440, 1920px × JavaScript on/off), screenshots, keyboard skip and native source disclosure behavior, mobile tap, reduced motion, forced-colors fixture, no external network requests, absence of horizontal overflow and a single original-investigation CTA. It also checks the PHP adapter's early-preflight CSS, already-printed CSS, late fail-open to original article, and tampered source rejection.

No JS is necessary for the historical content, links or disclosures. LCP/CLS observer values are fixture diagnostics only, never field or installed WordPress results.

## Actual local evidence (2026-11-09)

- Twice independently executed PASS: 10/10 Chromium contexts per run, PHP adapter modes PASS, HTML output byte-equal to pinned historical source template, deterministic screenshots 10/10 matching.
- Exact committed Python Git blob SHA-1 `9007deaea6f39867113e9121c01c62816206ace3` matched the locally executed source.
- Deterministic acceptance receipt SHA-256 `332b73aa27679d568d1ecada5973fa3f463d7909febaa74a0e0c6ce2fa9e97b0`.
- Unmounted fixture LCP samples ~96–344 ms and observed CLS 0 in test contexts; **not Core Web Vitals** and not production performance.
- Actual screenshot QA is preserved in the separate archive attached to the sprint record.

## Historical and commercial custody

Official NASA Review Board reference: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . An electrical arc is identified as the most probable initiator, not a conclusively proven spark. NASA S66-58038, S67-15717 and S67-21294 photographs have distinct documentary roles; source links are not a commercial media-rights grant. No new photo, invented geo pin or speculative source edge was added.

Only current relevant action: free original investigation https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . The educator dossier is not a confirmed SKU, checkout, or sale. Grok asset_id and qualified-human traffic unverified; paid orders/refunds/net revenue unavailable. Offer → step → blocker → experiment → evidence → owner: future rights-cleared educator dossier → checkout → no merchant-approved product → conduct buyer/rights/checkout verification before exposing purchase CTA → **BLOCKED** → founder/Claude. Documentary → Atlas → unknown published Grok asset → reconcile TASK-008, no invented attribution → **UNVERIFIED** → Grok/Praxxis. Atlas → free article → PHP-vs-browser integration risk → this test gate → **LOCAL PASS** → Apollo. Orders → net/1k qualified humans → missing denominators and transactions → 7/30-day authenticated reconciliation → **NOT COMPUTABLE** → Commerce/Analytics.

## Release gate: HARD HOLD

This **does not** certify real WordPress/Assembler behavior, actual HTTP navigation, genuine axe-core, screen-reader acceptance, browser chrome zoom, hosted CI, commercial media rights, R198 ancestry, or founder release approval. Independent installed-site testing and governance remain mandatory. Never activate multiple alternative Apollo shortcode adapters simultaneously.
