# Final Vestige Labs R164 — fail-closed YAML action-key custody

**2026-11-03 · Issue #73 · draft PR / hard release HOLD**

## Why this change is needed

R162 and R163 pin six external CI actions to audited immutable commits. However, a line-oriented SHA verifier could silently skip GitHub Actions YAML equivalent key spellings (for example `uses :`, `"uses":`, `'uses':`, flow-mapping entries, and quoted Unicode escapes), allowing an additional unreviewed action invocation to escape the immutable-source inventory. This is a defense-in-depth source-configuration safeguard, not a report of active abuse.

## Implemented contract

- `products/desktop/ci_action_key_guard_r164.py` permits exactly six conventional YAML action keys: four `      - uses:` and two `        uses:`, matching the existing Ubuntu/Windows jobs.
- Explicit/quoted/inline/unicode-escaped alternative keys and YAML merge keys fail closed. Unknown new workflow formats require QD source review before admission.
- The existing `ci_action_pin_guard.verify_action_pins` now runs this independent syntax check *before* checking each exact R163 SHA. The pinned action inventory is unchanged.
- `tests/test_action_key_custody_r164.py` has **21 deterministic synthetic methods**; `scripts/safe_unittest_r164.py` executes an exact no-skip inventory with private stdout/stderr suppression. The workflow invokes it under normal and `-OO` Python on Ubuntu and Windows.
- No client files or financial records enter CI. Zero telemetry; all six executables remain internal/unreleased and the premium binaries have no public routes.

## Verification boundary

Local source-only execution: 21/21 distinct R164 tests PASS in normal Python and 21/21 PASS in optimized `-OO` (42 local targeted executions). Real GitHub-hosted Ubuntu and Windows CI must be verified at the **exact PR head**. Prior R163 run #41658476903 on November 3 failed **before runner steps**; it does not verify or invalidate R164. A green source suite still cannot substitute for physical Windows 11 46-check review, genuine Defender/EDR assessment, signing, gated premium distribution, independent QD approval or founder authorization.

To reproduce in a complete checkout:

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r164.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r164.py
python products/desktop/ci_action_pin_guard.py .github/workflows/desktop-build.yml
```

This is a narrow lexical check, **not a YAML parser** or a guarantee against arbitrary malicious shell commands or a compromised repository owner. Do not use its PASS status for release approval.

## Next blocking action

Repository owner: inspect GitHub Actions runner-allocation failure banner and Actions/billing/policy status, then rerun the exact-head PR CI. After cross-platform verification, independent QD reviews the branch; no merge to production until authorization. Physical Windows 11 accessibility/Defender/signing/protected premium delivery remain hard HOLD.
