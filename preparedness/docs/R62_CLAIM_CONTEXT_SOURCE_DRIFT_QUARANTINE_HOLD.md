# R62 — claim-context and source-lineage review docket (PRIVATE HOLD)

**Issue:** #136. **Parent:** R61 draft PR #559 at exact `bdfd08794ae1a0e31e585dbd28c9b4c0c3ee69c3`. This is a new, isolated private review artifact, **not** a contributor merger, source rebasing, WordPress publication or independent safety approval.

## What the new validator protects

`preparedness/tools/r62_contributor_claim_context_docket.py` generates a deterministic, fingerprinted crosswalk from R61's **both-version** contributor source, article and citation evidence. The CLI requires an exact local Git checkout and runs the original R61 Git-object provenance program; missing original objects/remote tracking references fail closed. The original seven-cluster/29-contributor-article/72-frozen-file custody remains mandatory and distinct from the R58 full 35-article/1,959-original-citation custody.

High-risk changes that now require a specific human review work order include:

- **Unchanged citation IDs but changed advice:** R62 flags changes in the text immediately around an identical citation sequence, as well as changes outside its 180/240-character context windows. Citation order never proves claim support.
- **Inserted, deleted or reordered citations:** R62 keeps separate frozen and proposed work orders, preserving exact source ID, version, ordinal, Unicode codepoint offset, local context, article hash and candidate original reading-record hashes. It does **not** automatically pair citations across versions or alias IDs.
- **Changed source records/URLs/source-use metadata:** the docket can flag source reading changes even where a citing article body has not changed. Different contributor readings with the same ID or exact URL remain separate; never deduplicate distinct research depth.
- **Safety/publication metadata changes:** changes are surfaced, not adopted; either version describing an approval is still an **unreviewed assertion** and never activates a publication gate.
- **Unsigned reviewer CSV:** immutable evidence columns, exact row identity/census, safely escaped previews and protected context fingerprints. A returned note, even one stating “approved,” stays **UNTRUSTED_NOT_REVIEWED**. Spreadsheet formulas, bidi characters, missing/reordered rows and altered citations fail closed.

No original article bodies, source records, metadata, taxonomy, frozen R14 manifest, Git provenance rules, build path, homepage, navigation, WordPress or CMS are changed by this draft.

## Original contributor refs checked 2026-11-01 (Pacific)

| Cluster | Frozen R14 | Observed GitHub ref |
|---|---|---|
| Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` | unchanged |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | unchanged |
| Food | `4b009361277ea1d4617b368f5d45104c7318b284` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `d2212d0ca0750817d3929865d3069835980faf20` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Food | `2acf65ca3efa9b4b5db7976f379b9ea693be43a4` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `f654e600f89c321a480dd8f055be4d13d0673490` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical Field | `a5ce8a62f168db05c95232e3eb385dccd0d19e7f` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |

Five branches remain substantively advanced beyond the frozen R14 baseline, with **23 changed Preparedness files**, including seven changed article bodies carrying 315 frozen versus 334 proposed citation occurrences (+19 unreviewed). These proposed citations have **not** been incorporated into the integrated 1,959-citation baseline.

## Coordination

- Independent safety QD PR #157: `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; independent synthetic fixture PR #169: `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Both remain unmerged drafts.
- Start Here RC #553: `2af10621b0f4b5837f9224bf7f7163cc21590293`; shelter evidence PR #554: `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`. Review candidates only; not incorporated or safety-cleared.
- Homepage flagship PR #550: `6ef459ec76208fc84022328b938d79bf556ac774`; exact-browser QA PR #565: `91ca7a7d0e9e1b22374ea354775a0ae9d985e502`. Left untouched.

## Hosted verification of exact R62 branch (2026-11-01 Pacific)

A NEW isolated **machine-only** workflow `.github/workflows/preparedness-r62-isolated-tests.yml` enforces the exact base SHA and four-file changed-path allowlist. Hosted GitHub Actions run [#41394562900](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41394562900) **SUCCEEDED** for R60 **76**, R61 **69**, and the *exact repository-native R62 test file* **64** synthetic/adversarial tests: **209 passing in total**. These tests do not establish factual claim support or qualified safety review.

The mandatory full private machine integrity workflow [#41394562896](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41394562896) **FAILED CLOSED** at `seven_cluster_git_parity` (`R18_PRIVATE_PREFLIGHT_FAILURE`) because original contributor branch heads differ from frozen R14. Consequently, **do not claim that validation/build, the full repository test suite, all 13 stages or independent QD passed**. The frozen manifest and contributor evidence have not been rebaselined.

## Verify only from a trusted complete checkout

```bash
python -I preparedness/tools/r62_contributor_claim_context_docket.py --summary
python -I preparedness/tools/r62_contributor_claim_context_docket.py --csv > /tmp/preparedness-r62-unreviewed.csv
python -I -m unittest discover -s preparedness/tests -p 'test_r62_contributor_claim_context_docket.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The CSV is a **private reviewer worksheet**, not something to upload to WordPress. The tests exercise synthetic contributor Git objects and tampered documents, but a passing synthetic suite is not independent safety validation. A full hosted CI run may still fail at the existing **R15 seven-cluster parity gate**, which must **not** be bypassed or silently rebaselined.

## Remaining absolute release hold

The 206 tracked human source-link checks, 30 shared-URL groups, 43 fallback relationships, 15 open safety exceptions, qualified review of consequential preparedness and medical guidance, actual WordPress/print/accessibility QA and independent QD approval remain unresolved. No public publishing, CMS/navigation changes, false QD PASS, or assertions that unreviewed emergency/medical advice is safe.