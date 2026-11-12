# R376 — premium SQLite write-transaction custody (draft / release HOLD)

## Scope and reason
Applies to the operator-controlled offline license issuance registry used for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. It does not change the four free tools, customer data handling, license signing, public download pages, or product entitlements.

Before R376, both `IssuanceRegistry.reserve` and `finalize` attempted an unguarded `ROLLBACK` for every SQLite exception. If `BEGIN IMMEDIATE` itself failed, or a damaged/closed connection rejected rollback, that secondary SQLite error could mask the intended fail-closed `RegistryError` and disclose operator-private database details. Raising inside the original `sqlite3.Error` handler also retained the private exception in `__context__` even when the displayed error was generic.

## Change
- Centralize the **BEGIN IMMEDIATE → one guarded action → COMMIT** sequence in `registry_write_guard.run_protected_write`.
- Roll back only after a successful begin, and attempt rollback on *any* post-begin exception, including schema/row guard rejection, domain rejection, process interrupt, and commit fault.
- Suppress only `sqlite3.Error` from best-effort rollback. Propagate domain errors, `KeyboardInterrupt` and `SystemExit`; never attempt an automatic issuance retry.
- Convert SQLite integrity/write faults into the existing caller-specific public `RegistryError` messages **after** leaving the private exception handler, leaving `__context__` and `__cause__` empty for translated faults.
- Preserve the exact schema/row checks, output fingerprint, SQLite journal and synchronous policy, unique license IDs, immutable reservation policy and manual compliance/issuance decisions.
- A failed `COMMIT` can leave durability uncertain. Operator must inspect registry state manually before any further issuance.

## Local executable evidence (2026-11-12, Python 3.13.5 Linux)
- `python -W error -m unittest -q test_registry_write_guard_r376.py`: **14/14 PASS**.
- `python -OO -W error -m unittest -q test_registry_write_guard_r376.py`: **14/14 PASS**.
- `python -m compileall -q` of the local helper/test pair: **PASS**.
- 28 focused method executions exercised synthetic begin/action/commit/rollback faults with private canaries, interrupt passthrough, deterministic rollback, and real in-memory/on-disk SQLite inserts/constraints.
- Local Git blob hashes of the exact tested helper and test sources can be compared with the committed `registry_write_guard.py` and `test_registry_write_guard_r376.py` blobs. This is **not** a complete exact-head checkout or execution of the modified `license_registry.py` inside the full repository.
- CI workflow adds four invocations, standard/optimized Python on each Ubuntu and Windows, before packaging.

## Release acceptance and blockers
- GitHub Actions runners recently failed *before any job steps*, on the R375 parent run #43196952109. New CI outcome must be inspected separately; do not infer a pass from source-only local tests.
- Pending: full repository six-app regression, 22 genuine AES-GCM premium cases, native Windows 11 x64 packaging/smoke, Defender, accessibility, premium entitlement checks, QD review, founder approval.
- **DO NOT MERGE, PUBLISH EXECUTABLES OR PUBLIC PREMIUM DOWNLOAD LINKS.** This change is a draft stacked on R375 and not on `main`.

## Next highest-impact step
Get the blocked GitHub Actions runners executing (check failed-check annotations, billing/spending caps and runner eligibility). Rerun R376's combined Linux/Windows gates, then complete native build and distribution acceptance without changing the site's QD/founder approval workflow.
