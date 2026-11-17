# R424 — publisher identity and nested cohort custody (DRAFT / HARD HOLD)

**Scope:** Final Vestige Studios site-layer Preparedness Issue #136; conversion #820 and business charter #818. Additive read-only follow-on to R423 PR #2805, exact parent `ba8f271d3ec0f0016f5010023f283b21e2e37c79`.

## Demonstrated defect and correction

R423 accepts the synthetic URL `https://youtu.be/ABC123` as a YouTube video despite YouTube's conventional eleven-character native IDs. It also accepts a 7-day claimed sales/traffic aggregate larger than the same campaign's 30-day aggregate. R424 rejects both syntactic contradictions while **never claiming a published social asset, source-accurate hook, rights-cleared media, real human visitor, valid merchant order, medical safety or QD approval**.

- Extract candidate native publisher media IDs from valid YouTube watch/Shorts/live, TikTok, Instagram and Facebook video URLs. Enforce eleven-character YouTube media ID shape. Keep creator-assigned `asset_id` and platform-native media ID separate rather than pretending they are equal.
- Compute domain-separated deterministic SHA-256 over proposed topic, platform, native media ID, creator ID, first-party free landing destination and UTM keys. The receipt explicitly says `UNVERIFIED_REVIEW_ONLY`. A digest proves neither ownership nor publication.
- Reject claimed 7-day measurements greater than related 30-day measurements across sessions, orders, gross, refunds and fees, without treating arithmetic as paid-settlement verification. The current cohort schema has no independent merchant settlement, aligned end-date or independently qualified human-session proof and remains **HOLD** even when synthetic amounts are consistent.
- Guard input receipt reads against nonregular files, hard/symbolic links, oversized/empty files, duplicate JSON keys, NaN/Infinity and changing file identity. CLI always exits 2.
- Preserve inherited R409–R420 content/citation gates, original writing and all qualified QD blocks.

## Local exact-code tests

**62/62** new R424 regression tests PASS under Python `-I` with synthetic fixtures. **570/570** inherited R409–R416 tests passed in separate bounded module runs. R420/R421/R422/R423 completed **58/58 + 74/74 + 79/79 + 90/90** in separate local module runs. Total **933 PASS from separate processes, not one combined run**, and no native authenticated full repository checkout. Python compilation PASS. R417–R419 inherited rerun incomplete in current run; do not relabel earlier run evidence as current.

Remote R423 source baseline Git blob `1e97e28dfd06401725f38309d2a9ea842b6f013f` equals the executed local predecessor. New Git source/test blob identities must be compared to local executed byte identities in final PR receipt. Original 35 articles, 203 distinct source IDs, 280 source occurrences, 17 shared URL review groups, five disputes and nine alternative Shelter manuscript forks are **inherited counts, not newly rebuilt or adjudicated**.

**Native validate/build and actual 35 WordPress/private preview export comparison: NOT EXECUTED** — complete authenticated source checkout/export pairs not accessible to this run. Actual mobile/keyboard/checkout/merchant, safety/privacy and independent QD checks: NOT DONE. Hosted CI result, if any, must be reported separately without inventing a PASS.

## Exact inspected coordination refs (2026-11-16 PT)

| Branch / PR | SHA |
|---|---|
| Claude food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Claude health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Claude history field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Claude history food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Claude history home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Claude shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Claude Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter continuation | `ac8625faf30dd5538fadc31e06cb5a2cea1defae` |
| Shelter followup | `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` |
| Independent safety QA PR #157 | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` |
| Synthetic fixture PR #169 | `e9cd7766dac59d47ab467d8945269b9146c2aef5` |
| Dependent isolated fixture PR #2205 | `bbcf1859768624c611df4abadc564c18247cf32a` |
| Homepage lead PR #1689 | `f55c36b6598eec558dd8bb24e4c8988becc51be0` |

QA #157's household no-main-breaker drill fix and medicine safety caveats remain unmerged. PR #169 still contains a canonical-writing duplicate-source fixture case; dependent PR #2205 safely moves that case to a disposable sandbox and is not merged. Neither independent QA branch nor original 7+2 manuscript candidates were changed or chosen.

## Conversion-first one-offer friction docket

One high-intent, prospective topic is **household emergency contacts and reunification**. The only existing candidate free destination is `https://finalvestige.com/preparedness/`. Original Article #15 and printable Tool #104 are private **HARD HOLD**, pending source-to-claim, hazard and child-privacy validation; Tool #102 is a distinct existing tool. No retired water freebie or false medical safety language.

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| ONE real FV-owned/licensed Preparedness practical pack → paid checkout/delivery | No authenticated rights-cleared payable FV SKU, permitted offer, delivery or refund terms | Authenticate one already sellable product and working merchant checkout/refunds on mobile before any paid CTA | **HOLD**, no verified product/order | Founder/Commerce |
| One already-published on-topic Grok asset → existing free Archive | No independently matched immutable creator asset ID, native post ID, rights/hook or allowed mobile first-party UTM | Praxxis checks actual published post, rights, factual source hook, post/asset ID and destination; R424 is only reviewer-side syntax | **UNMATCHED** | Grok/Praxxis |
| Existing free Archive → optional Tool #104 | Article #15, emergency accuracy, reunification scope, child privacy and accessible print not independently approved | Human source/citation scope assessment and accessibility/safety review, no tool promotion until release permission | **HARD HOLD** | Preparedness/QD |
| Qualified sessions → relevant CTA → confirmed lead → paid merchant order → realized net | No consent-safe source attribution, trusted 7/30 cohorts, order settlements, refunds/fees | Claude's existing event/merchant evidence, no duplicate tracking or synthetic customer, small-sample flags | **NOT COMPUTABLE** | Claude/Commerce |

Proposed free-only CTA, **not posted**: “Start With Trusted Preparedness Resources.” No paid CTA, false urgency, affiliate activation, launch, navigation, CMS, email, social posting, analytics script, payment charge, spend, merge or QD PASS.

Founder retains spending/commercial/release approval. Claude retains website/analytics engineering. Grok retains all social creation/posting and its task queue. Praxxis independently verifies social assets and rights via TASK-008. Cross-references #136, #820, #818.
