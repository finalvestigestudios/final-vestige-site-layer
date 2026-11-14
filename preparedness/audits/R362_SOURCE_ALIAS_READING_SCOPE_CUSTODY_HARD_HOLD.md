# R362 - source URL alias, reading-scope custody and branch reconciliation

**Status: DRAFT / HARD HOLD / NO MERGE / NO PUBLICATION.** Issue #136; conversion policy #820; charter #818. This is a read-only reviewer aid, never QD PASS, independent medical/emergency validation, a source human-link check, merchant verification, or release approval.

## Authenticated current GitHub custody (2026-11-14 PT)

Parent integration: R361 draft PR #2449 HEAD `aaf0871a6029c455e7ac117272d56c4dc3d9053a`. Independent QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; fixture QA #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` (unremediated); its dependent correction #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a`; home lead #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`. All were open drafts on inspection.

| Original Claude/Shelter ref | Exact HEAD |
|---|---|
| `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| `claude/prep-shelter-continuation` | `ac8625faf30dd5538fadc31e06cb5a2cea1defae` |
| `claude/prep-shelter-followup-evidence` | `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` |

All seven original contributor taxonomies have 35 article slugs, no duplicate article slugs, and six planned tool entries; the two Shelter continuation refs contain eight tool plans. The R361 integrated taxonomy preserves **35 article entries and nine planned tool entries** with 27 article `gate:true` restrictions. It is misleading to compare that 27 with independent #157's 22 without noting different baselines: #157 changed 18 to 22 on its *older own branch*. The active integrated content gate count is 27. None of these gate numbers grants editorial or safety approval.

## Source-citation reconciliation - direct remote read, not inferred

- Read exact R361 crosswalk blob `d62e493a67dedd23e04cfdf3cce762ef933c6bf9`, original base register blob `b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77`, and all seven original fragment blobs pinned in `r362_alias_review_gate.py`.
- Base register 34 rows; original fragments: food 30, health 21, historical field 28, historical food 28, historical home 29, shelter 45, start 29. Aggregate **244 source rows / 202 exact raw URLs / 201 conservative terminal-slash review aliases / 32 shared-alias review groups / 15 duplicated source-ID groups**.
- Independently compared all **75 variant records** across the 32 crosswalk groups to original source rows keyed by origin and row_index: **75/75 matched; zero structural mismatches**. All 32 groups remain `pending-human-source-and-reading-scope-review`.
- **Material alias distinction:** original NCHFP jerky source has both `https://nchfp.uga.edu/how/dry/recipes/jerky` and `https://nchfp.uga.edu/how/dry/recipes/jerky/`. These are *two unmodified source URL strings* but *one conservative review alias*. Do not use raw duplicate-URL counts as crosswalk closure counts; do not merge different authors' reading scopes, source support text, historical safety assessments, or verification states.
- The separate crosswalk source-head metadata records older drafting commits; exact current branch commit drift was checked above, while pinned *source-file Git blobs* were independently retrieved and matched. Do not reclassify a source as human-reviewed merely because the pinned file is unchanged.
- **32 unresolved source review groups remain**, even when syntactic closure matches. Source count parity is not independent verification of the asserted procedures or 35 articles' citations/claim truth.

## Engineering boundary

`preparedness/tools/r362_alias_review_gate.py` performs read-only source file Git blob identity checks against all eight original source files plus crosswalk, duplicate JSON-key rejection, 244/202/32/15 expected inventory checks, conservative terminal-slash alias closure, source ID/row-index and entire variant reading-scope custody, and mandatory pending review states. A missing or mutated native checkout remains `INVALID_HARD_HOLD`. Any clean observation is only `REVIEW_REQUIRED_HARD_HOLD`; CLI exits 2 even for a clean result. It does not modify routes, article/tool bodies, WordPress, CI, commerce, Grok tasks, or releases.

`preparedness/tests/test_r362_alias_review_gate.py` contains **51 independently executed synthetic adversarial tests**; exact source/test Git blobs were compared against locally tested bytes. Python compilation PASS. Full repository native `validate.py`, `build.py`, corpus-wide test discovery and 50 private WordPress + 50 preview outputs **NOT EXECUTED**: no authenticated local checkout; GitHub container DNS resolution unavailable. Direct read-only GitHub connector source retrieval does not substitute for this.

QA #157, #169 and dependent #2205 remain separate and unmerged. Tool #104 child-card privacy, print disclosure, no-JS and 911 language are still under qualified review; Article #15 and 35 full articles require claim-by-claim safety/source adjudication. Never claim unreviewed content is medically safe.

## Conversion-first owner acceptance (NO live changes)

| Offer -> funnel | Blocker | Proposed change / experiment | Pass/fail evidence and owner |
|---|---|---|---|
| **One FV-owned Preparedness pack -> settled paid order** | No verified rights-cleared payable SKU, merchant acceptance, delivery, refund evidence | Founder/Commerce authenticate an **existing** active product before drafting an optional upsell; preserve free Archive and do not resurrect retired water products | **HOLD / UNVERIFIED** - Founder/Commerce |
| Public free household emergency plan -> optional printable | Tool #104 child privacy, paper readability, citation support, no-JS statement and review states | Keep public `/preparedness/` official-source-led; test paper/mobile and disclosures after qualified editorial resolution | **HARD HOLD** - Preparedness/QD |
| Authenticated Grok family-contact social asset -> free guide | Real published asset_id, allowed destination, topic and mobile CTA not authenticated | Praxxis/Grok TASK-008 to confirm without creating a new creator queue or post | **UNVERIFIED** - Grok/Praxxis |
| Qualified human sessions -> permitted CTA -> confirmed lead if applicable -> merchant-paid receipt -> refunds/fees -> net revenue | No consented attributable source/session-to-merchant records | Claude/Commerce use existing approved measurement only; 7/30-day cohorts; report net revenue per 1,000 qualified human sessions only when denominator and receipts exist | **NOT COMPUTABLE** - Claude/Commerce |

Draft free-resource CTA only: **Start With Trusted Preparedness Resources** -> `https://finalvestige.com/preparedness/`. No new product or affiliate, false urgency, speculative attribution or checkout is authorized. Archive remains free and public safety guidance stays linked to original agencies.

**Release decision: HARD HOLD.** Nothing merged, deployed, published, emailed, posted, purchased or activated.
