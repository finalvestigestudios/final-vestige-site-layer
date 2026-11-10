# R337 — byte-exact, private six-app release-gate JSON evidence (2026-11-10)

**Draft engineering change only.** Applies to release verification reports for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. Stacked exclusively on [R336 draft PR #1938](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1938), exact base `222e2ddfc2cb0d8690100a5d26253e35997296fc`, **not** production `main`. Independent QD approval and founder authorization are hard holds.

## Reproduced acceptance gap

`products/desktop/report_evidence.py::publish_report` previously ignored the return count of `stream.write(payload)` and linked the staging inode to the requested report path without checking its contents. A short write, a wrapper dishonestly returning a full count after writing fewer bytes, or same-length substituted bytes could thus produce an apparently successful `verification.json` even though the exact deterministic evidence was not stored. If `os.fdopen` failed before assuming ownership, the raw `mkstemp` descriptor could leak.

Against a locally reconstructed **R336 predecessor implementation**, the new 18-case suite produced **9 assertion failures and 2 errors**; these cases are intentional red tests, not evidence of a live customer incident.

## Implemented

- `report_evidence._write_verified_stage` now owns or explicitly closes every staging descriptor, including `fdopen` exceptions and `KeyboardInterrupt`, and closes streams when context entry fails.
- Stage writer must report an **exact built-in integer** equal to the encoded report length. No boolean, subclass, text, or partial count is trusted.
- After `flush` + `fsync`, the same staging descriptor is rewound and re-read through EOF; bytes must equal the intended canonical UTF-8 JSON + LF **exactly** before the exclusive `os.link` publication. Short and same-length corrupted results fail closed; private exception causes are suppressed.
- Preserve existing exclusive, no-overwrite publication, deterministic serialization, POSIX private temporary-file permissions, unchanged report schema, and unchanged `release_authorized=False` / premium verification holds.
- Add 18 regression cases and explicit normal/`-OO` Ubuntu plus Windows workflow steps in `.github/workflows/desktop-build.yml`. No site, download, payment, accounting calculation, or premium release changes.

## Local evidence

Environment: Linux, Python 3.13.5, synthetic evidence dictionaries, genuine temporary filesystem and hardlink operations, no Windows executables or customer data.

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_report_evidence_exact_stage_r337.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_report_evidence_exact_stage_r337.py'
python -m py_compile products/desktop/report_evidence.py products/desktop/tests/test_report_evidence_exact_stage_r337.py
```

**18/18 PASS standard + 18/18 PASS `-OO` = 36/36 test executions, zero skips, compile PASS.** Source blob is `5b68694c5c40daa1ee7070f060b6f540c40b7533`; test blob is `2ef47d6d6748ce8306c1fb2fb5c4b3e5366091a3`, both verified against locally tested bytes. This is **focused isolated-module testing only**; legacy R38 report cases, the complete private repository suite, all 22 genuine AES-GCM cases, hosted workflows and native Windows 11 x64 acceptance were **not executed locally**.

## Security / release limitations

This enforces byte-exact evidence **before** linking. It does not prevent all adversarial concurrent same-user filesystem mutations between readback and link, and it does not independently authenticate an unpinned report. The legacy stage pathname cleanup remains unchanged and must be separately reviewed for a check-to-unlink race. No tested/signed/malware-scanned private Windows binaries, access-controlled premium distribution, or live download links exist from this sprint. Report success is not compliance approval.

At sprint start, [R336 Actions run #42881360721](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42881360721) was **failure**, with Ubuntu and Windows jobs showing `steps=null`; infrastructure cause unconfirmed. A new draft PR may trigger the same pre-step failure, not a source-test result.

**Next most valuable step:** owner restores GitHub Actions runner eligibility/billing/permissions to obtain real executed logs; then run full normal/optimized desktop discovery (including 22 genuine AES-GCM cases and legacy report suites), Windows 11 x64 native all-six acceptance, SHA/Defender/accessibility/premium access-control checks, independent QD review, and founder release approval. Do not merge or publish on this evidence alone.
