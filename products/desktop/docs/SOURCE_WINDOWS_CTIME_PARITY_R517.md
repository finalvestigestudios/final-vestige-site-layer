# Final Vestige Labs R517 — Windows source-descriptor creation-time parity (DRAFT / QD HARD HOLD)

**Scope:** [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73), the source-evidence runner for all six separate Windows x64 utilities. This is a source verification reliability fix, not Windows binary validation, licensing, financial engine work, a release, or compliance approval.

## Confirmed defect in parent R516

The R516 source fingerprint helper compared **all seven** `Path.lstat()` and `os.fstat()` fields when opening an unchanged source. On Windows CPython, the *creation-time* `st_ctime_ns` returned by pathname and descriptor APIs may disagree for the same file. This behavior was **already observed/documented in this repository** by `products/desktop/scripts/source_smoke_gate.py` (R101). The R516 helper therefore risks spuriously rejecting legitimate source files under native Windows even when the source has not changed. The independent Windows Actions jobs have not run; this is a code-deduced platform regression, **not** a claimed completed native Windows reproduction.

## Implementation and regressions

- `products/desktop/scripts/source_path_snapshot_r515.py`: add `_same_path_descriptor_identity`; compare dev/inode/mode/hardlink count/size/mtime for *Windows cross-view* comparisons; keep the full seven-field identity on non-Windows.
- On **every platform**, compare the full seven-field *pathname receipt to pathname receipt* and *descriptor receipt to descriptor receipt* before/after reading. This keeps Windows same-view ctime mutation a hard failure. Preserve <=1 MiB source limit, link/junction/hardlink rejection, SHA-256 source verification, private-path-free errors and no shell.
- `products/desktop/tests/test_source_evidence_runner_r509.py`: six focused regression methods inserted into the existing immutable 416-command inventory: simulated Windows path/fd ctime divergence, Posix strictness, structural mismatches, a real source read and repeated receipt, same-descriptor ctime mutation, and source content mutation.
- Existing manifest SHA `a55a9b5bcbee5b9f075a39fc581ed5a4716eaca3`, source workflow SHA `7fa8e7633f1357f31ba668bc16f11be79fea5ae4`, and CI commands remain unchanged.

## Locally executed evidence — limitations explicit

A Linux Python focused harness against the same updated helper logic ran **6/6 passing standard** (`python -B -W error`) plus **6/6 passing optimized** (`python -OO -B -W error`) = **12/12 synthetic method executions**, with Python compilation passing. A negative control forcing the exact R516 full-field cross-view comparison rejected an unchanged synthetic file with divergent pathname/fd ctime. The tests simulate the known Windows discrepancy; **not** a native Windows 11 run. The entire committed test module, 416-command Linux/Windows matrix, six native EXEs, Defender, SHA-256 binary receipts, keyboard/scale accessibility and premium entitlement/download validation **have not run**.

## Next acceptance gates and minimum unblock

The exact R516 head's three GitHub Actions workflows failed before executing any steps, with six jobs showing no assigned runner and `steps=null`: [Windows internal build #44255331013](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44255331013), [source matrix #44255331057](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44255331057), [identity #44255330986](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44255330986). **Cause remains unconfirmed.** Repository admin: verify GitHub Actions billing/spend limits, repository workflow policy and eligible GitHub-hosted Windows/Linux runners. Then rerun all required workflows at this R517 SHA, verify the R517 committed regression on real Windows, and complete native six-executable release and protected premium distribution checks.

**QD HARD HOLD:** no merge to `main`, publication, executable downloads, unrestricted premium artifacts or automated financial/compliance decisions. Local-first privacy, Decimal-safe money, deterministic audit evidence and mandatory human review are unchanged. Independent QD review and founder authorization remain required.
