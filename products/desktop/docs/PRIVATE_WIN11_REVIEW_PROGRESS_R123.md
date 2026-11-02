# Final Vestige Labs R123 — read-only private Windows 11 acceptance progress

**DRAFT / RELEASE HOLD · Issue #73 · strictly stacked on R122 draft PR #520, not production.**

## What R123 closes

R122 can record each of the **46 human-observed Windows 11 checks** privately, but the R109 verifier gives a global count, not a safe per-product remaining-work queue. R109 also validates every *referenced* witness, while an interrupted R122 record could leave an **unreferenced witness** that the global validator ignores. A reviewer could mistake a partially recovered review folder for clean evidence.

R123 adds `scripts/windows11_review_progress_r123.py`. Its **read-only** command requires the actual Windows 11 x64 workstation, the same independently authenticated raw-R9 SHA-256 pin, the real six-EXE R9 custody verification, a matching review build, the complete 46-slot schema and verified witness hashes. It refuses active/stale R122 cooperative locks, extra files, orphaned witness notes, substituted content and candidate-folder review storage. It revalidates the review matrix and all referenced witnesses after inventory inspection.

It returns only fixed product/check identifiers, per-app PASS/FAIL/NOT_RUN counts, each app's next NOT_RUN check, and `RELEASE_HOLD`. It never prints private reviewer notes, reviewer ID, evidence hashes, confidential paths or invoice/payment data, and never modifies a witness, EXE, matrix or source ledger.

## Physical operator usage

Follow the [R122 operator runbook](PRIVATE_WIN11_WITNESS_WRITER_R122.md) for trusted private receipt of exact R9-smoked Windows x64 candidates, independently authenticated digest, and human review template. The following are **example placeholders, not accessible download paths**:

```powershell
$pin = "<separately authenticated lowercase SHA256 of the exact raw R9 JSON bytes>"
python products/desktop/scripts/windows11_review_progress_r123.py `
  --dist "C:\PRIVATE\six-exes" `
  --r9-report "C:\PRIVATE\custody\offline-candidate-evidence.json" `
  --expected-r9-sha256 $pin `
  --review "C:\PRIVATE\review\matrix.json" `
  --witnesses "C:\PRIVATE\review\witnesses"
```

Expected initial counts are 0 PASS / 0 FAIL / 46 NOT_RUN; **this is not an acceptance result**. After each actual human Windows 11 observation recorded through R122, rerun R123 to find the next outstanding check. A failure, unexplained orphan, conflicting reviewer lock, or mismatched source fingerprint means **HOLD and human investigation**. Never remove an unknown witness or lock automatically. If all 46 checks have reviewer-declared PASS, R123 still reports `RELEASE_HOLD` and labels the manual matrix `MANUAL_MATRIX_COMPLETE_UNCERTIFIED`.

## Threat model and limitations

- Authenticated out-of-band custody of the expected R9 digest is required: a self-derived or unauthenticated hash proves only equality, **not provenance**.
- R123 is not a physical test runner; GitHub-hosted Windows builds do not replace an independent Windows 11 reviewer performing NVDA, keyboard, contrast, scaling, locked-surface and other real checks.
- A malicious privileged actor with writable evidence directory access may race local checks. The cooperative lock and twice-read checks reduce accidental races, **not** guarantee transaction isolation against hostile filesystem activity.
- The witness folder is intentionally strict: any extra file or directory causes a HOLD. A reviewer should use a dedicated empty folder rather than store screenshots, notes, tools or system-generated files alongside witnesses. Store observations separately and privately.
- No antivirus/EDR clearance, code signing, premium entitlement, compliance determination, release bit, download endpoint or approval occurs. QD exact-head review and founder authorization remain mandatory.

## Automated verification

`safe_unittest_r123.py` mandates **17 synthetic methods with zero skips** under normal and `-OO` interpreters on both Linux and Windows CI. They cover no-pass/one-pass/FAIL/all-46-claim status, deterministic per-app queues, orphan/extra-file rejection, tampering, locking, pin/Win11 preconditions, confidential output redaction and reviewer-path separation.

**All six applications UNRELEASED.** Next highest-impact step after exact-head CI verification: transfer and independently authenticate actual six private candidate executables and evidence for authorized physical Windows 11 review, then perform the 46 human checks and independent Defender/EDR + remediation-history assessment. QD/founder approval, signing and access-controlled premium distribution remain outstanding.
