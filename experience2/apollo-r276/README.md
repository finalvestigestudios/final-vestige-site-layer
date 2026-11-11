# Apollo R276 — paper/offline primary-source custody

**DRAFT / UNMERGED / HARD HOLD — no WordPress, commerce, email, social or production writes.** Issue #150; commercial coordination #820; parent R275 PR #1986. Homepage PR #49 and original Research Desk PR #158 are untouched.

## Exact source defect and correction

In the original authentic R275 PHP preview, the source/rights disclosure is a native **closed** `<details>`. Chromium's print layout hides the content by default even though the existing CSS sets the `<details>` element to `display:block`. Consequently an archived/printed evidence panel omitted both NASA primary-source hyperlinks, the single-source dependency explanation, and editorial status details. The existing pale-gold status text also printed on white at insufficient contrast. Reproduced before the patch using print-media Chromium.

R276 narrowly patches `apollo-r273/assets/review-custody.css`: print-only `details::details-content` visibility, readable black metadata, noninteractive print source URLs generated via `attr(href)`, and suppression of the now-misleading '(opens in new tab)' print cue. On-screen markup, native expand/collapse, no-JS behavior, source URLs, research evidence and the single free-investigation action are unchanged. No speculative geographic pin, NASA photograph, merchant link or tracking call is added.

NASA Apollo 204 Review Board authoritative source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The Board found that an electrical arc was the most probable initiator but did not conclusively determine a single ignition source. NASA's commercial endorsement/advertising rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . NASA sources are links, **not** rights/endorsement approval.

## Executed local validation — 2026-11-10 PT

- All inherited PHP gates: R273 **13/13**, R274 **15/15**, R275 **8/8**; integrity gate **15/15** PASS.
- Source-controlled `qa/print_smoke.py`: **10/10** Chromium JS/no-JS screen+print contexts at 320/390/768/1440/1920px, reproduced twice with matching `smoke_receipt.json` and screen/print screenshots; authentic parent print defect detected.
- Supplemental `qa/print_gate.py`: **10/10** print/screen/touch/reduced-motion contexts and **4/4** independent negative controls PASS (original R275, remove print visibility, remove literal URL, remove print contrast). All 20 screenshots reproduced byte-for-byte twice.
- Prints show all three panels' NASA source hyperlinks, explicit URL text and shared-source warning. 6/6 NASA source anchors; 3/3 original free investigation CTAs. No external requests or horizontal overflow. The printed sources remain legible without requiring JavaScript.
- Browser fixture uses the authentic PHP output from R274/R275 and Chromium `set_content`; it does **not** prove installed WordPress, CSP, production rendering, axe-core or a screen-reader pass. Local HTTP navigation is blocked by `net::ERR_BLOCKED_BY_ADMINISTRATOR`; Firefox/Safari print behavior remains unverified. Browser UI zoom, field LCP/CLS and exact-HEAD hosted CI remain outstanding.

## Reproduce locally

```
php experience2/apollo-r273/qa/logic_gate.php
php experience2/apollo-r274/qa/logic_gate.php
php experience2/apollo-r275/qa/php_gate.php
python experience2/apollo-r275/qa/receipt_gate.py
python experience2/apollo-r276/qa/print_smoke.py /tmp/apollo-r276-print
```

Use `python experience2/apollo-r276/qa/print_gate.py /tmp/apollo-r276-extended` for the supplemental extended QA runner from the reproducibility archive; it is **not** a committed file. Screenshot hashes are in each JSON receipt; no third-party service is contacted.

## One controlled commercial hypothesis — no activation

Verified published Grok Apollo `asset_id` **not established** -> public Apollo Atlas -> original free Apollo investigation -> separately disclosed Mini Museum buying guide only after commercial authorization -> merchant-authenticated purchase. Hypothesis: offline source-custody reliability preserves credibility with documentary viewers; effect on sales **unmeasured**. Grok owns video/posting; Praxxis creator review; Claude site/analytics; founder publication, rights, merchant and spend approval.

| OFFER -> STEP | BLOCKER | CHANGE/EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|
| Mini Museum -> paid sale | Merchant approval and settlement not authenticated | Authenticate payable orders, refunds/fees | HOLD | Founder/Claude |
| Grok Apollo -> Atlas | Authentic published asset_id/link unknown | Reconcile TASK-008 without retasking Grok | UNVERIFIED | Grok/Praxxis |
| Atlas -> free investigation | Printed native closed details conceal NASA source proof | R276 print custody repair | LOCAL PASS, NOT LIVE | Apollo |
| Order -> net / 1,000 qualified humans | No paid settlements or valid sessions | Use existing analytics for 7/30-day reconciliation | NOT COMPUTABLE | Claude |

**Release HARD HOLD:** independent accessibility/axe, print in additional engines, installed WordPress/Assembler, HTTP/CSP, editorial review, applicable media rights, independent QA, source-controlled CI and founder authorization. No monetization claims, deployment, WordPress edits or social publications.
