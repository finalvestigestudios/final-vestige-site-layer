# R497 — PE certificate record tail custody (INTERNAL / QD HARD HOLD)

Issue #73. Draft branch stacked on R496 PR #2866; **not** production `main`.
This change affects the shared executable-format preflight for LedgerDiff Lite,
Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro
and ProcureGuard Studio Pro. It does **not** build, sign, publish, or approve
any of those six Windows x64 applications.

## Defect and correction

In R496, `verify_certificate_table` checked the file-size *claim* and read
each eight-byte `WIN_CERTIFICATE` header, but never read its declared payload
or alignment tail. After a concurrent file truncation (or when a direct caller
supplied a stale file length), a header could survive while most of the claimed
certificate record was absent. The structural check would return successfully.

R497 uses the **same already-open stream** to seek to and read one byte from
the last claimed position of **each** aligned record. If a payload, final byte,
or alignment tail is unavailable or its probe triggers an I/O error, verification
fails closed with a fixed, private-path-free diagnostic. Header read I/O failures
are also translated *after* leaving the exception handler, removing a retained
private OSError `__context__`. The existing 8 MiB table and 128-record limits
still apply. No PKCS#7 payload is copied to memory or executed.

This is a *best-effort descriptor availability probe*, not an atomic snapshot:
it does not prevent an adversary from changing bytes between reads, does not
prove Authenticode contents or certificate validity, and cannot replace an
exact-descriptor SHA-256 digest, malware scan, trusted Windows x64 smoke test,
or independent release authorization.

## Regression evidence

New module: `products/desktop/tests/test_pe_certificate_tail_r497.py`.
Twelve tests cover complete/unsigned/multi-record cases, maximum count,
missing payload, missing alignment padding, a short tail read, a private
I/O failure and nonzero padding. On the **R496 parent module**, the tests
demonstrated **7 expected failures**; these now pass.

Local Linux Python verification on exact Git-blob-matched helper and test bytes:

```sh
cd products/desktop
python -B -W error -m unittest discover -s tests -p 'test_pe_certificate*.py'
python -OO -B -W error -m unittest discover -s tests -p 'test_pe_certificate*.py'
python -m py_compile pe_certificate_guard_r496.py tests/test_pe_certificate_tail_r497.py tests/test_pe_certificate_guard_r496.py
```

**34/34 pass in each mode (68 total executions), 0 skips; compilation passes**.
These 34 methods comprise R496's 22 inherited focused tests and R497's 12
new tests. They run on inert synthetic streams; the full six-app repository
suite, parser integration tests and actual Windows executables have **not**
been run locally. Git-blob SHA identifiers:

- Modified helper: `23e0e00b90f0b984e22a3f0d103b74a86ce4a4ad`
- New tests: `1497f041e48302b15685db70c1682caa256be8f5`
- Existing inherited tests: `006fd6a852ad4a0ae14bef9ab65167bab788b8ae`

Independent source-evidence CI requests R497 in normal and optimized mode
on Ubuntu and Windows. The internal build source-testing workflow now
explicitly requests inherited R496 focused/integration suites and R497.
They must actually run before this PR can advance.

## Release hold and next action

Previous R496 source and internal build workflows failed before job steps
(`steps=null`, no runner assigned). The exact cause remains unconfirmed.
Authorized repository administration should restore Actions runner
eligibility or execute these regressions in a trusted full Windows x64
checkout, then run the entire six-app regression/build/packaging matrix,
Defender, SHA-256 verification, smoke tests, accessibility, and protected
premium distribution checks. **No executable or premium URL may be exposed.**
Independent QD review and explicit founder approval are required for any
merge or publication. Decimal-safe money logic, local-first privacy,
deterministic financial audit trails, and human compliance review are untouched.
