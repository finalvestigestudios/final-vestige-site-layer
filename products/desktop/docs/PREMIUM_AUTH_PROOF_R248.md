# R248 — Premium entitlement proof must be affirmative and fail closed

**Issue #73 | Feature branch stacked on R247 | DRAFT / QD + founder HARD HOLD**

## Reproduced risks and concrete changes

The shared premium review guard on R247 treated only the literal `False` and a short list of expected exceptions as license failure. A broken callback returning `None`, `0`, or another falsey value could be treated as authorized. An unexpected `TypeError` or `RuntimeError` left sensitive report cases and reviewer notes displayed while the exception bubbled out. At first window opening, `open_review_window` invoked `authorize()` but did not check its return value.

R248 requires an **affirmative truthy proof** from the existing authoritative Ed25519 offline entitlement verifier; falsey results, ordinary verification exceptions and broken truthiness protocols deny access. The already-constructed review window scrubs its visible financial evidence on denial. Before constructing the window, a failed/empty proof prevents `tk.Toplevel` creation. Unexpected verifier error details are not displayed or printed. A scrubber failure is still propagated to avoid falsely claiming a successful scrub.

All six launchers and all financial engines remain unchanged. Existing file evidence, human review journals, Decimal calculations, signed-license verification, non-telemetry defaults and premium distribution restrictions are untouched. This is not a substitute for cryptographic verification or a race-free authorization lease.

## Artifacts and checks

- `fvs_suite/review_target.py`: replace literal-`False` guard with strict proof handling and fail-closed exception path.
- `fvs_suite/review_ui.py`: require an accepted proof before constructing premium review controls.
- `tests/test_review_revocation_r247.py`: align the inherited unexpected-error assertion with fail-closed denial.
- `tests/test_review_auth_proof_r248.py`: **14** focused unit + displayless AST/preflight tests, covering falsey proof types, expected/unexpected verifier errors, malformed truthiness, privacy, early window denial and retained valid-proof behavior.
- `.github/workflows/desktop-build.yml`: explicit R248 normal and `-OO -W error` checks on both Ubuntu and Windows before full source suites.

### Verified local evidence (bounded)

On **Linux CPython 3.13.5**, reconstructed helper code and a **minimal, locally reconstructed GUI preflight**, `python -W error -m unittest discover -s products/desktop/tests -p 'test_review_auth_proof_r248.py'` passed **14/14**, and the matching `python -OO -W error` command passed **14/14**. These are **28 isolated test-method executions**; the full committed GUI module and full repository were **not run locally**. The two GUI AST tests used a local preflight reconstruction, so native Windows behavior and committed-source integration remain subject to hosted/native verification. Python compilation passed. No real customer data or license secrets were used.

## Required QD checks / release hold

Run the same R248 test file (normal and optimized) against the **full committed source**, then the R247 inherited and entire six-app test suite. On a real Windows 11 x64 test machine verify falsey/stale authorization cannot open a window, unexpected license failures clear previously loaded synthetic report paths/cases/reviewer notes, and a valid signed entitlement still permits **human-only** exception workflows. Build six distinct EXEs in a private environment, verify SHA-256 and malware scanning, test high-DPI/keyboard/accessibility, and ensure both premium download channels are access-controlled. Hosted CI has been failing before execution (zero runner steps), so a GitHub Actions owner must restore runner/billing/workflow execution and rerun the unchanged draft commit. Independent QD and founder release signoff remain mandatory; no executable/site publication permitted.
