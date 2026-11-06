# R243 — Checksum inventory publication inode custody (six Windows candidates)

**DRAFT / independent QD + founder HARD HOLD; issue #73.** Based only on immutable R242 head `45f82fb8b7aef8801fd5aa9d3eaadc541ffac36e` ([draft PR #1310](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1310)). Not based on or merged into production `main`.

## Security failure and change

The shared `build_inventory.py` creates the SHA256SUMS.txt manifest for the four free and two premium Windows candidates. R242 verified staged bytes before publication, but R242 still captured the manifest's device/inode **after** `os.link(stage, target)`. A post-link `target.lstat()` failure stranded a published checksum manifest: rollback had no identity to compare. Worse, another writer swapping the linked target with a different regular file before the identity capture could make that replacement look like our own file; a later verification failure could delete the replacement. Even a byte-identical replacement could be accepted as a successful publication.

R243 captures the **validated staging inode before linking** and uses this pre-publication identity for rollback. After `os.link`, it separately confirms the published file is regular and has the exact same device/inode, failing closed if another object appeared. Cleanup only unlinks a regular target **when its identity matches the staging inode**, and preserves unrelated replacements; existing non-overwrite link, checksum, six-entry inventory, staging cleanup, redacted exceptions and human release gates remain intact. This is defense in depth, not immunity to all hostile concurrent filesystem races.

## Reproduction and execution evidence

The exact R242 Git blobs (`build_inventory.py` `e5e559016778326dc3957639034f5e6b70e6d2de`, `candidate_guard.py` `cc92c58246196f284ea12659621a347bd96e4fe9`, inherited test file `163a4ae329017fb57d8d0db36fd659177ade207a`) were reconstructed and checked with `git hash-object` before testing on **local Linux CPython 3.13.5**.

Against *unmodified* R242, the twelve new R243 fault/acceptance tests showed **6 failures, 1 error, 5 passes**. The failures covered stranded linked manifest following post-link permission/ENOENT/I/O faults or interrupts; a different inode with byte-exact content being accepted; and deletion of an unrelated corrupted replacement.

Against patched source blob `44af90fe06e80a7f7575391da9985060716fcb80` and the new test blob `b06cd2249487cc1d21392f971efc57ca3237d8fb`, all **12/12 R243 + 19/19 inherited R242 tests PASS** in normal and optimized (-OO) modes, **62/62 passing local method executions**, zero skips. `compileall` PASS. Tests use synthetic bytes, real local files/hardlinks, and controlled failure injection; **no actual EXE was executed, scanned or released**.

From repository root:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_inventory*'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_inventory*'
python -m compileall -q products/desktop/build_inventory.py products/desktop/tests/test_inventory_publication_identity_r243.py
```

The checked workflow adds 12-case normal and -OO R243 tests to **Ubuntu source-tests** and **Windows prepackaging** steps. Hosted CI, full six-engine regression, native Windows 11 x64 build/smoke/accessibility and Defender/EDR remain **UNVERIFIED** until runner allocation succeeds.

## Release hard hold and next step

Do not publish or offer any of the six executables. The two Pro products require authenticated/gated delivery, and no compliance/payment approval is automated. Four free and two premium remain unreleased. Keep production branch, WordPress site and premium downloads unchanged; require independent QD, full native Windows validation and explicit founder release authorization.

**Highest-impact next step:** inspect the GitHub Actions failed-run banner plus billing/spend restrictions, runner provisioning and workflow policy; restore hosted Ubuntu/Windows execution and rerun this unchanged commit, followed by the entire inherited regression and Windows packaging/scanning/smoke/accessibility checks.
