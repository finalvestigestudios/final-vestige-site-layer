# R198 — Policy Delta NFKC physical-citation custody (DRAFT / HARD HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Branch `feature/labs-policy-nfkc-source-custody-r198-20261104` is stacked on R197 draft PR #1016 at immutable parent `1fef3111d75522567a3fff348c5b5dd8406864e4` (not `main`).

## Scope and concrete defect

The pre-R198 `_local_compatibility_evidence` helper walked caller-supplied hunk mappings and list pairs without first validating their physical source identities. Unlike the NFC and cross-script helpers, this NFKC-only evidence path could generate human-review citations from repeated/backward/forged coordinates, invoke custom object behavior on direct calls, or emit valid-looking earlier citations before discovering malformed later input.

This is a **source-identity trust-boundary hardening** improvement, not evidence of a remotely exploitable GUI vulnerability. The ordinary TXT/MD/CSV path builds hunks internally; direct Python API inputs and later maintenance are the risk.

## Implementation

- New `fvs_suite/policy_compatibility_custody.py`: `owned_nfkc_hunks` verifies the entire supplied list before a single human-review citation may be rendered. It checks exact native list/dict/string/tuple/int types, all mapping keys before field lookup, increasing and nonrepeated physical lines **across** hunks, reader's 50,000-line cap, and a 10 MiB-per-side text budget. Overlong lines are validated but excluded from optional compatibility navigation.
- `policy_diff.py` now uses those validated, staged native source rows. Existing unique NFKC pairing, deterministic source-number ordering, 16-pair cap and human-review-only disclaimers remain.
- New `tests/test_policy_nfkc_custody_r198.py`: **26 regression methods**, including genuine NFKC positives, ambiguous duplicates, malicious keys and container subclasses, coordinate collisions, late invalid records, long lines, bounds and unchanged inputs.
- Neither input files nor exact byte fingerprints are modified. No uploads, telemetry, automated legal conclusions or payment decisions.

## Reproducible focused local verification

Environment: Linux CPython **3.13.5**. Exact Git blob comparison for the two new independently testable files:

| File | SHA-1 Git blob |
| --- | --- |
| `fvs_suite/policy_compatibility_custody.py` | `c751525fa0e1947364d729f35e7ca11ed7e92dd6` |
| `tests/test_policy_nfkc_custody_r198.py` | `1090c06b415bd4ca11b89d4aa2bf8567be0f849d` |

Executed in an isolated package root with `PYTHONPATH=.`:

```sh
python -m unittest discover -s tests -p test_policy_nfkc_custody_r198.py -q
python -OO -m unittest discover -s tests -p test_policy_nfkc_custody_r198.py -q
python -m py_compile fvs_suite/policy_compatibility_custody.py tests/test_policy_nfkc_custody_r198.py
```

**26/26 PASS normal; 26/26 PASS -OO; 52/52 total focused executions; compilation PASS.** No skipped tests. The isolated new guard and its committed test file are byte-identical to the GitHub blobs. The new `policy_diff.py` call-site was inspected in GitHub but **not executed against the complete inherited repository**. These results are *not* evidence that the whole desktop suite, Windows builds, CI or native UX passed.

## Review / distribution gates

- Draft stacked PR only. No production `main` merge, WordPress publication, hosted downloads or publicly accessible premium file.
- QD reviewer to run the complete inherited Python suite in normal and `-OO` on Ubuntu and Windows, including R150/R151/R197 Policy Delta real-file tests to catch integration drift.
- Current GitHub-hosted runner problem: R197 [Actions #41946214091](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41946214091) failed with zero steps for both source-tests and windows-build; root cause undetermined. Inspect Actions failure banner, billing/usage, repository permissions and hosted-runner allocation. Rerun an unchanged commit once scheduled execution is restored.
- All six standalone Windows x64 apps are **UNRELEASED**. Private builds must be checked for functionality, hash, Defender/EDR, Windows 11 keyboard/screen-reader access, signing, premium access control and independent QD/founder sign-off before release.

**Next highest-impact step:** restore actual hosted CI execution and run full inherited source/integration tests, then privately build, hash, scan and smoke all six candidates. This branch makes no release claims.
