# Final Vestige Labs R252 — Premium launch proof custody

**2026-11-07 UTC · DRAFT / independent QD + founder HARD HOLD.** This change is stacked on R251 at `18e2193708adfd835611696824966b6663ec2828`, not production `main`. No executables, license issuers, paid downloads, customer evidence or WordPress pages are published.

## Defect and risk

In the two premium desktop launch routes, `_select_premium_entitlement` and `_require_current_premium_entitlement` previously treated **any non-raising call** to `verify_license` as successful verification, even if a dependency accidentally returned `None`, `True`, or a license object belonging to another product. Unexpected ordinary verifier errors could escape into the Tk callback error handler with private file paths. The review workbench had its own authorization checks; this sprint fixes the **launcher / Generate gate**, which occurs before running either premium engine.

## Changes

- `fvs_suite/premium_launch_proof.py`: `has_verified_premium_proof` requires a native `grants` or `procurement` identifier and an object whose **exact type** is the verifier's `Entitlement` class and whose `product` matches the requested premium application. The existing offline Ed25519 `verify_license` remains the cryptographic authority; this is a result-shape check, **not** a replacement for signature verification.
- `fvs_suite/app.py`: applies the check to installed-license launch, manually selected-license launch and the revalidation immediately before premium Generate / Review actions. A malformed/falsey/truthy-sentinel verification result is denied. Unexpected ordinary errors are caught without interpolating exception strings, filenames, paths, or entitlements into dialogs; no premium engine executes on failed proof. The existing locked-without-trusted-production-public-keys behavior is unchanged.
- `tests/test_premium_launch_proof_r252.py`: 20 synthetic methods (8 pure-proof plus 12 AST-extracted GUI authorization path tests). No real license keys or sensitive financial data. Verify wrong product, `None`, `True`, subclasses, unexpected private-path errors, installed vs chosen file, cancel, and no-key fail-closed behavior.

## Local test evidence and limits

Linux Python local isolated reproduction: `PYTHONPATH=/tmp/fvs_r252 python -W error -m unittest discover -s /tmp/fvs_r252/tests -p 'test_premium_launch_proof_r252.py'` → **20/20 PASS**, and optimized `python -OO -W error -m unittest discover ...` → **20/20 PASS**. **40/40 isolated test-method executions, zero failures/skips.** `python -m compileall -q` passed. Exact committed Git blob SHAs match executed helper `fe17ec29dc2120b143407ce9cfb45750daace5c7` and test source `d951d51c49e96ad4784dabbdcf8412e90e4c3d77`.

**Scope limitation:** local `app.py` consisted of the source-owned two authorization functions reconstructed into a small package, not the complete exact repository GUI. The committed tests read and AST-compile those two functions directly from real `app.py` when repository tests execute. No complete repository matrix, Tk window, native Windows GUI, CI runner, licensed production key, or Windows x64 executable was tested. The new guard checks only a verifier return value; it cannot prevent local binary tampering or license sharing.

## Independent QD required before release

1. Restore GitHub Actions hosted job execution: R251 run [#42349625047](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42349625047) reports `windows-build` and `source-tests` **failed with zero returned steps**. Root cause not established: owner must inspect Actions billing/spend restrictions, workflow permissions and runner availability. Rerun the unchanged R252 commit when unblocked.
2. Execute **committed** `test_premium_launch_proof_r252.py` normally and under `-OO -W error` on both Ubuntu and Windows, plus the complete six-engine source gate. Verify no inherited test behavior changed.
3. On native Windows 11 x64, inject a synthetic verifier returning `None`/`True`/wrong-product proof and raising private-path `RuntimeError`. Neither GrantAudit Studio Pro nor ProcureGuard Studio Pro may open a licensed data workflow or Generate. With a test-only valid Ed25519 entitlement, confirm the exact product opens and revalidation occurs before actions. Do not distribute a test private key.
4. Verify all six privately packaged Windows executables with SHA-256, independent malware scan, keyboard/high-DPI/NVDA inspection, and manual audit/Decimal provenance review. Keep premium EXEs inaccessible to unauthorized visitors.
5. Require separate independent QD and founder approval before any production merge, sale, or public download.

**Next highest-impact step:** Unblock hosted source-tests and native Windows builds, run full two-mode suites, then obtain real six-binary private QD evidence. All six applications remain UNRELEASED.
