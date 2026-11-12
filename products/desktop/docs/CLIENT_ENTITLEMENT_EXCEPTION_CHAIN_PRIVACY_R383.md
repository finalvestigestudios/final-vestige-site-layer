# Final Vestige Labs R383 — Client-side entitlement error-chain privacy

**DRAFT / QD + founder HARD HOLD.** Issue #73. Base R382 draft #2226, not main. No release or site modification.

## Defect and actual scope

The customer-side verifier in `fvs_suite/offline_entitlement.py` previously
translated local file-read errors using `raise EntitlementError(...) from None`
**inside** a `ValueError` or `OSError` handler. Python still preserves the
private underlying error in `__context__`, even though default traceback
display suppresses it. A GUI diagnostic, logger, or test inspecting exception
objects could expose customer-local filesystem paths and sensitive metadata.
This affects the offline license read used by **GrantAudit Studio Pro** and
**ProcureGuard Studio Pro**. The four free programs are unaffected.

The new `fvs_suite/entitlement_reader_privacy_r383.py` runs the existing
descriptor-bound `journal_io.read_regular_bytes` once, converts known
`ValueError`/ `OSError` faults into three constant public classifications,
leaves all private handlers, then raises the public `EntitlementError`
without a retained `__cause__` or `__context__`. The public wording for
oversize, unsafe regular file, and inaccessible files is unchanged. The
original 8,192-byte size limit, no-follow/alias/identity checks, Ed25519,
product binding, time-window checks, and fail-closed no-trust-key behavior
remain in the existing verifier. No uploads, telemetry or new accounts.

## Test evidence and boundaries

**Executed locally (2026-11-12, Linux Python 3.13.5):**
- Exact committed helper SHA `81a874687fbdfb905a51a0a9e1f2c5598681a01d`;
  exact committed 16-test SHA `3be5b0e88bde71fa8d9193580ba37a8c50148411`.
  Both matched `git hash-object` on the executed files.
- `PYTHONPATH=<isolated source> python -W error -m unittest discover -s tests -p test_client_entitlement_privacy_r383.py`: **16/16 PASS**.
- Same test command with `python -OO -W error`: **16/16 PASS** (32 method executions).
- Compileall succeeded. Synthetic reproduction of the old `except: raise ... from None`
  behavior confirmed the private `ValueError` survives in `__context__`.
- Positive exact-byte return, once-only reader calls, oversize/unsafe/OSError
  classifications, nested private cause/context, unicode source, both premium
  product labels, stderr/stdout silence, no automatic retries, unmasked interrupts
  and programming errors.

**Evidence limitation:** The 32 executions cover the exact helper/test blobs
in an isolated local Python tree, **not** the complete exact-HEAD
`offline_entitlement.py` import, six-app regression suite, full cryptographic
integration, native Windows execution, or packaging. The integration change is
small but must pass the existing R11/R12/R13/R50 entitlement suites in hosted CI
before QD or founder approval. This is a local diagnostic confidentiality
improvement, not DRM or a guarantee of license validity.

## CI and next release gates

`.github/workflows/desktop-build.yml` now explicitly invokes this exact test
module before packaging on **Ubuntu and Windows, normal and -OO**, four gates,
remaining below the reviewed 224 KiB YAML byte budget. GitHub Actions on the
preceding R382 exact HEAD failed before runner allocation and had one unreachable
annotation per job; the owner must inspect those annotations, billing/spending
limits, and runner eligibility. Do not treat CI YAML presence as CI execution.

Next: establish actual hosted execution, run full six-app plus 22 real AES-GCM
cases and encrypted Ed25519 registry issuance integration, package native
Windows x64 binaries, Defender and accessibility checks, then verify QD/founder
approval and premium download access controls. No executables or URLs published.
