# Labs R323 — canonical JSONL evidence framing and audit numeric/text guard

**DRAFT; independent QD + founder HARD HOLD.** Issue #73. Stack on R322 draft PR #1852 only, not `main`. This changes only an **offline, read-only** restored-evidence inspector, 30 synthetic regression methods, this note and internal source/Windows CI. No app engine, Decimal money calculation, licensing, financial records, website, publication or entitlement edits.

## Defect and corrective behavior

The R321–R322 premium plaintext inspector used `bytes.splitlines()` to count audit records. That routine recognizes bare carriage return (`CR`) as a row separator even though the premium journal format uses a final line-feed terminator. For example, `{}\r{}\n` could be counted as two JSONL records, despite being only one LF-terminated record. Its JSON parser also accepted floating-point JSON numbers (`1.5` and `1e309`) and decoded escaped lone Unicode surrogates. These are **not** emitted by the supported premium review-event writer: its numeric values are integers and its text must encode as valid UTF-8.

R323 instead counts records by the actual `LF` bytes, strips at most one terminal `CR` from each record to preserve legacy `CRLF` compatibility, and refuses all other bare `CR` placements. It rejects float/exponent syntax at parse time (without ever converting money to a floating point value), rejects lone escaped surrogates by requiring UTF-8-serializable decoded text, and continues to reject malformed JSON, duplicate keys, `NaN`, `Infinity`, NUL, invalid UTF-8, bad count, unfinished final record and oversized journals.

A valid empty journal with a zero declared event count remains accepted. Valid LF, CRLF, mixed LF/CRLF and ordinary multilingual Unicode are accepted. Existing receipts remain explicitly non-authenticated/noncompliance/nonrelease, even after an independent R322 SHA witness match. No journal event-chain verification is added by this sprint.

## Local reproduction (2026-11-09 PST)

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored_journal_canonical_r323.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_restored_journal_canonical_r323.py'
python -m py_compile products/desktop/scripts/verify_restored_bundle_r320.py products/desktop/tests/test_restored_journal_canonical_r323.py
```

**Actually executed locally:** 30/30 methods passed normal and 30/30 passed `-OO` (**60/60 focused method executions**), `py_compile` passed, on a Linux Python isolated reconstruction of the exact updated journal-check function and the **exact committed test file**. Matching function verification: 1,936 characters, FNV-1a 32-bit `2ac2931b` on the function from the committed GitHub file and from the tested local reconstruction. Test file Git blob SHA `743d39cd639f7d0e8cfe2342b709f10d370ac9cd`, matching GitHub. The same test suite on a reconstructed pre-R323 journal-check function had **8 failing test methods** (expected red regressions). These are real executed unit tests on the isolated function, **NOT** evidence that the complete private checkout, Windows, original vault integration or six executables ran successfully.

The internal `.github/workflows/desktop-build.yml` now runs R323 tests under normal and optimized Python for Ubuntu source testing and before Windows packaging. As of the sprint start, R322's [desktop CI run #42766475802](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42766475802) failed with both jobs recording **zero execution steps and no runner name**. Hosted tests have not yet run; infrastructure cause is unknown.

## Security boundary, approval and highest-impact next step

Do not interpret a passing read-only plaintext consistency check or arbitrary operator-supplied witness as proof of source authenticity, human reviewer identity, correct event-chain semantics, payment approval, grant compliance, entitlement, or release authorization. A trusted source archive's genuine AES-GCM authenticated restore, **22 zero-skip genuine integration tests**, QD, founder review and Windows 11 x64 acceptance are still required. Keep original reports, passphrases and private evidence local; never include them in logs or public CI artifacts.

**Owner unblock:** restore eligible GitHub Actions runners (check Actions billing/spending and repository workflow/runner eligibility) OR execute the desktop test commands and `vault_crypto_gate_r316.py` from a full private checkout with the required `cryptography` dependency on a trusted Windows 11 x64 machine. Preserve the six-executable private artifact/Defender/accessibility/SHA-256 acceptance and premium access-control HARD HOLD until verified; publish nothing from this PR.
