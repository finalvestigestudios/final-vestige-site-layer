# Labs R520 — manifest descriptor custody before immutable source checks

**Status: DRAFT / QD HARD HOLD.** Tracks [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R519 [draft #2986](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2986) at `825b28e82c69ef61b51e40268bebc18e27238de4`, never production `main`.

## Source-integrity defect and fix

R519 bounded `Path.open("rb").read(65_537)`, but did **not** bind the manifest pathname, unique link identity, file-descriptor receipts or exact before/after metadata. A regular hardlink was accepted by that reader, and a pathname could change between the caller's link preflight and its open. The SHA-pinned manifest parser independently prevents altered commands from being accepted; this sprint strengthens the earlier filesystem custody layer rather than claiming that hashes were previously bypassed.

R520 adds `products/desktop/scripts/source_manifest_guard_r520.py` and routes `source_evidence_runner_r509.read_manifest_bounded` through it. It rejects relative, linked/junction-parent, leaf-symlink, hardlinked, missing, empty, nonregular, oversized and descriptor-mismatched files before returning bytes. It reads **at most 65,537 bytes**, captures `lstat` and `fstat` before/after, and refuses changes in inode, link count, size or timestamps. It handles Windows `lstat`/`fstat` ctime differences in **cross-view comparisons only**, retaining strict same-view creation-time stability. Raw descriptor ownership is transferred only after `fdopen` succeeds; failed adoption closes the handle. Path/private operating-system details are not retained in public exception chains.

`load_commands` still checks the exact immutable Git blob, ASCII command grammar, fixed 416-command count and linked test/script preflight. The original 416-command manifest Git blob remains `a55a9b5bcbee5b9f075a39fc581ed5a4716eaca3`; independent Ubuntu/Windows source workflow Git blob remains `7fa8e7633f1357f31ba668bc16f11be79fea5ae4`. No release gate, user CSV, financial engine or licensing behavior changed.

## Exact local execution and limitations (2026-11-18)

- **Linux CPython 3.13.5:** **15/15 PASS** standard (`python -B -W error -m unittest test_manifest_r520_local -v`) and **15/15 PASS** optimized (`python -OO -B -W error -m unittest test_manifest_r520_local -v`), 30/30 focused local executions, no skips. `python -m py_compile source_manifest_guard_r520.py` passed. The exercised helper's local Git blob SHA `fb7bdda9c27bc03b566dc2536db11da2c715061e` matches the actual committed GitHub helper blob exactly.
- **Negative control:** A synthetic regular manifest with a second hardlink was accepted by the original R519 bounded-read algorithm; the exact R520 helper rejected it. This verifies a filesystem-custody gap, **not** a Git digest bypass.
- **Committed regression integration:** 16 new R520 methods appended to the *already-pinned* `products/desktop/tests/test_source_evidence_runner_r509.py`. Three R519 tests were adjusted from mocking `Path.open` to the new descriptor read, preserving bounded-read, private failure and malformed stream assertions. These committed methods and all inherited tests **have not been run checkout-wide**; the 30 passing focused executions used a standalone synthetic harness, not this whole committed module.
- Windows creation-time parity is tested with a simulated `os.name="nt"`; **native Windows execution is still pending**. Path/descriptor checks reduce change windows but **are not an atomic filesystem sandbox** against malicious concurrent mutation.

## CI, production and next highest-impact gate

At inherited R519 commit `825b28e82c69ef61b51e40268bebc18e27238de4`, the three workflows [internal Windows build #44281173690](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44281173690), [independent source #44281173517](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44281173517) and [six-image identity #44281173677](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44281173677) failed before any steps; jobs returned `steps=null`. Root cause **unconfirmed**. Check new R520 exact-head runs separately when available; never count queued/no-run jobs as passing.

**Smallest blocker resolution:** A repository/account administrator verifies GitHub Actions billing/spending limits, workflow permissions and runner eligibility, then reruns exact R520-head Ubuntu/Windows jobs. Next priority is executing **all 416 pinned commands** and the native Windows x64 six-executable smoke, Defender, checksum/provenance, accessibility and protected premium-entitlement matrix. Independent QD review and explicit founder authorization must precede merge, publication or verified download links.

**Release hard hold:** No production merge, CMS/site publication, unsigned/unscanned public executable, unrestricted premium payload, telemetry/upload, automated payment approval or automatic compliance decision.
