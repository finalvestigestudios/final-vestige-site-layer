# R64 — Full Article-to-Source Dependency Review (PRIVATE / RELEASE HOLD)

**Owner:** Preparedness Archive integration, Issue #136. **Status:** isolated draft, unreviewed; never publish or treat as qualified medical or emergency guidance approval. **Parent:** frozen exact R63 draft PR #572 at `c0117fa41c058e55926aaa62ee7440fbcad680fe`.

## Why another gate is needed

R61/R62 preserve original and proposed contributor text and claim context. R63 preserves all original and proposed contributor source readings, including uncited materials. The remaining handoff problem is **bidirectional coverage for a specific article/source pair**: a reviewer must see the full old/new occurrence list, unchanged-but-reworded manuscript, exact original/proposed source-reading candidates, and the historical source-use note *together*, without treating same URL, same citation ID or current contributor branch as a factual or safe replacement for the frozen source.

This R64 draft adds **one stable review work order for every article/source ID union across both versions** of all 29 original contributor articles. Sources absent from citations but appearing in article metadata still receive their article/source work order. Uncited source records remain preserved in the complete R63 parent inventory and are NOT misleadingly represented as supporting a claim.

The dossier distinguishes:
- Citation multiplication/removal/ID resequencing without guessing which historical occurrences match.
- Changed context or codepoint positions even where the citation ID is unchanged.
- Changed article body, metadata, safety-state fields and publication-state fields without approval.
- Added/removed/altered contributor source candidates, cross-contributor reused source IDs, and exact shared URLs **without aliases**.
- Incomplete coverage within the seven original clusters; references outside seven must separately be reconciled against complete R58 35-article custody.
- Exact original/observed source-use presence and unabridged notes, including null vs absent.

The exhaustive JSON contains full original/proposed citation contexts and original contributor source records with complete reading notes; the protected CSV contains only compact source/identity/census keys and one optional, **unsigned** untrusted note column. Neither can grant QD, human verification or medical/emergency guidance safety clearance.

## Source-of-truth and reproducibility

The CLI never trusts a saved summary. It calls R61 with `python -I` on actual Git objects, regenerates R62 and R63 reports, and validates the entire R63 report before R64 construction. All per-article source ID unions and every original and observed citation occurrence are independently counted with exact deterministic fingerprints. R64 preserves R63's full original source inventory by parent fingerprint and does not copy/merge/rewrite contributors.

Run only on a trusted, exact checkout with all original seven refs present:

```sh
python -I preparedness/tools/r64_article_source_dependency_review.py --summary
python -I preparedness/tools/r64_article_source_dependency_review.py --csv > /tmp/r64-private-notes.csv
python -I -m unittest discover -s preparedness/tests -p 'test_r64_article_source_dependency_review.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The dedicated R64 workflow also runs R60–R63 targeted tests, read-only real Git provenance, complete native validation/build and full native Python tests as **diagnostics only**. The separate mandatory 13-stage private integrity pipeline remains FAIL CLOSED at `seven_cluster_git_parity` until independently resolved. Do not bypass, rebaseline, or convert a diagnostic pass into release approval.

## Exact contributor refs verified before creating this draft (2026-11-02 UTC)

| Cluster | Branch | Observed Git SHA | Frozen R14 |
|---|---|---|---|
| Start Here | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` | unchanged |
| Shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | unchanged |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | advanced / unreviewed |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | advanced / unreviewed |
| Historical Food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | advanced / unreviewed |
| Historical Home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | advanced / unreviewed |
| Historical Field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | advanced / unreviewed |

The exact independent QA heads were also inspected: PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (safety wording/taxonomy) and PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` (isolated synthetic food fixtures). Both are unmerged drafts; neither is copied wholesale. Current homepage work PR #573 `6c513b9cec57494230063269dee60f6e637646a6` remains separate and unchanged.

## Known safety/governance HOLDs

Five original contributors advanced beyond R14 (23 changed paths; 7 changed manuscript bodies with 315 frozen vs 334 proposed citation occurrences, +19 **unreviewed**). Original integrated 35 articles, 1 water planner, 1,959 citation occurrences remain separate and unchanged. R64 covers 29 original contributor articles and does **not** claim to revalidate six separately integrated articles.

Human source verification remains 0/206 tracked, 30 shared-URL groups, 43 source fallback relationships, 15 open safety exceptions, high-consequence guidance requiring qualified review, installed WordPress/browser/print/accessibility QA and independent QD still unresolved.

**NO** article changes, source-record rewrites, original provenance rebaseline, live WordPress/CMS/navigation/homepage writes, public publish, merge, unsigned-note approval, or assertion of safe unreviewed medical/food/water/emergency advice are authorized.
