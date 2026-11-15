# R439 — private SQLite error-chain custody (DRAFT / HARD RELEASE HOLD)

Tracking: [Final Vestige Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
Parent: [R438 draft PR #2549](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2549), pinned to `b186c5dfd92d8afaa5ceef2c0b5022d203a22b7a`. This is a feature-branch-only change; no production `main` mutation.

## Reproduced defect

The operator's offline premium SQLite custody had three nested exception-translation boundaries that appeared sanitized in `str(error)` but still retained potentially private SQL diagnostic text, customer identifiers, or local file locations in `error.__cause__` / `error.__context__`:

- `registry_schema_guard.enforce_registry_schema` chained `sqlite3.Error` into `RegistrySchemaError`.
- `registry_row_guard.enforce_registry_rows` chained `sqlite3.Error` into `RegistryRowError`.
- `license_registry.IssuanceRegistry.reserve` and `.finalize` chained either inner guard exception into a public `RegistryError`.

These chained objects are observable to code calling the APIs even if a CLI prints only a generic error. Suppressing traceback display with `raise ... from None` would not remove `__context__`.

## Implemented behavior

All three boundaries record a bounded boolean failure result *inside* their relevant handler, then raise the unchanged sanitized exception text *after* the handler exits. This removes the originating private exception object from the outward chain without masking invalid database structure or permitting partial writes. `BEGIN IMMEDIATE` and the existing rollback path remain in place. Schema checks, row validation, exact premium products, SHA-256 evidence, protected filesystem reads, SQLite record semantics and deterministic/Decimal financial engines are unchanged.

This protects the operator-side license registry for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**, not their client executable or payment flow. No real customer data or signing key is used in validation.

## Local test evidence — Linux Python 3.13.5

The three modified full production modules and three unmodified dependencies were reconstructed from GitHub and checked against exact original Git blob SHA-1 IDs before modification:

- `license_registry.py` original `72090738c49f45c56acc0621f2d23853f953b574`, fixed `f32ae1cfd4a9f62e71a2eaf4ce7dcb0b089d1455`
- `registry_schema_guard.py` original `ce02616ce6745c01a3d1891ec4fb4aa93280404a`, fixed `0025aeda8a2a5a841cf21d35abe9476ec30600dd`
- `registry_row_guard.py` original `dfac668a56733b0f488a938dd069423b07f05102`, fixed `dd024a1144eb284a55be5f2011a5b1ef1d8db58b`
- unchanged `registry_write_guard.py`, `registry_file_guard.py`, `issued_entitlement_guard.py` each also Git-blob-matched
- New `test_registry_private_guard_chains_r439.py`: Git blob `845d6b54faaf9e2e525508959fb500805ea499b1`; 8 real-SQLite regression methods.

Executed `PYTHONPATH=. python -W error -m unittest discover -s tests -p test_registry_private_guard_chains_r439.py`: **8/8 PASS**.
Executed the same command with `python -OO -W error`: **8/8 PASS**.
`python -m compileall -q .`: **PASS**.
Controlled original-source negative test with three original Git-blob-matched modules: **8/8 methods failed as expected**, verifying that tests distinguish the real defect. Cases include private SQLite error-chain canaries, nested causes, reserve rollback, finalize retention of reserved state, successful synthetic state transitions, and rejection of schema drift or malformed rows.

This was a **focused reconstructed module set** with real SQLite and exact production file contents, not a full Git checkout; prior inherited R13/R14/R15 suites were not locally executed. No native Windows binary was built or smoke-tested.

## CI and release controls

The source-evidence workflow invokes the new R439 suite plus inherited R13/R14/R15 on **Ubuntu 24.04 and Windows latest**, normal and `-OO`. Inspect actual runner/job steps before interpreting any result. The latest preceding R438 Actions runs [source #43661307120](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43661307120) and [Windows build #43661307132](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43661307132) both failed in approximately three seconds with **zero recorded steps and no runner assigned**; no CI success can be inferred. Root infrastructure cause remains unconfirmed.

**Next highest-impact step:** Repo owner checks Actions policy, billing/spending limits and hosted-runner eligibility; reruns exact R439 head, then runs six-engine regressions and genuine Windows x64 packaging/Defender/accessibility checks. Premium downloadable files must remain authenticated and gated. `release_authorized=false`. Independent QD review and explicit founder approval are mandatory before any merge, distribution, WordPress publication, or compliance approval. No executables or real licenses were issued in this sprint.
