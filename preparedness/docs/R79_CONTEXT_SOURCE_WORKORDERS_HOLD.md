# R79 — Context-Dependent Citation/Source Review Work Orders (PRIVATE / HOLD)

**Scope:** Preparedness Archive, Issue #136. **Draft-only, read-only engineering.** This is a review-routing instrument, not a publication gate override, editorial approval, clinical verdict, or claim substantiation.

**Immutable R78 parent SHA:** \`7b25206767793753860dc4165d7e89f00a105afe\` (draft PR #679). R79 adds exactly four files and does not modify any existing article, source fragment, taxonomy, stable URL, released public content, CMS, home/flagship branch, or independent QA branch. The separate WordPress-ready candidate remains RC PR #584 at \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\`.

## Substantive integration

R79 converts R78's sealed 41-document editorial packets into two complementary, deterministic human-review work queues:

1. **244 source orders**, each preserving the entire original and candidate research readings, both SHA-256 seals, exact URL, all 2,359 distinct-origin citation variant dependencies across the archive, the independent temporal review cues, the full *distinct* list of sources sharing its exact URL, and repeated-ID origin distinctions. Two research readings have no cited variant edge and still remain in the inventory. **Shared exact URLs are never conflated into equivalent supporting claims.**
2. **1,068 consequential lexical-context orders**, one for each preexisting action/quantity review candidate in all 35 articles and six draft tools. Every order includes complete original passage text, byte-exact original block SHA, original document/DOM position, all same-block citations and their uncollapsed source origins, and the entire immediately adjacent preceding and following blocks with their hashes and citation ordinals. **347 candidates have no same-block citation**; these are review cues, not 347 established factual or safety defects. Mechanical cues additionally flag shared-URL source variants, repeated IDs, temporal metadata and missing same-block citations as workload-routing information, not diagnosis or a safety score.

The R79 report **nests the complete R78 parent evidence unabridged** and tests whether a hypothetically re-signed parent still exactly matches an independently reconstructed R77→R78 proof. It independently rebuilds every source edge, checks each against R77 temporal-source provenance, and refuses changes to research readings, citation ordinals, neighboring context, source identities, unreviewed safety flags or seven-cluster census. Its stable source/action tables never create claims of review. Source and action CSV exports are **one-way** and spreadsheet-formula-neutralized; there is no review-response importer.

**No amount of adjacent citations establishes source substantiation or safety.** Presence of warning language nearby is not evidence that it is legally or medically sufficient. The 1,068/347 lexical flags may contain false positives and omissions. A source's dates, URL, and historical accuracy do not authorize use of a historical technique for modern emergencies.

## Pinned machine-only census to reconfirm at exact R79 head

| Review custody item | Expected count |
|---|---:|
| Complete article drafts / tool drafts | 35 / 6 |
| Distinct origin-scoped complete research readings | 244 |
| Individual citation occurrences | 2,173 |
| Distinct citation/source-variant edges (not claims) | 2,359 |
| Original unabridged DOM text blocks | 4,070 |
| Exact shared-URL groups / repeated-ID groups | 32 / 15 |
| Consequential lexical-context work orders | 1,068 |
| Context orders lacking same-block citation | 347 |
| Complete source readings with no cited variant edges | 2 |
| Human source, claim, qualified safety, and independent QD approvals | **0** |

**Run, do not assume, the tests.** On an exact R79 checkout:

\`\`\`sh
python -I -m unittest discover -s preparedness/tests -p test_r79_context_source_workorders.py -v
python -I preparedness/tools/r79_context_source_workorders.py
python -I preparedness/tools/r79_context_source_workorders.py --private-source-csv-stdout > /tmp/r79-sources-private.csv
python -I preparedness/tools/r79_context_source_workorders.py --private-action-csv-stdout > /tmp/r79-action-context-private.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

The isolated R79 test file comprises **91** checks: 41 individually named complete-document dependency tests and 50 source provenance, source-collision, temporal, context, CSV injection, evidence-tampering, HOLD and cardinality safeguards. Hosted exact-head results must be checked before calling it passed. Any outputs remain offline WordPress-ready drafts, not a public deployment.

## Rechecked collaborator refs, 2026-11-02

| Workstream | GitHub head SHA at inspection |
|---|---|
| Claude Start Here | \`2122d856fce9f64887c16df3d52e64be9f59a55b\` |
| Claude shelter | \`5daeaf2dd5ab71806a6b73c91edfb1d8df5da976\` |
| Claude food | \`f911ff7a655de8d81535ea86ec3d65a49ee76648\` |
| Claude health | \`d5ef5bafd68361434dd1cc9209915b8e8a4eaf17\` |
| Claude historical food | \`67e116e536c7410bed30f8f3b1bb8c166f3c223d\` |
| Claude historical home | \`7504a5f099594d635e3dd7332a33a2e1346c43a2\` |
| Claude historical field | \`4e5caf812727953aa45e3bda2d382f2c67b6a09c\` |
| Release candidate (separate) | \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\` |
| Independent start/safety QA PR #157 | \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\` |
| Independent synthetic fixture PR #169 | \`e9cd7766dac59d47ab467d8945269b9146c2aef5\` |
| Homepage lead PR #49 | \`10495883299d53596992c26a8987f629b2904670\` |
| Experience 2.0 flagship PR #604 | \`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176\` |

Independent PR #157 includes an appropriately bounded prevention of household breaker shutdown during drills, a medication caution, taxonomy gating and Red Cross source-type correction; the proposed wording is *not* independently safety approved. PR #169 replaces two source-dependent assumptions with synthetic fixtures, but a separate test still writes \`_dup_test.json\` in the actual shared research-fragments tree; its author must isolate that fixture to prevent parallel-test races. Both PRs remain draft, not merged.

## Mandatory separate integrity remains FAILED CLOSED

R78's exact-head engineering suite passed, but its separate mandatory 13-stage release-integrity run **FAILED at \`seven_cluster_git_parity\`**. Five current Claude contributor branches are ahead of their R14 frozen historical provenance commits; changing the frozen manifest silently would destroy the audit evidence. The independently identified exact diffs need controlled human review and explicit release-baseline decisions.

Additional requirements remain: 206 original human outbound link obligations, **0/244** candidate human source-link checks, 30 original / 32 candidate shared URL scope decisions, 43 fallback source decisions, 15 safety exceptions, 22 release-candidate editorial decisions, qualified independent review of actionable water/food/medical/CO/fire guidance, a real WordPress/browser/print/assistive evaluation, and exact-head independent QD sign-off.

**Release state is HOLD regardless of passing diagnostics.** No merging, no public publishing, no navigation or CMS/WordPress writes, no fake \`QD PASS\`, and no claim that unreviewed emergency advice is medically safe. Content is for private editorial review only.
