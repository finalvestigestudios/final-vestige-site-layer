# R316 — Authentic 41-guide WordPress export parity and source custody

**Issue #136 | Commercial coordination #820 | Founder business charter #818 | DRAFT / HARD HOLD / NO PUBLICATION**  
Observed 2026-11-12 PT. Source and generated-artifact read-only integration gate only. No CMS, page, navigation, sales, analytics, email, social, or commerce mutation.

## Why this lift matters

R310–R315 already exercised hundreds of synthetic source/citation cases, but none had verified all **41 authentic generated WordPress guides**. R316 makes that gap an explicit, executable fail-closed gate instead of interpreting synthetic test counts as production readiness.

The pinned builder `preparedness/tools/build.py` has Git blob `349173d1e1d735eade218d95c7a0a2649c8cccd9`. The inherited R315 citation gate has Git blob `e0518450c3b45e5e8b59a2f5d0f801279be4821b`. R316 refuses byte drift in either dependency.

## Source → export custody checks

1. Load exactly 35 crosswalk-pinned source articles and six separately identified original tools (not overlapping contributor numbering), preserve every authored slug.
2. Load the trusted repository builder and render each guide **in memory** from source. No build invocation, no output writes.
3. Compare all 41 real `preparedness/build/wp/<slug>.html` artifacts and their 41 `preview/<slug>.html` twins **byte-for-byte** with independent in-memory builder output.
4. Refuse missing, unexpected, symlinked, altered or line-ending-drift outputs, unresolved source/link tokens, missing WordPress block wrappers and absent draft/evidence warnings.
5. Cross-check the actual `build-report.json` against every guide's original canonical URL, source list, reading-word count and estimated reading time; detect duplicate routes and missing/extra report rows.
6. Require report `release_evidence.state=HOLD`, **41 drafts, 0 published**, `wordpress_publication_performed=false`, `independent_qa_verified=false`. No fake PASS.
7. Preserve all inherited R315 citation, taxonomy, original content and safety hard holds. A byte-identical WordPress draft is **not** an independent medical/food/water safety approval or QD pass. The validator exits 2 for a genuine draft-only hold, 1 for an invalid/incomplete proof, never success=0.

`landing.html` and known `hub-<section>.html` may exist in the build directory but never count as one of the 41. No site or hub routes are changed. R316 does not create downloadable tools or modify underlying manuscript contents.

## Test evidence and limitations

- Locally authored prototype: **65 new deterministic tests PASS**; 422 inherited tests PASS; **487/487 local prototype regressions PASS**; Python compilation PASS. These local fixture tests are **not authenticated execution of the final GitHub-committed code bytes**.
- Deliberately incomplete local checkout: no authentic native 41-item artifacts; GitHub hostname remains unresolvable from the local container. The full native Python validator/build and 41 WordPress+41 preview byte comparisons are **NOT EXECUTED / NOT VERIFIED**.
- The source gate is intended for the full trusted checkout. Its presence in a draft PR is not evidence that the actual 41 exports pass.
- Two ambiguous approved safety labels, USDA FSIS dual source records, ten substantive article-body changes, twelve metadata changes, Tool #104/Article #15 emergency messaging/child privacy/print/no-JS/accessibility, and the unresolved tool contributor-number collisions remain **independent HARD HOLDS**.
- Independent PR #157 remains OPEN/DRAFT at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. PR #169 remains OPEN/DRAFT at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; the second fixture test's source-directory mutation remains to be reviewed rather than assuming complete isolation.
- Homepage lead PR #1689 at `f55c36b6598eec558dd8bb24e4c8988becc51be0` is untouched.

## Authenticated contributor heads as inspected in this run

| Frozen contributor | Git head |
|---|---|
| `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |

All seven match the SHA recorded in the R306 authentic lineage ledger. Separate Shelter descendants `ac8625faf30dd5538fadc31e06cb5a2cea1defae` and `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` remain apart from the frozen seven and unadjudicated.

## Conversion-first, one audience and one potential offer

**Household emergency contact / reunification** is the single high-intent social topic candidate. No immutable, authentic, already published Grok asset ID or approved destination-specific campaign has been independently identified in the existing TASK-008 handoffs.

| OFFER → FUNNEL STEP | BLOCKER → CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE → OWNER |
|---|---|---|
| Authentic existing Grok household-contact content → public free official resource archive | Match published `asset_id`, exact campaign URL, mobile landing and consent-appropriate attribution. Preserve Grok's production queue. | NOT VERIFIED → Grok/Praxxis |
| Free verified official-resource entry → optional **free** original family card #104 | Emergency-dispatch texting wording, child privacy, no-JS, print and accessibility review; verify original rendered destination. | HARD HOLD → Preparedness independent QA |
| Free guide → optional owned practical **paid** pack | Identify **one existing** rights-cleared FV SKU and independently verify product fit, live purchasability, checkout/fulfillment/refunds; do not invent or activate an offer. | NO APPROVED MATCHING SKU → Founder/Commerce |
| Qualified-human campaign sessions → confirmed leads → merchant-confirmed paid orders → refunds/fees → realized net revenue | Reconcile consent-appropriate UTM/asset_id, sessions, confirmed orders, costs/refunds across 7/30-day cohorts, tiny-sample cautions. | NOT COMPUTABLE → Claude/Commerce |

Free-only **draft** CTA for editorial review: “Make a plan for how your household will reconnect. Start with free official preparedness resources.” Candidate public destination: https://finalvestige.com/preparedness/ . Do not describe original unpublished Article #15/Tool #104 as live, independently safe or downloadable from this destination.

**No merges, public WordPress writes, navigation, external posting, scripts, paid services, merchant changes, email or spending authorized.**