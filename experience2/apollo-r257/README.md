# Apollo R257 — complete print evidence custody (DRAFT / HOLD)

Owner: independent Experience 2.0 Apollo lane, Issue #150, cross-reference conversion #820 and charter #818. Stacked on Apollo R256 PR #1863; homepage #49, original Research Desk #158, original sealed Apollo R238, all live WordPress content/settings and Grok's content queue remain untouched.

## Demonstrated defect and proposed fix

The sealed Apollo Atlas contains **13 native HTML `<details>` disclosures**. R256 exposed the four SourceDrawer records when printed but the remaining closed disclosure bodies were still omitted from printed research packets. Offline Chromium 144 comparison of identical source PHP with all disclosures initially closed vs manually expanded gave 19,221 vs 20,625 whitespace-normalized PDF-text characters: **1,404 omitted**. R257's single print-only CSS override uses `details::details-content` to expose the entire evidence trail on paper without opening anything on screen or requiring JavaScript.

After R257, both closed and expanded PDF text normalize identically to **20,625 characters**, with SHA-256 `a4034436b5ad4bb3bfc09493dfd54f85fd428989bad05ae36e60ec298ecd0493`. The corrected packet is 18 pages versus 16 pages for the baseline closed print. The previously corrected four SourceDrawer provenance records remain. No NASA evidence, source links, historical chronology, geographic pin, gallery, images or copy changed.

## Reproduce exact-source test

```sh
python experience2/apollo-r257/qa/qa_r257.py \
 --atlas /path/to/sealed-r238 \
 --r253 experience2/apollo-r253/atlas-source-actions.css \
 --r254 experience2/apollo-r254/provenance-tap-continuity.css \
 --r255 experience2/apollo-r255/evidence-path-touch.css \
 --r256 experience2/apollo-r256/print-custody.css \
 --overlay experience2/apollo-r257/print-full-evidence.css \
 --out /tmp/apollo-r257
```

Dependencies: PHP CLI, Python Playwright, `/usr/bin/chromium`, `pdftotext`. The test checks R238 manifest SHA `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68` plus each child SHA and exact PHP-output/template identity, prints baseline and correction with native collapsed/open states, tests 320/390/768/1440/1920 widths × JS enabled/disabled, Enter/Space/touch interaction, reduced motion/no-JS, one original free CTA, zero unexpected external requests and no overflow. Two local executions passed (20 contexts); four same-size screen captures matched between executions and before/after print-only CSS. Text digests/JSON receipts matched; PDF *binary bytes* varied because export metadata varies. No browser-native zoom, axe-core, real screen readers, installed WordPress/Assembler, real HTTP/CSP, field LCP/CLS or Firefox/WebKit print acceptance is claimed.

## Source/rights boundary

Original technical findings: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The Apollo 204 Board found an electrical arc **most probable**, not a conclusively located individual ignition source. Catalog photos are distinct kinds of evidence, not images of the ignition event. NASA advertising/endorsement rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . NASA source access does not confer commercial rights or endorsement. No copyrighted NASA photos are embedded in this change.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer / step | Blocker | Proposed experiment | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Apollo educator evidence kit → purchase | No verified matching current SKU, media rights, checkout, delivered order or approval | Audit existing Products 001–015/Payhip, permissions and fulfillment before enabling any paid CTA | COMMERCIAL HOLD | Founder / Claude |
| Grok Apollo video → Atlas | No authenticated published Apollo asset_id / tagged link | Read-only reconcile TASK-008 with actual platform post inventory | UNVERIFIED | Grok / Praxxis |
| Atlas → free investigation | Closed print omitted evidence explanation text | R257 print-only native-detail disclosure custody | LOCAL ORIGINAL-SOURCE CHROMIUM PASS | Apollo |
| Paid orders → realized net receipts | No authenticated merchant orders/fees/refunds + qualified-human sessions | Consent-safe 7/30-day cohort reconciliation using existing measurement only | NOT COMPUTABLE | Claude analytics / Founder |

The **one current nonintrusive next action** remains the existing free Apollo investigation: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/. A teacher-ready paid Apollo kit is only a hypothesis; neither existence nor sale is verified. Never insert unrelated commerce in the historical narrative. Do not confuse clicks, leads or outbound affiliate sessions with paid orders.

**Release HOLD:** source/mode/rights review, genuine axe, independent screen-reader, browser zoom/Firefox/WebKit, isolated installed WP/Assembler, production HTTP/CSP, hosted CI/QD, R198 ancestry reconciliation, merchant permission, and founder approval. No merge, deployment, social post, merchant/analytics/email change or spending.
