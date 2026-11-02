# R72 — Origin-scoped source collisions and downstream passage-impact docket (PRIVATE HOLD)

**Issue:** #136. **Additive base:** R71 draft PR #631 at SHA 41edfb1155a8b62ab0a4d5d4c638f5b14c5d0746.
**Read-only independent RC:** PR #584 at SHA ddb3528ba6494dada1fa1c3a142ce746e3a67706.

## Purpose and boundaries

R72 is a review-only deterministic reconciliation layer over R71's complete
sealed source-to-block ledger. It makes source-scope ambiguity reviewable in
both directions: a URL shared by different research records is not one
verified source; an identical source ID reused across origins is not
permission to transfer verification or a safety verdict. Every reading
remains unabridged and separate, cited or uncited. All original R71 DOM
text, citations and provenance stay intact. No article/source rewrite.

The original evidence is 35 articles plus one water-planning tool, with
1,952 article citations + seven tool citations = **1,959 original occurrences**.
The separate proposed RC has 35 article drafts, six tool drafts, 244
unabridged source readings, and 2,173 candidate citation occurrences.
These distinct inventories must not be treated as directly subtractable.
R72 leaves the frozen originals and seven contributor baselines unchanged.

## New reviewer docket

* Checks R71 source and claim report seal/HOLD, complete source reading JSON,
  exact source URL, origin + source ID, original reading if present, and
  complete R71 DOM passage/citation work orders.
* Independently reconstructs every same-block citation edge and source-origin
  reverse index by article/tool, DOM block and citation ordinal. Exact URL and
  complete source SHA are required; missing, duplicated, retargeted, reordered
  or changed preferred source variants fail closed.
* Preserves uncited source records and queues citations not anchored to DOM
  blocks; neither is silently discarded.
* Creates two independent reviewer queues: shared **exact URL** and reused
  **source ID** across contributor origins. Neither implies equivalent
  research scope, factual failure or human approval. Each collision includes
  downstream exact citation occurrence pointers and distinct source SHAs.
* Creates 41 private per-document draft URL/block work orders.
  Same-block citations and adjacent hints remain NOT evidence of support.
  Topic keyword classifications remain editorial triage, NOT safety findings.
* Generates a formula-injection-neutralized private CSV collision docket,
  with reviewer notes explicitly untrusted and no approval importer.
  No URLs accessed, CMS access, publishing, or WordPress writes.

The validator rejects manufactured human/QD/safety approval, source reading
truncation or mutation, broken original SHA, duplicate/lost documents or
citation occurrences, changed private URLs, source/reverse graph drift,
inconsistent exact source identities/URLs, and modified topic-review totals.
The adversarial tests re-sign mutated reports to exercise structural checks,
not simply the outer report checksum.

## Exact-checkout commands (private only)

    python -I -m unittest discover -s preparedness/tests -p test_r72_source_scope_collision_impact.py -v
    python -I preparedness/tools/r72_source_scope_collision_impact.py
    python -I preparedness/tools/r72_source_scope_collision_impact.py --collision-csv-stdout > /private/r72-scope-collisions.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

A dedicated draft PR GitHub Action pins the exact R71 parent, seven Claude
contributor heads, RC source SHA, and four-file additive scope. Isolated
test success does NOT override the mandatory 13-stage release pipeline.
The latter remains FAILED CLOSED at seven_cluster_git_parity; do not claim
a green release without that exact independent pipeline.

## Coordination (read-only, 2026-11-02)

| Lane | Verified head |
| --- | --- |
| Start | 2122d856fce9f64887c16df3d52e64be9f59a55b |
| Shelter | 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 |
| Food | f911ff7a655de8d81535ea86ec3d65a49ee76648 |
| Health | d5ef5bafd68361434dd1cc9209915b8e8a4eaf17 |
| Historical Food | 67e116e536c7410bed30f8f3b1bb8c166f3c223d |
| Historical Home | 7504a5f099594d635e3dd7332a33a2e1346c43a2 |
| Historical Field | 4e5caf812727953aa45e3bda2d382f2c67b6a09c |
| RC #584 | ddb3528ba6494dada1fa1c3a142ce746e3a67706 |
| Independent QA #157 | 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; draft, unmerged |
| Synthetic QA #169 | e9cd7766dac59d47ab467d8945269b9146c2aef5; draft, unmerged |
| Homepage #49 | 10495883299d53596992c26a8987f629b2904670; unmerged, untouched |
| Flagship #604 | 5f87f1b0a48ed2f17ecca49a60c44a482ca530de; draft, untouched |

Independent #157 changed files/patches inspected: electrical drill should
not disable main household power, refrigerated medication needs qualified
product-specific guidance, American Red Cross is a nonprofit, Start Here
safety taxonomy needs gates, and negative publish tests. These are proposed
QA repairs, **not qualified medical/emergency safety approvals**.
Independent #169's isolated synthetic food-source upgrade tests were
inspected; neither fixture changes nor a passing test is source approval.

## Mandatory publication HOLD

Known outstanding requirements: five historically diverged original
contributors versus frozen provenance; 206 original historical human link
checks, zero candidate human link checks on the 244 RC records, 30 original
and 32 candidate shared-URL groups, 43 original fallback relationships,
15 unresolved safety exceptions, 22 independent founder/editor decisions,
qualified consequential-advice review, actual WordPress/browser and
assistive-technology QA, and independent QD approval.

No publishing, no public navigation changes, no CMS writes, no article edits,
no crosswalk rebaseline, no homepage/flagship edits, and no assertion that
unreviewed food, water, medical, fire, generator or emergency advice is safe.
