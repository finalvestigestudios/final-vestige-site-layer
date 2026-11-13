# Labs R411 — ancestor custody and per-child offline source continuity

**Scope:** issue #73, six standalone Windows x64 app source launchers, **DRAFT ONLY**. No release, production merge, WordPress changes, entitlement changes, billing, license material, executable upload, or public premium link. Independent QD and explicit founder approval remain hard requirements.

## Reproduced prepatch defects

1. R410 checked the desktop root and its package/launcher directories with `lstat()`, but **not every parent directory**. A root reached through an ancestral symbolic link or Windows reparse/junction directory could pass source verification while executing from an unexpected tree.
2. R410 computed an initial source digest and checked it only **after all 12 children**. If a child changed or deleted an imported source, the gate could still start the remaining 11 children before finally rejecting the receipt.

The R411 regression suite was executed with the **exact R410 Git-blob runner** (`19fd24622226d68b86ecde5e9be56a964a547a99`): 9/12 new synthetic methods failed, as expected. This is a synthetic local threat-model reproduction, **not** evidence of an observed customer incident or real attacker.

## Implementation

- Reject relative desktop root paths rather than resolving through an uncontrolled parent.
- Validate each ancestor from the filesystem root down to the desktop checkout using `lstat` and Windows `FILE_ATTRIBUTE_REPARSE_POINT` checks; continue validating suite, launchers and nested suite directories.
- Compare the exact original SHA-256 source inventory before **each** of the fixed 12 child runs and immediately afterward. The first detected mutation terminates the gate with a private-data-free `SourceGateError`; no remaining children launch.
- Preserve `-I`, normal/optimized execution, secret-denying subprocess environment, OS-level discarded child output, fixed inventory, no shell or stdin, timeout, deterministic successful receipt and `release_authorized=false`.
- No financial engine or `Decimal` logic, compliance rules, review queues, premium entitlement, or product output changes.

## Reproducible focused evidence (2026-11-13 PT)

- Matched the prior runner against actual Git blob `19fd24622226d68b86ecde5e9be56a964a547a99`.
- R411 edited runner Git blob: `ac90cd809c3c5a90648465b99f8727acc1f53609`.
- R411 regression file Git blob: `9276cc1f98f77648b6b2124cd501fba72b2d113c`.
- Locally ran exact edited Git-matched runner and 12 new test methods: **12/12 PASS** under `python -W error`, **12/12 PASS** under `python -OO -W error` = **24/24 focused method executions**.
- The test harness creates a temporary synthetic six-launcher source tree, with actual local Python child processes for the pass path and deterministic mocked mutation probes for fail-closed paths. It does **not** represent a full repository checkout or six real financial engines.
- **Not verified:** full repository regressions, actual six product launchers, Windows native reparse behavior, hosted Ubuntu/Windows CI, x64 PE, Defender, NVDA/high-DPI, signed packaging, premium protected delivery.

## Reproduce in a full trusted checkout

```sh
python -W error -m unittest discover -s products/desktop/tests -p test_offline_source_continuity_r411.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_source_continuity_r411.py
python -I products/desktop/offline_source_smoke_r408.py
```

Repeat the existing R408–R410 focused tests and full six-engine/Decimal, crypto, source custody and keyboard integration suites on **Windows and Ubuntu**. The independent source workflow includes the R411 methods on both operating systems.

## Residual limitations and release hold

Digest continuity detects a source change **between inventory checks**; it is **not** immutable filesystem enforcement, process sandboxing, or protection against a transient change that an attacker restores before the next digest. A hostile local user with concurrent write rights must not be treated as an acceptable build environment. Use an isolated, write-protected trusted checkout and genuine OS/runner attestation for release validation.

The suite is **not released**. Do not promote any source-only results to Windows executable validation. Next: resolve GitHub Actions job allocation or execute trusted full-checkout tests, then validate genuine Windows x64 packaging, Defender scan, accessibility, release checksums and gated premium distribution, followed by independent QD and founder approval.
