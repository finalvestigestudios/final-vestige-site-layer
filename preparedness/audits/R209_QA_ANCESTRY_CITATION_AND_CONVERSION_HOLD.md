# R209 — Cross-branch QA ancestry and citation safety HOLD
Preparedness Issue #136; business coordination #820 and charter #818. 2026-11-07 PT. **DRAFT_HARD_HOLD — no release or medical safety approval.**

## Authenticated engineering finding
All seven Claude contributor heads still match the 35-article R200 custody manifest: start 2122d856fce9f64887c16df3d52e64be9f59a55b, shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976, food f911ff7a655de8d81535ea86ec3d65a49ee76648, health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17, hist-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c, hist-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d, hist-home 7504a5f099594d635e3dd7332a33a2e1346c43a2.

**NEW: six stale QA patch ancestry witnesses.** Independent QA PR #157 is based on old Start Here commit 10f58fed1ba808056813064ca5f9680589db8da1, not the frozen current contributor 2122d856... All FIVE paths modified by #157 differ between its PR base and the current contributor, including the household plan and three-day kit. The current contributor already has later, expanded cautions about keeping power to safety systems during outage drills and about refrigerated medication. Blindly copying the older #157 article bodies could REMOVE those revisions. Fixture PR #169 also has a test-file base different from the current Food branch (one more stale-base witness). Follow-up PR #973 is correctly stacked on #169. Reconcile by independent three-way review, do not mechanically cherry-pick or overwrite shared tests.

Exact open/draft commit pairs and per-file base/head Git blobs are recorded in r209_observed_independent_review_prs.json. The R209 gate records six contributor-versus-PR-base mismatches and rejects direct substitution of an unrebased #157 article head into the 35-article source snapshot.

## Runnable gate and independently tested scope
New offline fail-closed validator: preparedness/tools/r209_review_dependency_gate.py. New 131-case in-memory/temporary-file regression suite: preparedness/tests/test_r209_review_dependency_gate.py. Python compilation and **131/131 synthetic tests PASS**. Exact source and test Git blob IDs match those executed locally. The suite includes 35 separately named article source identity corruptions, 35 candidate body substitutions and 35 route mutations, plus PR ancestry, fixture, source exception and permission-laundering checks. Good structural results return DRAFT_HARD_HOLD, exit 2; missing/stale inputs return INVALID_HARD_HOLD, exit 3. Never returns QD PASS.

With a trusted complete checkout run:
python -I preparedness/tools/r209_review_dependency_gate.py --manifest preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json --observations preparedness/audits/r209_observed_independent_review_prs.json --report /tmp/r209.json

Then run original Python validate.py, build.py and full preparedness/tests discovery. **Full native build and authentic 41 outputs NOT EXECUTED**: local terminal cannot reach GitHub and full source histories remain unavailable. Synthetic tests do not establish claim support, safe medical practice or publishing approval. Three unexplained citation occurrences across articles #7 and #20 and seven historical shared-source conflicts remain unresolved. Retain 35 original articles, unique URLs, original reading depth and all pending safety states.

## Conversion-first, single offer, no activation
**High intent:** families compiling emergency IDs, insurance details, financial records and essential contacts. Existing LIVE free official-resource gateway: https://finalvestige.com/preparedness/ . Detailed original Household Emergency Plan and Family Reunification Card remain DRAFT pending source, qualified safety, privacy, print and accessibility review.

**One commercial candidate:** Legacy Triage, public Payhip listing https://payhip.com/b/n1RhV currently describes a $19, 580 KB printable PDF for essential financial/contact records. This independently shows a public listing, **not verified seller rights, successful paid checkout, correct delivery, refunds, paid orders or realized net revenue**. A paid CTA remains disabled.

Draft free CTA only: "Read the free official-source preparedness checklist." Future staged, not approved: "Read our full household emergency plan"; "Print the optional family contact card (keep your details private)." Proposed paid disclosure, not activated: "Optional $19 records-organizing PDF; it does not replace official emergency guidance."

| OFFER → FUNNEL | BLOCKER | CHANGE / TEST | EVIDENCE | OWNER |
|---|---|---|---|---|
| Grok household-records asset → free gateway | No verified published asset_id and matched destination in TASK-008 | Reconcile actual post URL, allowed link placement and UTM content | UNVERIFIED, no attributed sessions claimed | Grok / Praxxis |
| Public gateway → official free checklist | FV full article not independently safety reviewed | Maintain free primary-source guidance; QA 360/390 px link, focus, contrast | Live official-resource gateway; new article HOLD | Preparedness / Site QA |
| Free guide → optional Reunification Card | Private data, printing and accessibility not accepted | Stage local-only synthetic-data tests | HARD HOLD | Site QA |
| Free guide → optional Legacy Triage | Rights, merchant checkout, delivery and refund evidence absent | Authenticate approved storefront and receipt/delivery without unapproved spend | Listing observed; paid activation HOLD | Founder / Commerce |
| Qualified visitors → net revenue | No verified buyers, refunds, fees or qualified-human sessions | Reconcile source-confirmed 7/30-day cohorts | Net revenue/1,000 qualified sessions NOT COMPUTABLE | Commerce / Analytics |

Creator content and posting remain Grok's; Praxxis owns independent review in TASK-008; Claude owns production website/analytics engineering; founder retains all spending and release decisions. No public writes, email, merchant activation, analytics scripts, social posts or site navigation changes.

## Next release order
1. Review six stale PR bases against current contributor content; preserve newer safety wording and fixture isolation.
2. Human-adjudicate three article source-use gaps and seven cross-cluster historic source collisions.
3. Rehydrate full source history; native validation, build, 36+ regression tests, all 41 WordPress-ready preview targets and QD safety signoff.
4. Check verified Grok campaign asset and authenticated Legacy Triage checkout/fulfillment before considering a commercial CTA. Never equate clicks or leads with purchases.
