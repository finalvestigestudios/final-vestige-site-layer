# R339 — do not unlink six-app release-report staging paths automatically

**2026-11-10 · DRAFT / independent QD + founder HARD HOLD.** Applies only to private JSON verification evidence for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro. Based strictly on R338 draft PR #1949 at `31ad3b7fd35051115de9f33d5ddc73eb5e1ed14b`, **not** on production `main`.

## Defect and boundary

The R338 publisher checked and then removed the temporary report pathname in a `finally` block, including after success, after incomplete staging, and after an `os.link` exception. An interfering same-user local process can replace that pathname before `Path.unlink`, causing deletion of a different file. If a link wrapper creates the destination and then raises, the former cleanup also destroyed the stage that could help a human investigate the unverified destination. An R338 link witness already preserves a stage on *witness mismatch*; R339 makes retention consistent across **all** code paths and removes the unsafe auto-unlink operation entirely.

## Change

`products/desktop/report_evidence.py` never deletes a staging pathname: not after success, pre-link failures, ambiguous link failures, or failed R338 post-link witness. Each successfully created stage is retained under the randomized `.fvs-candidate-report-*.tmp` name in the **same private report directory**. On an ordinary success the stage and final JSON are two hardlinks to the same 0600-created inode on POSIX; do not automatically distribute either. In unsuccessful cases an incomplete or disputed stage may remain and **is not an approval token**.

Existing exclusive no-overwrite hardlink publication, exact JSON serialization, fsync, staged byte readback, R338 final-byte/inode witness, descriptor custody, redacted errors, offline operation and QD holds remain. Financial Decimal rules, local files, compliance human-review requirements and premium entitlement are unchanged. The old R38/R337/R338 tests that demanded deletion now assert explicit retention, except invalid JSON which never creates a stage.

**Operational consequence:** retained hidden stage names accumulate in the private report directory. They contain release-verification metadata and must be kept out of customer distribution packages, public web roots, and unrestricted premium downloads. A human may remove them **only after** investigating failures, verifying the intended report, and ensuring no evidence-retention obligation applies; no automatic cleanup script or unsafe check-then-unlink path is introduced. Windows ACL and filesystem behavior still require native acceptance.

## Local evidence

Reconstructed R338 `report_evidence.py` and `report_link_witness_r338.py` from exact Git blobs `09babcfa5acc40b86f98eec3a191adca34244d2b` and `12054deb1fa231ccd2911d1d3bfe6b5d720d4757`. Edited module matched Git blob `4a0608e10b108c15c34854206c55b7502369ffea`; the 18-test module matched Git blob `224e7c5d036d9b407035d44a4e6a47e08e953b35`.

On Linux CPython 3.13.5, real tempfile/hardlink/descriptor operations, synthetic evidence only:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_report_stage_retention_r339.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_report_stage_retention_r339.py'
```

**18/18 PASS** standard + **18/18 PASS** optimized = **36/36 focused executions, zero skips**; Python compilation PASS. Cases include ordinary publication, hardlink custody, private mode, repeated deterministic bytes, existing destination no-overwrite, JSON rejection, fsync/fdopen faults, ambiguous link that creates a target then throws, forged copy or no-op link, concurrent stage pathname swap and stage preservation. Exact R338 predecessor code reproduced **11 failures and 4 errors** against the new suite (failure counts are tests, not incidents).

## Hosted gate and release hold

Ubuntu and Windows jobs now include R339 normal and optimized regressions **before any Windows packaging**, but are **not claimed green**. The most recent inspected pre-R339 [desktop workflow run #42901123889](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42901123889) completed FAILURE with both `source-tests` and `windows-build` showing no execution steps/log URLs. Infrastructure cause unconfirmed: check Actions spending/billing, workflow eligibility and runner allocation. Full private-source regression (especially 22 genuine AES-GCM cases), corrected R38/R337/R338 suites, NTFS stage ACLs, Windows 11 x64 real EXE builds/smokes, Defender, SHA256, accessibility and protected premium delivery are **unverified**.

**Next highest-impact step:** restore Actions so the complete normal/-OO suite runs on genuine Ubuntu and Windows runners, verify the 22 AES-GCM cases and reconciled report suites, then carry out native six-EXE verification. Keep the PR draft and unmerged; independent QD review and founder authorization are mandatory. No binaries, downloads, WordPress, paywall or production branch changes.
