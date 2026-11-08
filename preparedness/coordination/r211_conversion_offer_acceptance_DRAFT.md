# R211 Preparedness conversion acceptance — DRAFT / HARD HOLD
**Issues:** #136 (owner and safety gate), #820 (conversion contract), charter #818  
**Prepared:** 2026-11-07 PT. **No site, merchant, email, social, analytics or CMS writes.**
This is a review document, **not** campaign authorization, clinical advice, a released offer, or a QD approval.

## One audience, one candidate offer
**High-intent audience:** People coordinating critical household contact, identity, insurance and document-location information with loved ones before travel, evacuation or a family emergency. **Creator topic proposal:** "What if your family needed your important records tonight?" Grok/Praxxis must confirm the actual posted asset, topic, rights, URL and campaign identifier in existing TASK-008. **No verified matching published creator asset ID has been supplied.** Do not add an item to Grok's queue.

**Free, already live, nongated evidence destination:** https://finalvestige.com/preparedness/ — its official-source gateway explicitly holds the original FV long-form safety guides pending source/qualified review. **DO NOT describe the unpublished Household Emergency Plan as live or medically safe.**

**One paid candidate only:** "Legacy Triage," public listing https://payhip.com/b/n1RhV. Public page viewed 2026-11-07 PT: advertises a **$19, ~580 KB, 9-section printable PDF**, intended for handoff of family/professional contacts, location of records and financial/access information if a decision-maker is incapacitated or dies. This is **not an evacuation survival kit, emergency-services substitute or official preparedness plan**. A visible product/checkout UI does not prove rights, actual merchant acceptance, completed card charge, access/download success, refunds or net revenue. All remain **UNVERIFIED**. The listing does not authorize a new product, new offer, price guarantee or link on FV.

**Optional practical tool:** The same existing listed printable PDF, **only if** the founder/Commerce verifies seller rights, intended-use fit, transaction, access delivery, cancellation/refund path and an approved adjacent disclosure. Do not publish an unreviewed new Reunification Card, resurrect the retired water freebie, or replace the existing Focus lead magnet.

## Draft article/landing CTA copy — DO NOT ACTIVATE
Free, no email required: "Build your household plan using current official resources. Open the free Preparedness Archive." → https://finalvestige.com/preparedness/

Conditional paid module, DISABLED until all commerce checks pass:
"Want a separate, optional printable to organize where your household records, contacts and handoff instructions are kept? Legacy Triage is a $19 digital PDF listed by the seller. It is not an emergency response guide, and the free preparedness resources remain available without buying anything."
Disclosure adjacent to link: "Optional paid product; check the seller's current price and terms before purchasing." Identify the product seller/affiliate relationship accurately after independently confirming it; do not invent commission status.

**Fit guard:** A quick-evacuation water/food/medical video is a poor match to Legacy Triage. A household-records/document-handoff video may be a match **only** after Grok verifies actual hook and destination and a human approves the distinction.

## Acceptance and source/checkout gates (all release-blocking)
| Gate / funnel step | Required check | Current evidence (2026-11-07 PT) | Owner / state |
|---|---|---|---|
| Creator → free entry | Existing real Grok asset_id, published post URL, exact hook, permitted link, utm_source, utm_campaign and destination agree; no invented IDs | Shared TASK-008 inspected; no authenticated matching asset yet | Grok/Praxxis — HOLD |
| Official resources → safety credibility | Public destination remains free; original 35 drafts retain source, article, citation and warning custody; no QD PASS | Public gateway visible; source exceptions #7/#20 + 7 conflicts held; full native build unavailable | Preparedness/QA — HOLD |
| Paid product identity | Seller authorization, rights clearance, product preview and nine-section content match the page and buyer intent | Public Payhip listing and $19 advertised PDF only | Founder/Commerce — HOLD |
| Paid CTA honesty | Accessible mobile copy, clear separate paid choice, distinct no-purchase route, disclosures beside link, no urgency or medical claims | Draft copy only, no browser/assistive-tech check | Preparedness/QA + founder — HOLD |
| Paid checkout | Test exact live merchant acceptance, checkout friction, tax/payment disclosures, refund policy, accurate payment | No authorized real purchase/test transaction or verified merchant result | Founder/Commerce — HOLD |
| Delivery | Receipt, valid secure PDF link, correct downloadable file, mobile PDF usability, purchaser support/refund access | Merchant listing claims instant download; no delivery verified | Founder/Commerce — HOLD |
| Lead capture | If present, existing opt-in, privacy, confirmed delivery, single-list deduplication; no forced email to read safety resources | Existing Focus is separate; no Preparedness confirmed lead observed | Claude/Analytics — HOLD |
| Attribution / revenue | Qualified-human session by immutable creator asset and UTM → free entry → relevant CTA → merchant-confirmed order → fees/refunds → net receipts; do not count outbound clicks as purchases | Actual cohort inputs unavailable | Claude/Analytics + Commerce — NOT COMPUTABLE |

## Manual staged acceptance procedure
Use consent-respecting existing analytics only. On a founder-approved nonpublic review environment, check widths 360/390/768/1440px, keyboard focus, descriptive CTA, touch target, dark/light contrast, back navigation, source links and warnings. Validate that a reader can access the free source without email. A checkout test needs an explicitly authorized purchase/refund transaction; **do not buy or launch a paid CTA here**. Test seller refund contact and download with authorized credentials only. Log a specific FAIL with screenshot/evidence if any step breaks. Keep native build/validation and all 41 WordPress outputs on HOLD until executable; don't claim staged browser tests were performed.

## Measurement contract
Cohort 7-day/30-day by actual published Grok asset_id/utm_campaign. Report separately: (1) qualified human sessions (with transparent bot filtering limitations), (2) relevant guide visits, (3) unique CTA clicks, (4) independently confirmed subscribers if any, (5) merchant-confirmed paid orders/customers, (6) gross paid revenue, (7) payment/merchant fees, refunds, and (8) **realized net revenue per 1,000 qualified human sessions**. Formula: 1000 × (gross paid revenue − refunds − verified fees) / qualified-human sessions, only when denominator > 0 and revenue reconciled. Mark missing attribution NOT COMPUTABLE, not $0. Display small-sample warning whenever counts are too low for reliable inference. Do not add a second analytics script.

## Engineering blocker carried forward
R210's original optional --report called unrestricted Path.write_text and could overwrite a pinned source (including on INVALID), or follow a symlink. R211 guards source reads with descriptor-relative O_NOFOLLOW and creates reports exclusively outside the checkout using O_CREAT|O_EXCL (0600). **These tests cover local filesystem integrity, not the 35 authentic source audits, clinical safety or commercial acceptance.** Original native validation/build and 41 WordPress exports are still not executed. Independent #157 and synthetic fixture #169/#973 remain separately staged; PR #157 named test is absent but negative publication coverage already exists in newer GovernanceRegressionTests. Do not rebase by overwrite.
