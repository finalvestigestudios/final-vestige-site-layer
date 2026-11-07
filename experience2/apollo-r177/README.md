# Apollo Experience 2.0 — R177 provenance-aware Research Desk search (HOLD)

**Isolated source-controlled staging candidate. NOT production.** Parent: Issue #150; conversion program: #820 and charter #818. Stacked on R176. Research Desk original draft #158 and frozen homepage PR #49 untouched.

## Verified problem and fix

The original PR #158 JavaScript searches only a frozen `data-fvx-search` attribute. Later NASA provenance and the explicit caution about catalog identifier `S67-19766` appear in the visible card but are not guaranteed to be included in that original search index. In a real Chromium source-derived offline fixture, searching **“Catalog identification not verified.”** yields **0 of 6** records with exact original PR #158 JS (`32e757cc4dc8708397ff65ac21e89dd319781d78`). R177 searches both the original alias index AND each evidence card's actual `textContent`, including source custody, provenance, limitations and details. The same query now returns **1 of 6**, while “Photograph provenance” returns six. All sourced evidence remains readable with JavaScript disabled. No external network, analytics, merchant code, storage, or new links.

## Files

- `source-ledger-semantic-search.js`: optional replacement for **only** PR #158 `source-ledger.js`. Do not co-load original and replacement. Do not change the original PR branch.
- `stage_semantic_search.py`: fail-closed original JS Git-blob and R176 generated candidate SHA-256 pins; verifies exactly six records, six media provenance records, one catalog caution, fourteen historical links, one complete search UI, and no source scripts/iframes/forms. Generates staging-only fixture and asset substitution manifest. No WP integration.
- `test_semantic_search.py`: full repository checkout imports actual R174→R175→R176 source-pinned pipeline; nine positive/negative unit tests. Local QA archive uses a clearly marked source-derived fixture fallback.
- `browser_semantic_search_qa.py`: **genuine Playwright/Chromium** baseline-vs-fix, 320/360/390/768/1440/1920, repeat screenshots, keyboard activation, touch emulation, reduced motion, forced colors, JavaScript disabled, source-link inventory, no overflow, zero requests/page errors and fixture-only LCP/CLS observations.

## Reproduction from full repository checkout

```bash
python -m unittest -v experience2/apollo-r177/test_semantic_search.py
node --check experience2/apollo-r177/source-ledger-semantic-search.js
python experience2/apollo-r176/catalog_semantics.py experience2/apollo-r174/research-desk-provenance-candidate-UNPUBLISHED.html /tmp/r176-apollo.html
# The next expected SHA MUST originate from a separately inspected R176 audit, not from user-controlled input.
python experience2/apollo-r177/stage_semantic_search.py --original-js experience2/research-desk/assets/source-ledger.js --replacement-js experience2/apollo-r177/source-ledger-semantic-search.js --r176 /tmp/r176-apollo.html --expected-r176-sha256 <INDEPENDENTLY_REVIEWED_R176_SHA256> --out /tmp/r177-qa
python experience2/apollo-r177/browser_semantic_search_qa.py --fixture /tmp/r177-qa/R177-UNPUBLISHED-SEARCH-FIXTURE.html --original-js experience2/research-desk/assets/source-ledger.js --replacement-js experience2/apollo-r177/source-ledger-semantic-search.js --css experience2/research-desk/assets/source-ledger.css --out /tmp/r177-qa/browser
```

Local screenshot archive is offline **source-derived**, not installed WP. CSS may differ from Assembler rendering. No axe-core bundle is installed in the testing environment; **genuine axe has NOT run**. Also not tested: assistive screen readers, actual NASA image/CDN delivery, WordPress shortcode dynamic/reusable blocks, installed CSP and real-page CWV, exact-head GitHub CI. Keep release on HOLD pending these checks, Claude's adapter review, independent QA and founder authorization.

## Evidence / commercial relationship

**Chosen flagship:** Apollo 1, with the NASA Apollo 204 Review Board report as technical authority. Search makes provenance/uncertainty discoverable, improving evidence trust without presenting unverified image catalogs as conclusive proof or claiming a specific fire igniter. The archival images are **not cleared** as promotional assets for a future paid educator casefile. NASA source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/.

**One nonintrusive next action:** “Read original investigation.” Educators are a candidate high-intent audience for a rights-cleared *original* paid classroom evidence dossier, but no matching purchasable FV SKU/checkout/fulfilled order is verified. Do not insert a paid CTA until Commerce/Claude verifies rights, listing, price, transaction, fulfillment and refunds and founder approves. Grok retains the entire video publishing queue and TASK-008; Praxxis handles independent creator QA. No asset_id, attributed qualified human session, paid order or settled net revenue was independently reconciled. Net FV revenue per 1,000 qualified human sessions for 7/30 days: **NOT COMPUTABLE**.
