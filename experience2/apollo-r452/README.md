# Apollo R452 — Revenue-proof bridge and reviewer fixture (draft, no installation)

Purpose: stop a legitimate-looking NASA source trail, UTM click, email event, checkout start, or proposed Grok asset from being misrepresented as verified customer revenue. This is an isolated *source-only* branch stacked on R451, not homepage or WordPress content. The committed `reviewer.html` is a **non-live local reviewer fixture**, not installed on WordPress and not a replacement for the R450 staging component.

## One relevant visitor path

Only after an actual approved Grok Apollo long-form/Shorts URL has been verified: viewer → the existing `/apollo-1-evidence-atlas/` → source/uncertainty review and free original educator activity/receipt → [complete free investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → separately verified, founder-authorized rights-cleared paid original classroom kit (if ever offered). The visitor never has to purchase or subscribe to read the historical investigation. No unapproved checkout link, affiliate claim, sign-up, NASA photo, logo, geography, tracking script or price is embedded.

## Executable commercial proof contract

`python3 qa/funnel_guard.py proof-template.json --out QA/PROOF_RECEIPT.json` returns explicit **HARD_HOLD** and `null` verified revenue. `python3 qa/test_funnel_guard.py` executes adversarial validations of privacy, attribution, distinct 7/30-day cohorts, verified order lines, refunds, platform/source alignment, linked lead-to-customer rates and tiny-sample warnings. No direct network or WordPress calls. Amounts are integer USD cents; never calculate net revenue from clicks or checkout starts, never treat synthetic input as independently verified commerce. Structural calculations on supplied rows remain **unverified** until independent merchant settlement and human-traffic reconciliation; this tool cannot authenticate external evidence by itself.

`proof-template.json` is intentionally unpopulated: there is no evidence of a Grok Apollo post with verified `asset_id`, approved link placement, source-to-order human attribution, seller-accepted Apollo SKU, paid fulfillment, fees/refunds or a valid 7/30-day cohort. An empty ledger does NOT assert zero sales.

## Historical evidence and rights

NASA [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) distinguishes probable arc initiation from a conclusive single origin. NASA's [later flammability account (Feb. 14, 2018)](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) concerns tests after the fire, not proof of the original spark. [NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) applies independently; this sprint reproduces no archive media. See actual inherited R448 claim manifest, R450 source receipt, and R451 proof gate. Editorial QD approval is still pending.

## QA scope and blocked gates

- **TESTED LOCALLY**: standard-library Python checks; browser suite at 320, 360, 390, 768, 1024, 1440, 1920px with JS on/off, real keyboard/touch native `<details>`, single free CTA, readable no-JS, reduced motion, overflow and screenshots of *committed static reviewer fixture*. Actual PHP/WordPress staging was **not** navigated or installed for R452.
- **NOT RUN**: genuine axe-core scan, navigated LCP/CLS, field p75 INP/CWV, independent screen reader, theme/CDN/caching and complete WP staging. Local Chromium `page.set_content` **does not** meet these acceptance gates. Failure of outbound navigation in current sandbox is `ERR_BLOCKED_BY_ADMINISTRATOR`, not a staging pass.
- **RELEASE HARD HOLD**: R417 discrepancy and existing public Atlas editorial-status reconciliation, NASA rights review, founder-approved sellable product, Grok asset proof, verified merchant settlements, independent QD, exact-head green CI, real staging acceptance and founder permission.

## Owner-specific OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer/step | Blocker | Change | Evidence | Owner |
|---|---|---|---|---|
| Original Apollo teaching kit → paid order | No seller-accepted SKU, license/fulfillment proof | Refuse commerce CTA | `QA/PROOF_RECEIPT.json` HARD_HOLD | Founder/Claude |
| Grok Apollo video → qualified landing | Published asset and matched source unknown | Campaign ID guard | 27 local mutation tests; publication NOT_VERIFIED | Grok/Praxxis |
| Evidence Atlas → free investigation | Editorial confidence + mobile continuity | Reviewer source/limit cards, one CTA | 14 offline Chromium cases, NOT staging | Apollo/Site QA |
| Confirmed order → net revenue/1k qualified humans | No independently audited orders, fees, refunds, human denominators | Validated 7/30-day integer-cent cohorts and low-sample flags | No attributable net KPI; synthetic arithmetic only | Claude/Commerce |

Related: #150, #820, #818, original Research Desk PR #158 and homepage frozen PR #49. Grok/Praxxis TASK-008 Drive queue remains unedited. No WordPress writes or production release.
