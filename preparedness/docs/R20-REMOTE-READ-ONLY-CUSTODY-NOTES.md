# R20 — Authenticated remote Git-object custody, release HOLD

**Issue:** #136  
**Source of truth:** `R20-REMOTE-GIT-OBJECT-CUSTODY-HOLD.json` at this draft branch  
**Reference integrated commit:** `f7b73e0235f95c3b6a86dd4660a21c9d8f184bf0` (R13)  
**Exact authenticated comparison head:** `39a87feb8dea92661c30b591012d3879198d69e0` (R19).  
**Observation date:** 2026-10-31 UTC. **Authority:** Git-object preservation, *not* editorial clearance.

## Why this independent route exists

GitHub Actions private preflight run [#41200742724](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41200742724) failed before a runner was assigned or a single step executed. The R18 native eleven-gate suite therefore cannot legitimately be marked passed. This draft uses authenticated GitHub Git-tree and live ref reads to provide a narrower, reproducible **machine custody** check that does not depend on a runner. It is not a substitute for running the native build, render/parity gates, source verification or qualified safety review.

## What was actually checked

The attached JSON freezes **216 live Git-object comparisons** across 72 contributor-owned paths: author-commit blob, R13 frozen integration blob, and R19 current integration blob. All seven contributor refs were independently fetched and matched their original author commit IDs. All 72 integrated versions matched the frozen R13 manifest. There are 71 byte-identical author/integration pairs and **one explicitly unresolved metadata exception** for `preparedness-real-households.meta.json`. That exception is **not** a PASS.

A separate **81-path preservation check** confirmed exact unchanged Git blobs for all 35 article body/metadata pairs (70 paths), water planner body/metadata (2), and original source evidence files (9: base register, crosswalk, seven contributor fragments) between R13 and R19. No source body/metadata was rewritten and no new article routes were created for this draft.

The source crosswalk continues to contain 30 shared-URL groups and unread placeholder records; none has been independently human approved by R20. Git-object identity proves preservation only. It cannot verify that any URL works, that article citations support claims, that reading depth is sufficient, or that current emergency advice is safe.

## Local reproducible engineering (not yet hosted CI)

The accompanying R20 engineering bundle includes a read-only `remote_git_custody_gate.py` that verifies actual GitHub tree/ref data without a clone and a 48-test adversarial suite. **48/48 new tests passed** locally; **856/856 locally available reconstructed R10–R20 tests passed**. Those tests use synthetic fixtures. The standalone implementation is provided in the downloadable engineering package; it is **not part of this PR's file diff**, so this PR does not claim hosted execution or GitHub-reviewed Python implementation.

The full actual checkout, `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, all native Python tests, the rendered 1,959-citation audit, review of 30 shared-source groups, and qualified emergency/medical safety checks remain outstanding. Independent QA PR #157 has stale article patches and source differences; synthetic fixture PR #169 remains unmerged. Never apply either over preserved source/article content without review.

**RELEASE HOLD.** No WordPress writes, site navigation updates, external publishing, safety approval, or QD PASS. Do not call this manifest a release authorization. Any contributor ref movement, article correction, or base SHA change requires a fresh, separate review and new Git-object audit.
