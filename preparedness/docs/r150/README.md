# R150 — Preparedness tool source-origin migration SHADOW audit (DRAFT / HARD HOLD)
**Issues:** #136 (engineering) / #820 (conversion) / #818 (charter).  
**Immutable R149 parent:** `4fb42c6838b0ff486a1956914029c300d166de19`.  
**Date:** 2026-11-05. No public publishing, WordPress/CMS, navigation, email, social posting, merchant or analytics changes.

## Source impact independently calculated from authentic frozen GitHub data
The existing builder selects `article_origins[slug]` or `base`. Five implemented tool slugs are not mapped to their author-specific source fragments. R149 recorded 67 tool/source-use relationships and 173 citation-token occurrences. The new R150 **shadow-only** before/after model expands the analysis beyond the 58 currently unresolved identifiers:

| Risk before proposed remapping | Tool/source relationships | Citation occurrences | Release action |
|---|---:|---:|---|
| Missing current source ID, candidate fragment provides source | **58** | **142** | Each source and author-specific use requires qualified review |
| Currently resolves, but remapping silently switches to a different source record with the same ID/URL | **4** | **15** | **NEW R150 detection**: review changed title, support statement, verification-date/notes/publisher; URLs being equal is NOT approval |
| Currently resolves and candidate source record is byte-equivalent | **5** | **16** | Still requires review; existing link flag not true |
| **Totals** | **67** | **173** | **HOLD** |

The four *affected tool/source relationships* are:
1. `home-fire-escape-worksheet / usfa-fire-escape` — base → shelter; source title, `verified_on`, notes and `supports` change.
2. `kit-builder / ready-are-you-ready` — base → start; title, `verified_on`, notes, `published` and `supports` change.
3. `power-outage-planner / fsis-power-failure` — base → shelter; title, publisher, `verified_on`, notes, updated and `supports` change.
4. `reunification-plan / ready-are-you-ready` — base → start; same source-variant change as kit-builder.

These are **3 distinct source IDs** in **4 relationships**, responsible for **15 citation occurrences**. The source URLs happen to be unchanged; the source reading/claim scope is not. Counts are deterministic textual metadata differences, not expert medical or factual judgments. The source rows still have `human_link_check: false`. **Zero** source changes are authorized.

## Engineering
`preparedness/tools/r150_origin_migration_gate.py` is a read-only, fail-closed, Git-blob-custodied before/after source-origin impact verifier. It uses R149's pinned 16 original tool and source objects, rejects duplicate/forged IDs, changed source URLs, altered author-specific explanations, missing citations, invented reviewer approvals and expected-impact drift. Its optional `--report /path/to/private-report.json` generates a reviewer-only 67-row report; without the flag it emits a short JSON summary. It **always exits 2** because structural custody cannot approve source claims, medical safety, QD, commerce or public release. No source/crosswalk files are modified.

`preparedness/tests/test_r150_origin_migration_gate.py` contains 38 unittest methods, including 240 per-row adversarial subcases and 28 further negative tests. **38/38 locally executed synthetic tests passed,** and both Python files compiled. Exact committed Git blob identities must be checked against the locally tested files. This is NOT an authenticated whole-repository run.

In a trusted, exact-head checkout (no CMS writes):
```sh
python -I preparedness/tools/r150_origin_migration_gate.py --preparedness preparedness --docket preparedness/docs/r149/tool-source-use-review-docket.json --report /tmp/fv-r150-tool-source-impact.json
# Intentionally exits 2 / HARD HOLD. Report is local and reviewer-only.
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

## Seven Claude contributor branches — fresh actual head check
The crosswalk's 2026-11-04 source-head commits are **frozen integration snapshots**, NOT a guarantee that a named contributor branch still points to them. On the current check, **2/7 matched**, **4/7 advanced**, and **one (food) diverged**. This supersedes earlier claims that all seven current branch tips were unchanged.

| Cluster branch | Crosswalk pinned SHA | Actual branch SHA (2026-11-05) | Compare pinned → actual |
|---|---|---|---|
| claude/prep-start-bbfeb8 | `2122d856fce9f64887c16df3d52e64be9f59a55b` | same | identical |
| claude/prep-shelter-5e1e0e | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | same | identical |
| claude/prep-food-ccdc55 | `e9cd7766dac59d47ab467d8945269b9146c2aef5` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | diverged, 1 ahead / 1 behind; test and cluster-doc changes |
| claude/prep-health-837444 | `d2212d0ca0750817d3929865d3069835980faf20` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | 1 ahead; cluster-doc changes |
| claude/prep-hist-food-b81f19 | `2acf65ca3efa9b4b5db7976f379b9ea693be43a4` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | 1 ahead; two articles, source fragment, tests |
| claude/prep-hist-home-0e0e38 | `f654e600f89c321a480dd8f055be4d13d0673490` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | 2 ahead; three articles, source fragment |
| claude/prep-hist-field-9db767 | `a5ce8a62f168db05c95232e3eb385dccd0d19e7f` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | 1 ahead; two articles, source fragment |

**No upstream branch was changed or integrated.** Seven later revised article bodies across hist-food/home/field must enter the same lossless article/citation/reading-depth reconciliation and 32 shared-URL group review, not automatic cherry-picking. PRs #157, #169/#973 remain separate unresolved QA/fixture drafts; homepage PRs #49/#604 untouched. All 35 articles remain DRAFT / HOLD. The branch drift does **not** establish that the current release candidate has changed.

## Conversion-first Preparedness scope: ONE proposed free journey, paid SKU still unverified
Proposed matched intent: parent/caregiver household emergency contacts and school pickup/reunification. Authentic **free** `household-emergency-plan` article → optional **free** `family-reunification-card` printable. Both need source/safety review, draft build, mobile/print/privacy QA before promotion; the card has 11 currently unresolved source IDs. No verified FV-owned, rights-cleared, actually purchasable Preparedness pack in the evidence. **No paid button, upsell or checkout URL may be invented.** TASK-008 and dated Grok/Praxxis handoff have no verified matching Preparedness asset_id/post URL/destination; Grok retains all creative, scheduling and posting.

**Unpublished editorial CTA candidate:** “Practice your family's contact plan. Review the free Household Emergency Plan, then use the optional Family Reunification Card once its source and print/privacy checks are complete.” Not approved for public deployment.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Matching paid pack → verified paid order | No authenticated rights-cleared buyable SKU | Verify existing merchant item, price, terms, checkout, delivery, refunds; no new offer created | **HOLD; revenue unverified** | Commerce / Claude / founder |
| Free guide → reader | 35-article safety/source + independent QD incomplete | Preserve rich original text and citations, complete full native gates | **DRAFT; not promoted** | Preparedness / independent QA |
| Guide → Family Reunification Card | 11 source IDs; print/privacy/360/390px untested | Adjudicate 11 relationships then staged download/print/offline QA | **R150 structural reviewer gate BUILT, real UX NOT TESTED** | Preparedness / Site QA |
| Grok asset → approved guide | Asset ID/destination absent | Reconcile TASK-008 with Praxxis without changing Grok queue | **UNVERIFIED** | Grok / Praxxis |
| Session → CTA → confirmed lead → merchant-confirmed sale → net | No qualified-human denominator, offer or merchant evidence | Preserve #820 existing privacy-safe instrumentation; reconcile real orders/refunds/fees for 7/30-day cohorts | **Net $ per 1,000 qualified sessions NOT COMPUTABLE** | Claude / Commerce |

Safety instructions are free, not gated by lead forms. Existing Focus Fieldbook signup is separate; retired water freebies stay retired. No false merchant, lead, medical safety or QD approval claims.
