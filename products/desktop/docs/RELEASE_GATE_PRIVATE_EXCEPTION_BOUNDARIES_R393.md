# R393 — Six-app release gate retained exception privacy (DRAFT / HARD HOLD)

Scope: `products/desktop/release_gate.py` only; all six Windows x64 release candidates share this gate. This change is **not** a release, binary smoke, entitlement, code-signing verification, malware clearance, payment approval, or QD authorization.

## Reproduced defect and repair

Prior `_pe64` used `raise GateFailure(f"{path.name}: {exc}") from exc`. It retained an underlying `PEFormatError` via `__cause__` and repeated its string in the public error. Other guards used `raise ... from None` *inside* `except`, which masks rendered traceback but retains private `__context__`. A synthetic private-marker reproduction demonstrates these Python exception semantics; no customer material was used.

R393 now classifies the error inside the handler and raises a new, fixed, path-free `GateFailure` **after leaving the handler**. It covers:
- canonical SHA256 inventory read/parser;
- PE32+ image inspector;
- file/checksum custody hashing;
- native-versus-synthetic smoke provenance;
- preflight and repeated staging membership checks;
- smoke process failures.

The change deliberately uses generic failure text. Detailed lower-level exceptions must not become a public API or audit-log payload. It does not swallow `KeyboardInterrupt`/`SystemExit`; it does not treat failed gates as successes. Six expected binary names, SHA-256 inventory comparison, PE sanity checks, fail-before-run rule, pre/post smoke checks and false release/entitlement/signing/malware flags remain unchanged.

## Tests and evidence

`products/desktop/tests/test_release_gate_privacy_r393.py` contains **13** synthetic regressions: five translated failure sites plus alternate inventory and checksum paths, a second-directory check, smoke runner failure, marker confidentiality, no cause/context, valid pass-through, and no execution after preflight rejection. The independent source evidence CI workflow invokes all 13 in normal and `-OO` mode on both Ubuntu and Windows.

Local testing **before repository commit**: Linux Python 3.13.5, **13/13 normal + 13/13 optimized = 26/26 passed**, against a **locally reconstructed/stubbed release-gate boundary**, not the exact committed repository checkout. Treat this as focused logic evidence only. Full exact-commit tests, inherited regression compatibility, native Windows and real EXE functionality are **NOT VERIFIED**. No runner output is represented as a local pass.

## QD / founder hold

- Work only on isolated R393 branch stacked on R392 draft; production `main` untouched.
- Keep local-first financial data and protected premium distribution, Decimal/provenance integrity, human approvals, and a zero-telemetry default.
- Run full source tests and real cryptographic suites on the exact commit after hosted CI can allocate a runner.
- Independently perform Windows x64 build, realistic executable smoke, Defender/EDR, keyboard/screen-reader acceptance, installer/package checksums, and gated premium delivery verification.
- Independent QD review **and explicit founder authorization** are required before any merge/release/catalog download link.

## Known CI blocker and next step

At prior R392 HEAD `0d7b0624deea6f67da24986ee74134e363c35436`, source Actions run `43357395171` and desktop Actions run `43357395099` both failed almost immediately. All four jobs had `runner_id=0`, empty `runner_name` and `steps=[]`. The exact failure annotation was not accessible through the connector; do **not** infer a proven billing cause. Owner: inspect failed check annotations, Actions billing/spending limits, repository Actions permissions and hosted runner eligibility; rerun exact R393 SHA only after fixing allocation.

Next engineering step: full six-app engine and money/provenance regression, real AES-GCM + Ed25519/SQLite tests on Ubuntu/Windows, then Windows x64 candidate binaries and protected distribution acceptance.
