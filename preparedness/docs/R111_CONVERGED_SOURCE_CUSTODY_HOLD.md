# R111 — Converged seven-cluster / full-slate source and citation custody (Issue #136)

**PRIVATE, DRAFT-ONLY, STRICT HOLD.** No site/CMS/navigation/WordPress writes, branch merges, source rewrites, publication or independent QD PASS. A machine fingerprint is **not a signature**, evidence of accurate claim support, or a qualified emergency/medical safety approval.

## Gap closed

The original 35-article source-URL reviewer roster (R102) and the advanced seven-contributor revision chain (R107–R110) were separately inspected but had no single deterministic reviewer-ready cross-layer gate ensuring neither side silently loses a changed file, citation, qualified warning context, author-specific source reading or review state.

R111 introduces **`preparedness/tools/r111_converged_source_review_gate.py`**. Its read-only `scan()` re-derives the original R102/Library/validator and R107, R108, R109, R110 exact-Git pipelines on a *single trusted checkout*. Its pure `compose()` then verifies original 23 contributor change identities and blob OIDs against R108, the seven changed article records against both R109 and R110, and all 30 literal-URL collision groups against original author-scoped source variants and citation occurrences. Source reuse at a literal URL never becomes shared claim authority.

The private result is a deterministic **HOLD-only** joined reviewer worklist. It includes 23 original/current Git blob comparison workorders, seven flagged claim-neighborhood and adjacent-caveat workorders, and 30 original source-URL groups with only URL SHA-256 IDs and article slugs, never original article prose or source-note text. Existing authored safety states remain untouched, and source review statuses remain NOT_REVIEWED. The 35 articles, one buildable water-planner tool and five unbuilt tools are specifically accounted for. All 15 safety exceptions and 22 editorial decisions stay open.

## Tests and execution

A total of **78 synthetic local Python tests** exercised the exact R111 tool/test Git blobs independently (68 resealed report mutations, ten baseline/integrity checks). They proved the tool rejects attempts to alter contributor and citation OIDs, silently remove an article or collision group, collapse source variants, detach source-use notes, forge review approval flags, drop pending safety/editorial debt or confuse author-specific cite records. No test touches repository source fixtures; input records are in-memory.

Local test command:
```
python -I -m unittest discover -s preparedness/tests -p 'test_r111_*.py' -v
```
Proposed exact-checkout workflows must additionally run:
```
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I preparedness/tools/r111_converged_source_review_gate.py --repo-root . --json
timeout 480s python -I -m unittest discover -s preparedness/tests -v
```
The native builder outputs only **local WordPress-ready DRAFT files** under preparedness/build. Nothing in R111 imports or publishes to WordPress.

### Verification limits

The local scratch container cannot clone the private GitHub repository; therefore, local test PASS is a **pure synthetic module result, not 35-article integration verification**. All five upstream workorders must execute successfully against exact Git objects before R111's integrated reviewer dossier can be trusted. The current GitHub Actions runner-dispatch issue may prevent any steps from executing. If so, explicitly record **UNVERIFIED** rather than suggesting PASS. The older R107 9,183-test hosted result is a different commit.

R111 output is scoped to the known frozen 35-article/23-file/30-group baseline. **A changed count fails closed for renewed human reconciliation; it is not silently ignored and does not purport to be a future-proof general authoring system.** SHA-256 fields are local change detectors, not externally authenticated attestations. HTMLParser text models are not browser DOM or visibility verdicts. Independent original-source claim review, qualified guidance review, browser/print QA, mandatory 13-stage integrity, and independent QD are distinct unfulfilled obligations.

## Current external handoff pins checked Nov 3, 2026 PT

Seven contributor branches: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; history-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; history-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; history-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`.

Separate Preparedness RC PR #584 `ddb3528ba6494dada1fa1c3a142ce746e3a67706`, QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic-fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, homepage PR #49 `10495883299d53596992c26a8987f629b2904670`, flagship PR #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`. All left untouched.

PR #169 still has a temporary `_dup_test.json` write into the shared source tree; its *other* synthetic upgrade fixture is isolated. PR #157 remains unmerged and cannot be counted as independent safety approval.

**Decision: HOLD / NOT REVIEWED / DO NOT MERGE / DO NOT PUBLISH.**