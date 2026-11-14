# R368 — Private Tool #104 print disclosure custody

**DRAFT / HARD HOLD · Issue #136 · 2026-11-14**

## Source-level finding

At exact R367 parent e03d100617591cf07519ef71fd3bb75facdc7ce3, private Tool #104 family-reunification-card.body.html has Git blob be8698ac5d020476ff649d85813810e2000c6f98; metadata Git blob 47da1e7e20e39f0ea85e26d54a8d58301f6e0a15. The original contains the alert “A printed card can be lost” and caution “Anyone who finds it can read it.” The parent has class pa-card-mainhide; print CSS hides that class using display:none!important.

This is a **source-level warning suppression risk**, not a verified production printout, personal-data leak, or independent safety finding. No source advice is edited or approved here.

## Added isolated engineering

R368 pins Tool #104 original Git object identity, draft/pending safety states and the R367 41-document/50-paired-private-export gate, then probes original, private WP and preview HTML in JavaScript-disabled offline Chromium under screen and print media. It rejects hidden/missing/duplicate warning alerts, absent privacy sentences, missing no-JS fallback, unavailable browser, changed original IDs, absent checkout/build, and inherited gate failures. Always emits HARD HOLD, exit code 2, with release, QD, medical/child privacy, physical-print, orders and revenue flags false.

**TESTED locally:** 59/59 new adversarial Python tests with synthetic Chromium media/JS-off fixtures, plus 271/271 inherited isolated R364–R367 tests: 330/330 PASS. Exact committed new tool/test Git blobs match executed local files. Python compilation PASS.

**NOT TESTED:** Authenticated native checkout/build, 50 actual private WP + 50 preview pairs, physical-paper print/PDF, child privacy, emergency advice QD, hosted CI or merchant conversion. Local Git cannot resolve github.com. Browser simulation is not a physical-print PASS.

**Separate drafts:** QA #157, synthetic fixture #169, remediation #2205, homepage #1689. No merge or source approval implied.

## ONE conversion-first use case

- **Audience/topic:** family emergency contacts and reunification. Authentic existing free public destination: https://finalvestige.com/preparedness/ . Draft free CTA only: “Start With Trusted Preparedness Resources.” Tool #104 is a HELD, private, optional practical card, not safe/published/available.
- **Paid Preparedness pack:** HOLD. No independently verified FV-owned/licensed, rights-cleared, purchasable and deliverable SKU, merchant checkout, refunds, paid order, affiliate conversion or settled net revenue. Do not invent an offer or reactivate retired water products.
- **Grok match:** Praxxis must identify one genuinely already-published matched family-contact asset_id, exact media link, truthful hook and permitted mobile destination before recommending canonical organic-social UTM. Never invent an ID or change Grok's creation/posting queue.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| FV paid Preparedness pack, unverified | paid order | no existing validated payable SKU, rights, delivery, refunds | verify one existing actual product; founder approval before checkout test | HOLD | Founder/Commerce |
| Public free agency-link archive | matching social visit to free guide | published on-topic Grok asset unknown | independently verify actual asset ID/hook/mobile destination | UNVERIFIED | Grok/Praxxis |
| Private Tool #104 | guide to optional practical card | printed alert suppression, child data, no-JS, emergency/source review | qualified body remediation, native print/mobile QA | source-level print warning FAIL; native untested | Preparedness/QD |
| Qualified-human sessions | lead to paid order to settled net | merchant receipts, fees, refunds and attribution unavailable | existing Claude event contract and 7/30-day cohorts, tiny-n caution | NOT COMPUTABLE | Claude/Commerce |

Clicks, leads, affiliate outbound links and pageviews are not sales. No duplicate analytics scripts, false QD PASS, CMS/navigation, public publishing, social/emails, merchant activation, spending or unapproved release.

Cross-references: Issue #136, conversion issue #820, business charter #818, Praxxis/Grok TASK-008.
