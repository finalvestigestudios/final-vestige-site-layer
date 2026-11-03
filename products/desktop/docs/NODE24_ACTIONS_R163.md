# Final Vestige Labs R163 — Node.js 24 immutable CI action upgrade

**2026-11-03 · Issue #73 · DRAFT / HARD RELEASE HOLD**

## Exact upstream evidence and compatibility

R162 pinned six actions to immutable commits but three upstream `action.yml` files still declared Node.js 20. GitHub-hosted runners in November 2026 execute those JavaScript actions under Node.js 24, creating a runtime-compatibility warning and future upgrade pressure. This increment changes **only** the six internal CI action sources and the related narrow fail-closed source/upload guards, fixtures and strict regression inventory. All six apps remain unreleased.

The following upstream **version-tag objects** were read directly from GitHub's REST Git references API on 2026-11-03; corresponding `action.yml` at each **commit SHA** was independently read and found to declare `runs.using: node24`.

| GitHub action | Pinned upstream release | Immutable commit | Source / release |
| --- | --- | --- | --- |
| actions/checkout | v5.0.0 | `08c6903cd8c0fde910a37f88322edcfb5dd907a8` | [Git ref](https://api.github.com/repos/actions/checkout/git/ref/tags/v5.0.0) · [release](https://github.com/actions/checkout/releases/tag/v5.0.0) |
| actions/setup-python | v6.0.0 | `e797f83bcb11b83ae66e0230d6156d7c80228e7c` | [Git ref](https://api.github.com/repos/actions/setup-python/git/ref/tags/v6.0.0) · [release](https://github.com/actions/setup-python/releases/tag/v6.0.0) |
| actions/upload-artifact | v6.0.0 | `b7c566a772e6b6bfb58ed0dc250532a479d7789f` | [Git ref](https://api.github.com/repos/actions/upload-artifact/git/ref/tags/v6.0.0) · [release](https://github.com/actions/upload-artifact/releases/tag/v6.0.0) |

**Runtime requirement:** All three upstream releases require GitHub Actions runner **2.327.1 or later**. The CI uses GitHub-hosted `ubuntu-24.04` and `windows-latest`, not an unmanaged self-hosted runner. Hosted status does not replace a complete, exact-head CI result. The `v5` checkout behavior and `v6` upload-artifact behavior can change over time; this PR holds their specific releases by commit, not mutable major tags. No live program or customer data is uploaded.

## Source and privacy controls

- `.github/workflows/desktop-build.yml` uses exactly two immutable references for each of the three actions, one per operating system.
- `ci_action_pin_guard.py` rejects any nonmatching `uses:` source (missing/duplicate/action substitution) and the previous Node20 commit references.
- `ci_artifact_policy.py` remains an evidence-only allowlist: source JSON, `dist/SHA256SUMS.txt`, and `build/offline-candidate-evidence.json`, each under seven-day retention. **No EXEs or premium binaries are uploaded by CI.**
- `ci_source_contract.py` continues requiring both non-conditional normal and optimized source gates **before** the Windows packaging step. Regression fixtures use the same upstream source pins.
- R163 adds a strict 22-method inventory, executed under normal and `-OO` Python in **both** CI operating systems: **88 planned targeted executions**. The 22 methods cover pin identity, old-runtime rejection, mutable tags, injection/missing steps, real workflow custody, R41 no-premium artifact policy, R57 source gate, the mandatory R163 runner, and privacy-safe error handling.
- R162's historical upstream evidence stays in `IMMUTABLE_ACTIONS_R162.md` rather than being rewritten.

## Local verification (source checkout only)

```bash
PYTHONPATH=products/desktop python products/desktop/ci_action_pin_guard.py .github/workflows/desktop-build.yml
PYTHONPATH=products/desktop python products/desktop/ci_artifact_policy.py .github/workflows/desktop-build.yml
PYTHONPATH=products/desktop python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r163.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r163.py
```

The **complete normal/optimized six-app source suite**, both exact-head CI jobs, six internal Windows x64 PyInstaller builds, and offline metadata verification must also be inspected. Test sources and release notes are *not* evidence of a successful run.

## Release gating

**HARD RELEASE HOLD** remains: 46 independent physical Windows 11 accessibility observations, genuine Defender/EDR assessment, code signing, protected premium distribution and entitlement tests, independent QD exact-head review, and explicit founder authorization. Neither SHA pinning nor a passing CI run constitutes malware clearance, legal/compliance approval, Windows accessibility acceptance or permission to publish any free/premium executable.

**Next:** obtain exact-head Ubuntu/Windows CI logs, repair all regressions on the feature branch, then hand the reviewed evidence for the physical Win11 acceptance lane. Production/CMS never changed.
