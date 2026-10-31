# R23 — 81-file Preparedness Archive provenance gate

**Issue #136 · DRAFT / RELEASE HOLD · 2026-10-31.** This establishes original-content custody only. It is not source accuracy verification, human review of any medical/emergency instruction, permission to publish, or an independent QD PASS.

## New constraint

R22 independently froze the ten original source/taxonomy JSON blobs but did not require its native CLI to prove that the 70 original article body/metadata files and the two water-planner draft files still matched the frozen integrated baseline. A changed body could preserve a citation *count* while altering its surrounding medical, power, water, or food guidance.

R23 extends the **existing** `preparedness/tools/source_group_review_gate.py` CLI after its R22 source crosswalk checks. It independently pins the R20 evidence manifest Git blob `121d8f918c46ab55c666b540f74992bc9ff6e95d` and the original taxonomy Git blob `eea601e53e16e36cd4fc890876bc249b39632370`. It then requires exact original blobs for **35 article bodies, 35 article metadata records, two water-planner files, and nine source/crosswalk files (81 total)**. It verifies the complete original 35 unique URLs and six-tool slate, current safety-gate values through pinned taxonomy bytes, exact original source-use discrepancy, no unreviewed extra draft article/tool/fragment files, no symlink escape, and no coordinated source+manifest substitution. Every successful report still says `release_state=HOLD`, `may_publish=false`, `independent_qd_pass=false`, `medical_safety_approved=false`, `human_source_review_complete=false`.

**No legitimate editorial updates are automatically approved.** Changed material must receive a separate, reviewed baseline/evidence record; the machine must fail closed rather than update the frozen author record itself.

## Evidence actually checked

At exact R23 code+test commit `94f14b32ac8411a5975f6eadb4d380deb9a84aeb`, authenticated GitHub Git Tree `9470b6acfd781e47ac85eb0d1564acdfd2b9c9b7` was nontruncated (208 entries). Comparing its Git blob IDs and regular-file modes to the pinned R20 81-entry corpus manifest yielded **81/81 matches**, including 70 original article files, two tool files, nine source/crosswalk files, and **zero** differences. The pinned R20 manifest and taxonomy themselves matched their frozen Git identities. This was a **remote Git-object check**; it was **not** execution of the native Python gate against a complete local repository checkout.

All seven original Claude contributor branch commits remain at their pinned SHAs (`start 2122d856`, `shelter 5daeaf2d`, `food 4b009361`, `health d2212d0`, `hist-food 2acf65ca`, `hist-home f654e600`, `hist-field a5ce8a62`). Independent QA PR #157 still targets older safety wording, and synthetic-fixture PR #169 remains a separate draft; neither was merged. Homepage PRs #49 and #254 remain separate and untouched.

## Executed tests and unresolved gates

The two changed Python files were retrieved from GitHub and their Git blob IDs independently matched the locally executed files. **197 committed-scope Python tests collected: 195 passed, two explicitly skipped** because a complete trusted checkout is not locally available. This combines the 97 R21/R22 source-group tests and 100 new R23 regression tests (81 per-file byte-drift mutations plus source/manifest/taxonomy safety-state cases). The earlier 120-test larger local-only adversarial suite is not included in this committed-scope count. Native 35-article validation, WordPress draft build, full R18 private preflight and hosted CI remain **unexecuted** due to lack of local full checkout / GitHub Actions pre-runner failure.

The original 30 shared-source groups and 1,959 citation occurrences still need independent examination. Qualified review of consequential emergency or medical advice, the known additive `preparedness-real-households.meta.json` reading-scope explanation, source author/food-fixture provenance difference, full native build and independent QD approval remain **HOLD**. No WordPress/CMS writes, publishing, navigation changes, homepage changes, branch merges, or safety approvals took place.
