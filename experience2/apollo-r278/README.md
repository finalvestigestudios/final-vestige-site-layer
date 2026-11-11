# Apollo R278 — pinned source custody and complete reusable-block paths

**DRAFT / UNMERGED / HARD HOLD / NOT INSTALLED OR LIVE.** Independent Apollo Experience 2.0 issue #150, business conversion #820 / #818. This is a child of **R277 draft PR #1998**, never homepage PR #49, Research Desk PR #158, or Claude's production engineering branch. No WordPress, content, analytics, email, creator/posting, affiliate, payment, or spending change.

## Substantive defects and correction

1. **Revisited block false negative.** R277's global `$seen` set permanently marks a reusable-block ID even if first visited through an eight-plus-depth route that cannot reach its content. A later shallower route to that same *published* block is therefore skipped, so CSS may not preload. R278 uses a bounded **active recursion path** with `try/finally` cleanup instead of global deduplication. Cyclic references still stop and draft blocks stay excluded. The shortcode itself always renders static, readable evidence without JS.
2. **Unreviewed source replacement.** R277 used `require_once` on any readable sibling PHP and returned an **empty string** if the function was absent. R278 SHA-256 pins the exact audited R275/R276 component bytes (`3f3c5a01e64cbc68349dd20c3daceadb64bf8a2e68ec5a0a2ea4bb6a3eed9107`). A missing, modified, or invalid component yields **plain NASA original-source and free Apollo investigation links** with explicit pending-review wording. It does **not** execute an unreviewed component or grant commercial/editorial approval. Future source changes must intentionally update the reviewed pin and tests.

Historical source: NASA Apollo 204 Review Board <https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/> (the most probable initiator was an electrical arc; no single ignition source conclusively identified). NASA commercial nonendorsement/imagery rights: <https://www.nasa.gov/nasa-brand-center/advertising-guidelines/>. **A factual link does not imply rights or agency endorsement.** No invented locations, speculative evidence, NASA photos, or merchant links were introduced.

## QA and reproducibility (2026-11-10 PT)

From root of the review/extracted bundle:

```sh
php -l experience2/apollo-r277/apollo-review-shortcode.php
php experience2/apollo-r277/qa/wp_contract_gate.php
php experience2/apollo-r278/qa/wp_source_path_gate.php
python experience2/apollo-r278/qa/failure_gate.py
python experience2/apollo-r278/qa/http_header_gate.py QA-A
python experience2/apollo-r278/qa/browser_gate.py QA-A
python experience2/apollo-r278/qa/browser_gate.py QA-B
```

Local executed evidence: inherited R277 **20/20** simulated WP checks PASS; original R273/R274/R275 PHP **13/13, 15/15, 8/8** and receipt Python **15/15** PASS; R278 bespoke PHP **16/16** PASS; missing/modified/authentic actual-PHP negative control **3/3** PASS; Python localhost HTTP response, external CSS and CSP **headers** PASS; genuine Chromium offline Playwright **14/14 twice** for 320, 390, 768, 1440 and 1920px × JS/no-JS and 200%/400% root-font stress; responsive overflow, source custody, native keyboard disclosures, print-source URLs and no unexpected requests PASS; screenshot hashes reproducible. Reproduction evidence is stored as two QA receipts, metrics and deterministic screenshots.

**Important limitation discovered, not a passed gate:** Chromium `page.goto(http://127.0.0.1/...)`, even with request interception, returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` in this runtime. Python's `urllib` genuinely retrieved local HTTP+CSS and checked response CSP headers, but **browser HTTP navigation and actual CSP enforcement were NOT tested**. Offline Chromium loaded the same authentic PHP+CSS under `set_content`. No genuine axe-core library is available locally; it was NOT EXECUTED. Installed WordPress/Assembler, Safari/Firefox, independent NVDA/VoiceOver, actual UI zoom, real CDN/CSP, LCP/CLS/INP field p75, editorial/copyright review and hosted CI are still **NOT ACCEPTED**.

## Controlled acquisition-to-purchase hypothesis (unactivated)

One high-intent segment: historically curious viewers of a **verified, already-published** Apollo 1 Grok documentary. Only after Grok/Praxxis authenticate an existing asset ID, original posting URL/date and signed-out mobile path:

**Grok long-form → already-public Apollo Evidence Atlas → original free Apollo investigation → distinct optional, disclosed Mini Museum buying guide → independently merchant-confirmed paid order/commission settlement.**

Apollo evidence panels contain **no merchant CTA**. The optional guide belongs outside the historical narrative and requires publisher eligibility, rights/offer fit, founder approval and independent checkout acceptance. The existing Awin redirect-path observation in #820 is **not** proof of accepted merchant relationship, checkout or paid sale. Grok owns video/post/queue, Praxxis review, Claude core production/analytics; this lane only stages Apollo proof and QA.

**Commercial KPI:** verified realized net revenue (after fees/refunds) per 1,000 *qualified human* sessions in 7/30-day asset_id/UTM cohorts; separately report provider-verified leads, confirmed orders, paid conversion rate, lead-to-customer rate and small-sample warning. All actual revenue/attribution inputs are unavailable: **NOT COMPUTABLE, not $0**.

No founder authorization, CI green on exact SHA, installed CMS test, legal media clearance or merchant acceptance. **Keep draft, unmerged and unpublished.**
