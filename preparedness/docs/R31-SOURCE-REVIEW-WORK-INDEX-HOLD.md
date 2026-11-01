# Preparedness Archive R31 — deterministic human-review work index (DRAFT / HOLD)

Issue: #136. Base: R30 PR #369 at `6a69e3ce6b0b19bdf0613323427229fdf1c7a322`.

## Purpose and change boundary

The mandatory R25 citation-source review packet now runs the independently maintained R31 index validator before it can succeed. Existing thirteen-stage release-preflight sequencing and JSON output remain unchanged; no workflow, article, metadata, taxonomy, source, CMS, homepage, navigation, or public file changed.

R31 separately provides a stdout-only reviewer work index:

```shell
python -I -B preparedness/tools/citation_review_index_gate.py --repo-root .
```

The index deterministically assembles one record per **article or tool**, plus a URL-indexed list of **unmerged original selected-source relationships**. It carries the parent evidence-packet SHA-256, per-row evidence SHA-256, article-body digest, article-specific source-use digest, individual citation offsets/counts, original source identity and contributor origin. The original R25 packet (including entire source records and unabridged reading-depth explanations) remains authoritative and unchanged. Neither related sources nor overlapping URLs are collapsed into one contributor's reading scope.

## New fail-closed protections

The validator independently rederives and checks: frozen 35 articles + one tool, 1,959 source citations, 367 article-source relationships, 43 base-origin fallbacks, and a pending-human-review count of 30 shared URL groups; uniqueness of article/source keys; per-article body identity consistency; uniqueness and count parity of original Unicode token offsets; source record / scope hashes; source ID / URL / publisher-record fidelity; valid source date syntax; HTTPS source URL authority without embedded credentials, ports, control characters, ambiguous backslashes, non-ASCII authority or numeric host; and every explicit FALSE on machine-claimed human source, medical/emergency safety and QD approval.

These are **static integrity checks**, not live source-link verification, source trustworthiness proof, claim validation, legal/medical advice, or a rendered-browser accessibility assessment. Punycode hostnames are preserved verbatim but require independent identity review. URL syntax validation does not replace a qualified human opening and checking each source.

## Testing and execution boundaries

Available local reconstructed engineering suite: **910 collected; 909 passed, one skipped** on Python 3.13. **78 new R31 tests passed** (synthetic acceptance, tamper mutation, URL authority, no false review states); **63 inherited R25 regression tests passed**. The R30 private workflow file used for these local tests was recovered byte-for-byte at blob `8db2a5e1c34506de2b06f56f01e4e03be7b130da`. The locally tested R31 Python implementation, tests, and modified R25 packet gate were verified by GitHub blob SHA equality.

The full trusted checkout is still unavailable to the local environment (GitHub DNS resolution failure); the native 13-stage preflight, WordPress private build, full repository test suite and GitHub-hosted validation **have not passed**. Do not treat the reconstructed suite as native certification.

## Coordination custody (rechecked 2026-10-31)

Claude cluster branch heads: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `4b009361277ea1d4617b368f5d45104c7318b284`; health `d2212d0ca0750817d3929865d3069835980faf20`; historic food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`; historic home `f654e600f89c321a480dd8f055be4d13d0673490`; historic field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`.

Separate draft safety QA PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and isolated synthetic fixture PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5` were inspected, **not merged**. Homepage PRs #49 and #254 are unrelated, unmodified. Two source taxonomy records use an internal safety-approved-draft designation; one metadata record identifies founder review, which must not be construed as independent qualified medical review or QD PASS.

## Explicit outstanding release conditions

**HOLD.** Human verification of the 30 crosswalk groups, 43 base fallbacks and individual citation claims; qualified assessment of high-consequence emergency/medical/food/water guidance; independently verified live links and rendered accessibility; trusted native build; hosted CI execution; and independent exact-head QD approval remain outstanding. No WordPress writes, publishing, branch merges, navigation changes, or false approval were performed.


## Hosted runner breakthrough and failure-only diagnostics

GitHub Actions run [#41256381732](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41256381732) **did assign a hosted Ubuntu 24.04 runner**; fetched a full Git history, pinned Python 3.12.15, passed the workflow contract gate and reached the real thirteen-stage private preflight. The preflight returned exit code 2; its stdout was redirected to a private runner-local file, so its precise failing stage was not visible in the logs. It was **not** a pre-runner failure. It is unsafe to infer a successful build or which content gate failed.

R31 therefore includes a second bounded engineering repair: on preflight failure only, stderr prints a machine-readable source-free HOLD record containing the named failing gate (if detectable) and SHA-256 of the original error message. Raw filesystem paths, evidence, private document contents and human review notes are never echoed to the CI log. The original stdout JSON failure receipt and all fail-closed exit codes remain unchanged; the signed/pinned workflow itself remains unmodified. Added **22 isolated diagnostics tests**, including all thirteen named stages, setup failures, PII-leak prevention and false-approval checks. Updated reconstructed suite: **932 Python tests collected; 931 passed and 1 skipped**. The new production/error telemetry and test files are byte-identical to the locally tested code at blobs `7c8d39a1eda77374fe75a887b78468f59308da12` and `e0771c1a743ecd33d4ab4c3717dff17430b6fc01`. The native hosted job is still HOLD pending exact-head execution evidence and remediation of the identified failing stage.
