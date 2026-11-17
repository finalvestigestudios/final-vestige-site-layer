# R436 — Full-document accessible CTA and safety-copy semantic custody

**DRAFT / HARD HOLD.** Issue #136, commercial governance #820 / #818. Strictly stacked on R435 PR #2867 at exact parent `066b6d28e91370bf151f87d3ab10e0faa21d3e44`. Additive validator and tests only; no original article, source, route, product, WordPress, navigation, analytics or contributor mutation.

## Gap reproduced locally using synthetic bytes

R435 compares the **multiset of full-document anchor href values** but does not bind those hrefs to the labels people and screen readers see, or compare text *outside* `<main>`. In two independent artificial WordPress/preview pair mutations with identical correctly hashed destinations, R435 inspect produced equal link digests and no errors: (1) footer "Follow local orders" became "Ignore local orders"; (2) the same free Archive link label became "Paid checkout." R436 detects `OUTSIDE_MAIN_SAFETY_OR_CTA_COPY_DRIFT` and `CONTROL_ACCESSIBLE_NAME_OR_DESTINATION_DRIFT`, respectively. This does **not** prove any live-site compromise.

R436 compares ordered interactive-control semantics (href, visible text, accessible-name/description references, rel, target, download, referrer-policy, title and other supported attributes), checks missing ARIA references and nameless controls, and fingerprints full document/body-outside-main reading copy. Reports are deterministic, conservative and may flag legitimate WordPress chrome differences; no static PASS is accessibility certification. Existing R435/R434/R433 evidence and full document export byte-lock gates remain composed; missing original evidence remains HARD HOLD. The CLI is deliberately read-only and always returns exit 2.

## Verification boundaries

Local Python 3.13.5: `22/22` new tests and `426/426` combined R430–R436 subset tests passed in one local assembled test tree, Python compile clean. **Not full repository CI or a native build**. Source blob `62d1218d013a1e868066219510bbc392319df28c`, tests blob `17ec1ffaf54565a7b3d1465113e211b7bc525897` match locally executed code files. R435 original HEAD pinned above. Nine Claude/Shelter contributor branch pins re-compared live 2026-11-17, all identical/0 ahead/behind. Independent QA #157, fixture #169, dependent #2205 and home #1689 inspected at current exact SHAs, no change.

Open blockers: full authenticated Git checkout with original private 35-article manifest, genuine original manuscript candidates and 35 WordPress + 35 private-preview export pairs; native `validate.py`/`build.py`; original 5 source-applicability disputes and 9 unselected forks; qualified source/emergency/food/medical/child-privacy/accessibility/print review; independent QD and founder signoff; hosted CI. Original 35 article identities, 203 source IDs, 280 occurrences and 17 URL-review groups remain undisturbed. Do not infer safety from a green synthetic test.

## Conversion-first acceptance

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| One **existing authenticated** FV-owned or licensed Preparedness digital pack | Optional purchase after free official guide | Payable rights-cleared SKU, authorized seller, checkout/delivery/refund terms unknown | Independent real-product/fulfillment audit **before** any paid CTA | **HOLD**, no authenticated paid SKU | Founder / Commerce |
| Already-published, topic-matched family-contact Grok asset | Real post -> free official Preparedness Archive `/preparedness/` | Authentic asset_id, date, rights, source hook and mobile UTM not matched | TASK-008 research-only handoff; no queue/post changes | **UNMATCHED** | Grok / Praxxis |
| Free official checklist -> optional Tool #104 | Practical download, never gate core emergency information | Article #15 accuracy, child privacy, printable and device accessibility, Tool #102/#104 identity | Independent qualified QD and rights/delivery proof before any CTA | **HARD HOLD** | Preparedness / QD |
| Qualified human sessions -> confirmed paid orders -> realized net | Accurate consent-aware 7/30-day cohort, fees and refunds | Merchant settlement and denominator absent | Claude-owned native event/merchant reconciliation, no duplicate tracking | **NOT COMPUTABLE** | Claude / Commerce |

Unpublished **free-only CTA:** "Review the official household emergency checklist." Proposed source-backed destination: currently public `https://finalvestige.com/preparedness/` ONLY after a genuinely matched published Grok asset and accessible working free official-source link are independently verified. No paid CTA, retired water giveaway, affiliate activation, public posts, CMS/nav writes, emails, tracking scripts, spending or release authority taken. Claims of clicks/leads are not claims of paid orders.