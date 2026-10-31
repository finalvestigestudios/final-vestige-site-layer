# R11 — WordPress draft-export custody and stale artifact fail-closed gate

**Scope:** Preparedness Archive integration/citations only, Issue #136. **Release:** `HOLD`, `may_publish=false`. R11 is stacked on R10 draft PR #239 (`e209d0dccc5f5e140a4f4b6320f0dcb89d4571b0`). The 35 source articles, one water-planning tool, all contributor source fragments, WordPress, and public navigation remain unchanged. Neither QD PASS nor medical, food-preservation, water, fire, or generator safety has been established.

## Newly addressed vulnerability: old files survive local rebuilds

The existing `preparedness/tools/build.py` performs validated, local draft export, but writes into persistent `preparedness/build/wp/` and `preparedness/build/preview/` directories without removing previous runs' orphaned files. A renamed, removed, manually edited, or stale HTML export could therefore remain alongside the current 35+1 drafts. An external operator selecting files from that directory might accidentally import an obsolete or safety-label-stale artifact. `build-report.json` is not itself a cryptographically bound file index. This is an *artifact-custody* weakness, not evidence that the current repository has a stale artifact or that the drafts are medically safe.

## R11 controls

New read-only tool: `preparedness/tools/draft_export_custody.py`.

1. In the exact private repository checkout, run the existing Git-blob evidence lock, native structural validator, and R10 canonical claim/source gate first. If **any** fails, R11 does not endorse an output.
2. Require exactly **35 unpublished article drafts + one unpublished water planner**, article/tool slugs constrained to path-safe characters, complete taxonomy, and the currently frozen **224 source reading records, 30 unresolved URL groups, and zero independent human source-link checks**. This baseline intentionally fails if it changes until an authorized source-inventory review updates the gate.
3. Independently rebuild WordPress HTML, noindex preview HTML, hub pages and landing page in memory from current `build.py` renderer functions. Compare every expected file **byte for byte** with the actual generated files. Stale content, changed warning labels, removed source notes, altered article text, modified previews and partially written outputs fail.
4. Forbid **extra files, stale routes, backups, unexpected folders, symlinks and hard-linked content** in the two export directories. Files must be direct children of `preparedness/build/wp` and `preparedness/build/preview`, with bounded sizes; input paths may not escape the exact checkout build directory. R11 never deletes stray files itself: a human operator can inspect and clean them safely before rerunning.
5. Recompute all `build-report.json` fields directly from source, including canonical article URLs, reading-time/word counts, citation-ID order, hub counts, landing counts, full draft status, source rows and unresolved collisions. Reject altered status, counterfeit QD status, a WordPress publication claim, or public-mode index listings. The reported file hash index is **diagnostic machine custody**, never release authorization.
6. Emit a `HOLD` summary and optional private receipt. **No WordPress APIs, CMS writes, navigation edits, deploy actions or public-page publishing** are reachable from the code.

## Safe execution in a trusted checkout

```sh
# This prerequisite generates *only* private WordPress draft-markup files.
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
# Canonical source and claim audit is invoked inside R11's CLI.
python -I preparedness/tools/draft_export_custody.py \
  --json-out preparedness/build/private-R11-HOLD-export-custody.json
python -I -m unittest discover -s preparedness/tests -p 'test_*.py' -v
```

The local `build` command may leave extra files behind from old runs; R11 is intentionally strict. To resolve this, **only after examining the contents**, move the old build aside into a non-public local location and rebuild. Do not delete review evidence or claim an extra file is harmless without inspecting it.

## Evidence and limits

R11's test file covers synthetic WordPress-export fixtures, tampered review metadata, stale/extra files, URL/citation report mutations, symlinks, hardlinks, false publication and QD flags, source-custody drift, and idempotence. **82/82 isolated Python tests passed locally under `python -I` on 2026-10-30 America/Los_Angeles.** Tests in the private GitHub checkout, actual 35+1 WordPress export, the full repo suite and the 1,959 real occurrence records remain **unexecuted in this container**: `git ls-remote` fails with `Could not resolve host: github.com`. Authenticated GitHub connector was used to inspect current source and branch SHAs but cannot mount a full git working tree for local tests.

R11's byte comparison uses `build.py` itself as the reference renderer. It establishes **output parity with the frozen input and generator**, not factual accuracy, validated article health advice, WordPress editor compatibility, real source-link validity, independent QD approval, or authenticity of an external reviewer. Review of all 1,959 individual citations, including 30 shared-source reading-scope groups and qualified human assessment of consequential advice, remains mandatory.

## Coordination inputs verified on 2026-10-30 21:xx PDT / 2026-10-31 UTC

Seven contributor tips: Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, Food `4b009361277ea1d4617b368f5d45104c7318b284`, Health `d2212d0ca0750817d3929865d3069835980faf20`, History Food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`, History Home `f654e600f89c321a480dd8f055be4d13d0673490`, History Field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`.

Preparedness integration `c8df99cc661e518e93e58e1cc1ea3d7256f58643`; independent QA PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic-fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; R10 PR #239 `e209d0dccc5f5e140a4f4b6320f0dcb89d4571b0`; separate homepage lead PR #49 `10495883299d53596992c26a8987f629b2904670`; separate Experience PR #238 `918155c271d44e421baadcb3e4b92e71ea6ce683`. All remain independent and unmodified by this sprint.