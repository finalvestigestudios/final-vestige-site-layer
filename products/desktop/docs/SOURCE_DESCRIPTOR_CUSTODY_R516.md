# Final Vestige Labs R516 — descriptor-stable source receipts (DRAFT / QD HARD HOLD)

**Scope:** issue #73, all six Windows x64 utilities (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro). This is a targeted integrity correction to the existing read-only 416-command source-evidence runner; it **does not** build, approve or distribute executables.

## Reproduced R515 defects

R515 checked descendants for symlinks and read source bytes, but it did not reject a symlinked *checkout root* or hard-linked source files. Those two file layouts were **accepted** by the exact previous helper (Git blob SHA `d448a71175d7eef34f26ba3170397176fb2c9523`) during a local negative-control run. It also did not bind source bytes to the opened file descriptor and stable before/after metadata, leaving ordinary file-replacement and mid-read modifications less constrained.

## R516 change

- Reject relative roots, linked/junction checkout roots and linked ancestors; keep the R515 segment and descendant-link checks.
- Reject nonregular source files, hard-linked sources, and source sizes above 1 MiB before digesting.
- Use bounded descriptor reads, `O_NOFOLLOW` / `O_NONBLOCK` where available, and compare `lstat` / `fstat` metadata before open, after open, after read and at the final path. Preserve no-source-bytes/no-path error messages.
- Keep the public `source_fingerprint` and `matches_source_fingerprint` APIs intact. No changes to command manifest, CI action pins, production runtime or application logic.
- Add 12 regression methods to the **existing** matrix-listed test file, so both normal and `-OO` invocations already cover them without changing the 416-command inventory.

This is **defense in depth**, not a TOCTOU-free, atomic filesystem sandbox. The parent directory tree may still change between inspections. On platforms without `O_NOFOLLOW`, leaf races rely on descriptor/path identity checks. Metadata-only time-of-check mutation is not sufficient to establish a cryptographic writer identity. The source runner and its tests remain read-only.

## Exact source, local evidence and limitations

- Parent commit: [R515 `1f806d8348ceceb512be1d6185d423c68b3fe476`](https://github.com/finalvestigestudios/final-vestige-site-layer/commit/1f806d8348ceceb512be1d6185d423c68b3fe476).
- Tested **byte-identical** Linux CPython 3.13.5 helper Git blob: `61c291c3747e086c8bee0392427776c5205bd4ca`; 3,725 bytes, SHA-256 `5617a0ef7faabded2fe5040f3b3f2b1974ad86e283ab017a1dc31242c981e007`. Verified GitHub file readback after commit.
- Local synthetic regression **12/12 PASS** with `python -B -W error -m unittest -q test_r516`; **12/12 PASS** with `python -OO -B -W error -m unittest -q test_r516`; **24/24 focused test executions**, no skips; helper and test Python compilation passed.
- Exact parent-helper negative control: **two unsafe layouts reproduced** (hard-linked leaf and symlinked checkout root accepted), both rejected by R516.
- The locally executed regression module contains the **same 12 scenarios** as the 12 newly committed methods, but the **complete committed module and full 416-command checkout matrix have NOT run** on a native full checkout. Local tests were on Linux, not Windows. Source integrity is not a release or entitlement test.

## CI, QD and release conditions

The previous R515 head's three workflows failed before any job steps: source [#44249404288](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44249404288), internal Windows [#44249404270](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44249404270), six-image identity [#44249404320](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44249404320). Their GitHub job APIs returned `steps=null`; the underlying infrastructure root cause is **not established**. Inspect new exact-R516-head Actions after opening the draft PR.

**Smallest unblock:** repository/account administrator checks Actions billing/spending caps, GitHub-hosted runner eligibility and repository workflow policy, and reruns the exact R516 SHA. Then execute all 416 source commands on Ubuntu/Windows, native six-program Windows x64 packaging and smoke, Defender, executable SHA-256, offline/privacy and keyboard accessibility checks, and protected premium entitlement/download verification.

**HARD HOLD:** no merge into production, site edits, untested EXEs, unrestricted premium downloads or automated compliance approvals. The four free/two premium split, Decimal-safe money logic, deterministic audit trails, local-first privacy and human review are unchanged. Independent QD review and explicit founder approval remain mandatory.
