# R375 — Premium issuer SQLite bootstrap handle custody

**Scope:** Operator-side local-first license issuance registry for GrantAudit Studio Pro and ProcureGuard Studio Pro. The other four free desktop utilities and customer-facing entitlement verification are unchanged. **DRAFT ONLY — NOT RELEASED / NOT QD OR FOUNDER APPROVED.**

## Defect and correction

In `license_registry.IssuanceRegistry._db`, SQLite `connect()` could succeed before a PRAGMA or table-creation operation raised `sqlite3.Error`. The prior handler raised a public `RegistryError` immediately, **without closing the connection**. It also used `from exc`, making the private database exception and local path available through `RegistryError.__cause__` and `__context__`.

R375 retains the exact busy timeout, DELETE journal, FULL synchronous mode and original protected issuance-table DDL. It now tracks whether setup completed, attempts one close of every connection whose setup did not complete, including non-SQLite `BaseException` interrupts, and emits the fixed public `RegistryError` **outside** the SQLite failure handler. A SQLite failure during cleanup cannot replace the sanitized setup error. Successful usage still closes the connection after the yielded transaction.

The registry's persistent ID reservations, exact schema/row guards, operator-only filesystem policies, collision refusal, signed license format, and human issuance/approval flow remain unchanged. No network or telemetry behavior is introduced. This is **not** database replay defense, a license-signing audit, or proof of cryptographic entitlement.

## Synthetic test evidence — November 12, 2026

- **12 new regression methods** in `products/desktop/tests/test_registry_bootstrap_r375.py`, covering all four SQL setup statements, connection failures, path-canary exception-chain isolation, cleanup-failure handling, KeyboardInterrupt/SystemExit, successful and failing context exits, precise PRAGMAs/DDL and real SQLite table and row persistence.
- Reconstructed pre-fix `_db` exhibited **9 failed methods of 12** under Linux Python 3.13.5 with the new tests, consistent with the pre-existing handle leak and private exception chaining.
- Reconstructed corrected `_db` on Linux Python 3.13.5: **12/12 PASS** with `-W error`, **12/12 PASS** with `-OO -W error`: **24 isolated passing method executions**.
- Local executions used a **reconstructed targeted method and stub module**, not an independently materialized full exact-head repository checkout; the committed complete-module test file has **not** been run locally. Claims are explicitly limited to this method-level reconstruction. All canaries and records were synthetic.
- Four explicit hosted CI commands added: Ubuntu and Windows, each regular and `-OO`, before packaging. The same source-controlled module must execute in the complete checkout to establish integration correctness.

## Release blockers and next action

At start of sprint, R374 exact-head [Actions run #43188201634](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43188201634) was `failure` with `steps=null` on both Ubuntu and Windows. Root cause of runner dispatch remains unconfirmed. Inspect failed-job check annotations, Actions billing/spending controls and hosted-runner eligibility. Do not count a pre-run failure as a test result.

Next: restore hosted runners and execute the entire six-app regression suite, including the **22 genuine AES-GCM cases**, then run actual Windows 11 x64 PyInstaller builds, executable smoke, Defender, accessibility and premium distribution/license entitlement checks. Hold merger, release and all premium download publication until **independent QD review and founder approval**.
