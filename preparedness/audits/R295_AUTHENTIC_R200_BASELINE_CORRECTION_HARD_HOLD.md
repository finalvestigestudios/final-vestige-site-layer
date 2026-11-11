# R295 — Corrected R200 Custody Baseline and Hist-Food Citation-ID Reconciliation (UNAPPROVED)

**Date:** 2026-11-11 PT · **Issue owner:** #136 (Preparedness integration + provenance only) · **Conversion coordination:** #820 / charter #818
**State:** DRAFT / HARD HOLD. No publication, merge, WordPress, CMS, navigation, production analytics, social posting, affiliate activation, merchant change, email, spending, or independent QD certification.

## Material correction to R293 and R294
The prior R293/R294 reports incorrectly described five Claude contributor branches as having changed *after the R200 frozen inventory*. R293's field named `frozen` actually points to older **pre-R200** commits for five clusters. Its field `head` matches the exact published R200 frozen manifest in all seven clusters. The authentic source of truth is:
- `preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json`
- Git blob `5822f9dfde21d1f3bdfc26658769d852c639438c`
- schema `fv-preparedness-r200-seven-cluster-35-article-frozen-custody-v1`.

**Fresh read-only GitHub compare_commit results (2026-11-11 PT):** Start Here `2122d856fce9f64887c16df3d52e64be9f59a55b`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; Hist-Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Hist-Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; Hist-Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`. Each named branch was **IDENTICAL to R200**, ahead=0, behind=0, changed files=0. Future moving heads must be re-compared; the R295 JSON receipt is time-bounded evidence, not a live GitHub API.

This correction **supersedes** the narrative of five new contributor updates / 23 new changed paths in R293/R294, but preserves the recorded older revisions and real manuscript-source differences as historical witnesses. R294 audit's top line now carries a prominent correction without destroying historical text.

## Hist-food source identity: one raw-ID substitution, eight markers
R294 accurately preserved two divergent raw citation IDs:
- **Pemmican and Dried Meats:** seven occurrences of `hist-food-nchfp-jerky` in integration, seven of `nchfp-jerky` at R200.
- **Pioneer Travel Rations:** one such occurrence each.

This is one **distinct source-ID pairing across two manuscripts**, not two separate vanished sources. At exact commits, both source fragments list the NCHFP *Jerky* page with matching title, publisher, `supports` text and verification date; their URL text differs by a trailing slash. Hist-food R200 fragment blob: `c1856c998c6c728f0de72221e5654a238df994a9`; older integrated fragment blob: `d10628342fea5f177a8d1be00dd906d0c9c7850e`. Source `notes` records the former test-fixture placeholder problem. **No automated source aliasing, ID rewrite, harmonization or editorial source-support approval is permitted.** The separately acknowledged USDA FSIS versus NCHFP heat-step and storage-life disagreement remains an editorial/safety hold.

## New executable review gate
`tools/r295_r200_source_authority_hold.py` reads the authentic R200 manifest, legacy R293 crosswalk, all three R294 seven-article witness manifests, and the new exact R200 branch-compare receipt. It enforces:
- 35 distinct canonical article routes and original per-cluster blob custody, 41 intended draft export targets.
- Seven actual R200 branch identities rather than confusing older ancestors with the R200 baseline.
- Seven historical article routes, source metadata still in draft, 334 recorded citation occurrences, no reading-depth/citation-count regression relative to R200.
- The exact 7+1 hist-food source-ID occurrence discrepancy without silently authorizing an alias, and five LF-normalized R200 body matches.
- Fail-closed safety and commercial flags **always false**. Even mechanically consistent provenance returns `DRAFT_HARD_HOLD`, not QD approval.

**Verification:** 55 adversarial synthetic Python unittest cases passed, including 34 duplicate-route checks, seven SHA tamper checks, false-QD/publication-state checks, lost depth/citations, stale branch receipt and malformed source-use metadata. Local checked source/test Git blob IDs match the GitHub committed objects. **Not** a complete native validator/build run on current full repository. Local GitHub DNS prevents complete checkout. Source-level R295 snapshot cannot independently attest that a moved branch stays unchanged.

The earlier 138-test R294 prototype was offline-only and uncommitted; do not count it as merged, executable R294 GitHub code, or release validation. Previous isolated test counts similarly do not establish 41 authentic output bodies.

## Independent QA / source safety blockers
PR #157: `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, OPEN/DRAFT; household breaker/refrigerated-medication safety edits, no publication clearance. PR #169: `e9cd7766dac59d47ab467d8945269b9146c2aef5`, OPEN/DRAFT; the fixture-upgrade test now isolates data in a temporary copy, **but** a separate duplicate-source regression test still temporarily writes to the actual `preparedness/sources/fragments` directory. This must be isolated before running concurrent tests. Home lead PR #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`, OPEN/DRAFT, untouched.

Existing 21 historical lineage disputes, 32 shared-source URL groups, 15 duplicate-ID groups, three CDC/Ready.gov agency-citation disputes and genuine semantic support reviews remain. Article #7 chemical-contamination language, Article #15 / Tool #104 child information, printing, no-JS, accessibility and all medical hazard claims require qualified human review. Historical source registration and full-text parity are NOT proof of source support or reader safety.

## Conversion-first friction and release-plan (offer → step → blocker → experiment → evidence → owner)
| Offer | Funnel step | Blocker | Change / acceptance check | PASS/FAIL evidence | Owner |
|---|---|---|---|---|---|
| Existing free official-source Preparedness Archive at `/preparedness/` | Social video → existing page | No independently verified already-posted Grok `asset_id`, rights, post date or signed-out mobile URL | Praxxis verify one existing family reunification/school-pickup video against TASK-008 without assigning Grok new posts; use existing approved campaign scheme only | NO VERIFIED MATCH | Grok / Praxxis |
| Existing free household-planning resource | Landing → relevant official-source guide | Original FV reunion article and Tool #104 not safety/privacy cleared | Draft CTA copy only: “Plan how your household will reconnect. Start with free preparedness resources.” Verify intended official-resource destination before any use. No new gate/paywall | UNPUBLISHED; DESTINATION NOT TESTED | Preparedness QA / Claude landing owner |
| Optional existing Tool #104 | Guide → downloadable contact resource | Minor PII, shared-device print, no JS, mobile keyboard/accessibility | Qualified approval, signed-out mobile/print/no-JS audits, ensure no server upload of child's personal details | HARD HOLD | Preparedness QA |
| $19 Legacy Triage listing under **Vested Wisdom** | Guide → optional paid pack | FV rights/seller of record, relevance to reunification intent, live checkout, terms, delivery and refunds unverified | Founder/Commerce must prove licensed ownership and merchant settlement, test buyer journey and intent-fit; no CTA until written approval | PRODUCT LISTING OBSERVED; NO VERIFIED FV OFFER | Founder / Commerce |
| Confirmed paid customer | Purchase → realized net revenue | No authenticated sessions→orders or fees/refunds | Use existing approved attribution only; 7/30-day qualified-human cohorts, realized net per 1,000 sessions; tiny-sample warning | NOT COMPUTABLE, NOT ZERO | Claude Analytics / Commerce |

Do not market retired water freebies, treat visits/clicks/checkouts as paid orders, activate a mismatched upsell, duplicate scripts, rewrite Grok's production queue, change `/focus/`, or publish any original unreviewed guidance. Founder retains release and spending approval. This PR is review-only.

## Remaining native gates
- Re-run exact seven contributor GitHub comparisons before any integration decision.
- Full authenticated repository checkout → `python -I preparedness/tools/validate.py`; `python -I preparedness/tools/build.py`; `python -I -m unittest discover -s preparedness/tests -v`; R295 CLI; verify 35 articles plus six tools export only as WordPress drafts, preserve canonical routes and original content depth.
- Independent scientific/editorial review of source support, chemical/water and food-safety citations, child-data handling, and accessibility.
- Founder approval only **after** successful independent QD; no QD PASS inferred.

**R295 remains DRAFT / HARD HOLD.**
