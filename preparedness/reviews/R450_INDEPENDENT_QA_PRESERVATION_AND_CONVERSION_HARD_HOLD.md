# R450 — independent QA preservation without cross-branch mutation (DRAFT / HARD HOLD)

Scope: Preparedness Archive source/citation safety gates only — #136; commercial cross-reference #820 and founder charter #818. No publish, merge, WordPress, navigation, analytics, social, merchant, affiliate or email writes. Founder approval remains required.

## Exact reviewed Git evidence (2026-11-17 PT)
| Source | PR / branch HEAD | Original `preparedness/tests/test_preparedness.py` Git blob | Test methods |
|---|---|---|---:|
| Independent start safety QA | #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` | `32627489b7727d97ac54663d87ac8d112911c811` | 30 |
| Food synthetic fixtures | #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` | `e80d622c2fd32bf6c9752e375c1208c1d47d8e7c` | 36 |
| Dependent no-canonical-write repair | #2205 `bbcf1859768624c611df4abadc564c18247cf32a` | `b63e7f4dc9c84a4bef15dd581affe08ac81356af` | 37 |
| Current parent integration | #2947 R449 `2044fcd03ec6d7d34d07dd86833121dd3ab7fdef` | `c329f98e051d2aabe31a3343869b0fdac355b315` | 36 |

**Found:** R449 already includes 36 fixture/governance tests from the food track, with a temporary-directory duplicate-ID test. It lacks QA #157's specific four-article human-safety publication rejection test and #2205's runtime protection against writes/deletes in the canonical checkout. PR #157 also changes **four non-test files**: two full-length article bodies, `sources/fragments/start.json`, and `taxonomy.json`. These MUST receive independent editorial/source review before any source merge.

## Additive deliverables
1. `preparedness/tools/r450_qa_overlap_rehearsal.py`: stdlib-only Git-blob-pinned custody checker; AST method-preservation inventory, same-name drift report, structural anti-canonical-write fixture checks, independent publication-block witness check, fail-closed non-publishing receipt. Its **optional** output can only be a never-overwritten rehearsal file outside the checkout, preserving all original R449 test bodies.
2. `preparedness/reviews/R450_QA_COMPOSITE_REHEARSAL_NOT_EXECUTED.py.txt`: exact GitHub-source 38-test candidate (R449 36 + QA #157 human-safety + #2205 no-canonical-write runtime guard), deliberately named `.txt` so it does not execute or replace `test_preparedness.py`. The full candidate needs AST/native runtime proof before use.
3. `preparedness/tests/test_r450_qa_overlap_rehearsal.py`: additive synthetic adversarial tests for malformed/unpinned inputs, source test loss, dropped emergency safety assertions, isolation/canonical-file guards, lossless candidate construction, and release-hold invariants. It must be executed independently in the authenticated checkout.

## Exact original contributor verification
Nine original protected refs compared 0 ahead/0 behind against R449 frozen SHA pins:
`claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`;
`claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`;
`claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`;
`claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`;
`claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`;
`claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`;
`claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`;
`claude/prep-shelter-continuation` `ac8625faf30dd5538fadc31e06cb5a2cea1defae`;
`claude/prep-shelter-followup-evidence` `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`.
No Claude, QA, fixture, homeowner, editorial or production branch was edited.

## Tests and hard boundaries
- **85/85 local companion synthetic tests PASS**, Python compilation PASS, in 0.522s. This local companion tests the same algorithm but is not a byte-identical execution of the GitHub-committed R450 code/test module. Exact committed runner + actual authenticated GitHub source snapshots **NOT EXECUTED**; no CI PASS asserted.
- Original 35-manuscript identities / 203 source IDs / 280 occurrences / 181 literal URLs / 17 shared-URL review groups remain the protected R397 docket, not re-executed from a native checkout here.
- **Five source disputes, nine unselected forks, all 17 shared-URL review cases, full 35-article body build, 70 real WP/private-preview exports, independent human source/reading-depth and emergency/medical/food/child privacy/QD approvals: HOLD.** No tool confirms safety of unreviewed guidance.
- Tool #102 plan builder remains distinct from unpublished Tool #104 wallet card; original Article #15 and Tool #104 cannot be advertised as approved.

## Conversion-first: offer → funnel step → blocker → experiment → evidence → owner
| OFFER → STEP | BLOCKER | CHANGE / ACCEPTANCE | EVIDENCE | OWNER |
|---|---|---|---|---|
| One existing FV-owned rights-cleared Preparedness practical pack → paid checkout → delivery | No authenticated purchasable FV seller SKU, rights, completed merchant transaction, refund policy or reliable delivery | Audit actual seller account, SKU, license, live checkout/mobile receipt, delivery and refund terms **before** proposing a paid CTA | **NOT VERIFIED, HOLD** | Founder / Commerce |
| One already-published on-topic Grok family-reunification clip → public free agency-linked Archive | Actual immutable asset_id, spoken claim, permission, publishing date, landing link and mobile rights unknown | Praxxis independently match exact on-topic existing video; record public post link and `utm_content=asset_id`; don't assign Grok a new production task | **UNMATCHED** | Grok distribution / Praxxis QA |
| Public no-gate official family emergency planning guide → optional future Tool #104 | Article #15 and Tool #104 medical/emergency/child-privacy and print reviews not complete | Proposed *free-only*, unpublished CTA: “Review the official household emergency checklist.” Confirm official URL, phone viewport/accessibility, and source-to-page intent. Keep essential instructions free | **PENDING** | Preparedness/QD |
| Qualified-human `asset_id/utm_campaign` landing → useful CTA → confirmed lead if applicable → merchant-confirmed paid order → fees/refunds → realized net revenue | Merchant settlement, attribution, confirmation and cohort denominator absent | Request existing Claude/Commerce 7/30-day consent-safe cohort evidence; net revenue per 1,000 qualified-human sessions; tiny-sample warning; don't call clicks/starts sales | **NOT COMPUTABLE** | Claude analytics / Commerce |

No paid service, commerce or CTA was activated. Grok retains content and posting control; Claude owns site/analytics production; Praxxis is independent content QA; founder retains release/spend. DO NOT reactivate retired water freebies.
