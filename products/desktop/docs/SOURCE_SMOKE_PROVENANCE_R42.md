# R42 — Six-engine source-smoke provenance, pre-release only

Scope: the four free desktop apps (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and two premium apps (GrantAudit Studio Pro, ProcureGuard Studio Pro). This change protects **source-only synthetic smoke evidence**. It does **not** validate a packaged Windows binary or approve downloads.

## Why this sprint

The R21 source smoke initially hashed each engine and launcher, then executed six synthetic smoke checks. Source files could be changed or replaced between the initial hash and the smoke run, leaving a successful report that attested to **different source bytes** than those being tested. The R21 report writer also used direct exclusive text-file writes; an interrupted write could leave a partial JSON file on disk.

## Implemented safeguards

1. Inventory the Python engine files and the exact six launchers with descriptor-based, chunked SHA-256 reads. Refuse symlinked source/package paths, hardlinks, non-regular sources, source files over **16 MiB**, and source inventories over **256 files**. Compare filesystem identity/size/timestamps before and after each read to detect observed in-flight edits or replacement.
2. Run all six established deterministic synthetic smoke routines with no customer inputs. Keep the report schema **fvs-source-smoke-v1**, with both `released` and `qd_approved` always `false`.
3. Recompute the **entire** source inventory *after* all six smokes. If any inventoried file is modified, removed, or added during the run, **do not create success evidence**. Changes after this final snapshot remain outside this safeguard and need separate custody controls.
4. For `--report`, reuse the previously committed R38 `report_evidence.prepare_report_path` and `publish_report` helpers. Destination must be a **new file outside the repository tree**. The JSON is staged in a private temporary file, flushed and published with no-clobber hardlink semantics. Filesystems without link support fail closed. Failed publication does not authorize success.
5. Maintain the R41 evidence-only GitHub Actions upload policy: no EXEs are uploaded. The source-only report stays inside runner temporary storage, not the distribution directory. The Linux and Windows workflows execute the new regression tests normally through test discovery and explicitly under `python -OO`.

## Verification commands and observed results

From a checkout containing this branch:

```bash
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p 'test_source_smoke_integrity_r42.py' -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p 'test_source_smoke_integrity_r42.py' -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -v
```

**Executed on Linux x86_64, Python 3.13.5, with a reconstructed source subset** containing the exact committed R38 `report_evidence.py`, exact committed R21 legacy test, and R42 source plus new regression tests. Results: **22/22 new tests and 8/8 legacy R21 tests pass**, both normally and with `-OO`; `compileall` passes. New tests include mid-smoke changes to engines and premium launchers, new/removed source files, unsafe symlink/hardlink alias, oversized files and module counts, in-read mutation, replaced file descriptor, no-clobber evidence, and strict six-app status flags. The source and regression Git blob hashes were compared against the actual commits. The results are **not** full-repository CI and do not demonstrate that the real `fvs_suite.smoke.run_smoke` passed on this branch.

Source evidence is intended to prove only a synthetic source run. SHA-256 checks of source bytes do not establish trustworthy build provenance against a privileged attacker controlling source and reports. R38 report publication is no-clobber but Windows filesystem ACLs must still be reviewed by operators.

## Mandatory remaining gates

GitHub Actions runs still fail before any recorded steps on both Ubuntu and Windows (last observed R41: [run #40926314601](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/40926314601)). Verify R42's own run independently. The user/repository owner must restore hosted runner provisioning/billing, or run the complete source suite and `products/desktop/scripts/verify-windows-candidate.ps1 -Build` on a trusted Windows 11 x64 workstation. Retain EXEs privately until real Windows smoke tests, AV/security inspection, inventory checksum validation, controlled premium licensing/download delivery, independent review, and **explicit QD approval**. No production branch or public download changes are part of R42.
