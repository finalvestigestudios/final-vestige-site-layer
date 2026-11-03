# Labs R162 — immutable internal GitHub Actions references

**2026-11-03 · Issue #73 · DRAFT / HARD RELEASE HOLD**

## Finding

The internal six-app build workflow previously invoked mutable `actions/checkout@v4`, `actions/setup-python@v5`, and `actions/upload-artifact@v4` references. A future retag or a compromised mutable action reference could change the code that checks out our private source, executes tests, or uploads **only** approved metadata. A passing test suite does not compensate for changed action code.

## Implementation

Pin the six external action invocations (two per action, across Ubuntu and Windows jobs) to specific upstream commits, confirmed against GitHub upstream tag commit APIs on 2026-11-03:

| Action | Upstream version | Immutable commit |
| --- | --- | --- |
| actions/checkout | v4.2.2 | `11bd71901bbe5b1630ceea73d27597364c9af683` |
| actions/setup-python | v5.6.0 | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| actions/upload-artifact | v4.6.2 | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

`ci_action_pin_guard.py` rejects unknown, missing, repeated, tag-based, dynamically substituted or otherwise changed `uses:` references. The already-mandatory `ci_source_contract.verify_workflow()` invokes this gate, and both jobs separately execute the CLI and strict 21-method regression inventory under normal and optimized (`-OO`) Python. The R41 upload policy is synchronized to accept **only** the pinned upload action and its exact two metadata-only paths; EXEs and any public artifacts remain prohibited. Existing R41/R57 fixtures were updated to the pinned action contract.

Before upgrading any pinned action, independently examine the upstream commit and its changelog, update the literal pin and fixtures, run normal and optimized source tests on both operating systems, and request fresh independent QD review. **Never unpin to fix a build failure.**

## Local source verification

From the repository root:

```bash
PYTHONPATH=products/desktop python products/desktop/ci_action_pin_guard.py .github/workflows/desktop-build.yml
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r162.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r162.py
```

The R162 matrix covers 21 synthetic methods × two interpreter modes × two CI operating systems = **84 planned method executions**. An exit code of zero from an action-source gate means the fixed action references matched; it does **not** prove upstream authorship or that runtime dependencies and applications are free of defects. Only actual completed CI results count as passing evidence.

## Release gates unchanged

The full source/portable binary smoke checks remain in force. Independent **physical Windows 11 acceptance** (46 observations), verified Defender/EDR, code-signing, authenticated premium delivery, QD exact-head approval, and founder authorization remain mandatory. Neither a passing pinned-action gate nor a successful internal EXE build authorizes public distribution. Four free and two premium applications remain unreleased, with no CMS or production change made here.

## Threat-model limit

This narrow source matcher deliberately fails closed for action calls it can see in the fixed workflow, but is not a complete YAML interpreter, supply-chain audit, malicious-runner defense, or proof that a distinct `run:` shell step could not transmit files. The existing independent R41 artifact upload allowlist and R57 source gate are complementary, not replaceable.
