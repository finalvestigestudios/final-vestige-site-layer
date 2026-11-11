# Apollo R275 — shared-source truth and editorial receipt custody

**Status:** isolated staging code; draft, unmerged; not deployed. Owner: Apollo Evidence Studio. Source issues: #150 (Apollo) and #820 (conversion), charter #818. Parent: R274 draft PR #1980. Do not touch PR #49, PR #158 or WordPress content/settings.

## Scope and defects addressed

1. The two public-Atlas editorial categories both cite **one** NASA Apollo 204 Review Board report. The source-disclosure panel now explicitly says these are not independent confirmations; no new evidence, coordinates, photographs or event chronology are introduced.
2. A self-asserted 64-character digest and reviewer name previously produced the deceptively positive heading “Editorial review receipts supplied.” R275 now says **Unverified review metadata present** and marks each entry **self-reported, unverified**. A future review date is rejected. The unconditional `data-fv-review-ready="false"` remains; no metadata unlocks deployment.
3. The new CLI-only receipt checker can verify that each *locally supplied* review artifact matches an exact SHA-256 and expected record/source, while rejecting missing/duplicated evidence, path traversal, symlinks, future/impossible dates and arbitrary `approved` flags. **Matching file hashes prove only integrity, not the identity of an editor, actual editorial acceptance, NASA media rights or publication authority.** Never use the CLI success flag as a production approval gate.

Primary source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . The Review Board's most probable initiator was an electrical arc; the specific point of ignition was not conclusively established. The public Atlas remains at https://finalvestige.com/apollo-1-evidence-atlas/ and its two editorial badges still require independently documented human review.

## Reproduction

From repo root:

```sh
php -l experience2/apollo-r273/review-custody.php
php experience2/apollo-r273/qa/logic_gate.php
php experience2/apollo-r274/qa/logic_gate.php
php experience2/apollo-r275/qa/php_gate.php
python experience2/apollo-r275/qa/receipt_gate.py
python experience2/apollo-r275/qa/browser_gate.py /tmp/fv-r275-qa
python experience2/apollo-r275/qa/perf_probe.py /tmp/fv-r275-perf.json
```

PHP gates: R273 13/13, R274 15/15, R275 8/8. Python integrity negative-control suite: 15/15. Chromium browser tests: 10 JS/no-JS viewport contexts at 320, 390, 768, 1440, 1920; five forced-colors, touch, reduced-motion, 400%-root-text contexts. Source-specific NASA links, native disclosures, multi-instance IDs and the original free investigation action preserved; screenshot hashes reproduced on two runs. Local lab PerformanceObserver LCP/CLS can be collected but is **not** field Core Web Vitals. Chromium's real HTTP navigation is blocked by administrator policy; `set_content` is not HTTP/CSP or installed WordPress acceptance. Genuine axe-core, screen-reader QA, UI zoom, field vitals, exact-head CI, rights clearance and independent editorial sign-off remain **NOT TESTED**.

## Conversion gate, not a history-page advertisement

One proposed route: verified Grok Apollo documentary (`asset_id` still unknown) → public Evidence Atlas → original free investigation → separately disclosed optional Mini Museum buying guide → **merchant-confirmed** paid affiliate order. This sprint adds zero merchant links, trackers or email hooks. Hypothesis: correctly stated review status and shared-source provenance reduce trust friction before a relevant purchase consideration; commercially **UNTESTED**. Grok owns creative/distribution; Praxxis reviews it independently; Claude owns site/analytics; founder controls release/spend/affiliate activation.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Mini Museum guide → paid order | Merchant acceptance/commission settlement not authenticated | Verify eligibility, paid order, refund and fee records | COMMERCIAL HOLD | Founder / Claude |
| Grok Apollo documentary → Atlas | Published asset ID, campaign and link placement not confirmed | Reconcile existing TASK-008; do not overwrite Grok queue | UNVERIFIED | Grok / Praxxis |
| Atlas → investigation | Self-reported review badges and same source counted twice | R275 custody integrity + accessible source disclosure | LOCAL PASS / NOT LIVE | Apollo / Editorial |
| Paid orders → net revenue per 1,000 qualified humans | No independently verified purchases, refunds, fees or valid denominators | Claude's consent-safe 7/30-day cohorts using existing analytics | NOT COMPUTABLE | Claude / Analytics |

**Release: HARD HOLD.** No production edits, new external service, social publishing, merchant activation or spending. Required: signed editor review, independent accessibility QA including axe and screen reader, installed WordPress/Assembler and HTTP/CSP tests, live field LCP/CLS, commercial-rights and merchant proof, exact-head CI and founder approval.
