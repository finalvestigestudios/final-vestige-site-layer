# R106 — Bounded mandatory native-unit test timeout (PRIVATE HOLD)

Issue #136. Draft PR against exact R105 parent `d12e39f9b90455e9c12dc6914f121cc6546bc77d`. This is a **CI execution reliability change**, not a waiver, source reclassification, a publication release, or a qualified emergency/medical assessment.

## Verified symptom and narrowly scoped remediation

The immutable R105 mandatory run [41729663679](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41729663679) entered the mandatory integrity stage around 22:19:32.79 UTC and returned a fail-closed `native_unit_suite` error around 22:22:33.64 UTC — approximately **180.85 seconds**. The original preflight's `execute(..., timeout=180)` passes that exact ceiling to `subprocess.run` for **every** stage. R104 also failed at almost exactly 180.83 seconds. The independent R105 9,060-test suite took 176.986 seconds on one hosted runner; prior runs varied, including runs over 200 seconds.

This timing strongly indicates a per-stage timeout, but is **not proof** of the underlying exception from prior redacted receipts. R106 fixes the likely limitation without shortening the tests: **only** the required `native_unit_suite` has a separate 480-second default. The original 12 other mandatory stages retain their **180-second** ceilings, and the contract continues to demand all 13 in the same order. Both values remain integer-bounded to 10–1,200 seconds. The 30-minute top-level GitHub Actions job timeout is unchanged. No workflow contract, permissions, triggers, checkout SHA, head requirement, or release authorization is modified.

The receipt emitted to stderr upon failure now includes a fixed safe category `failure_kind` in `TIMEOUT`, `EXIT_NONZERO`, `CUSTODY_OR_EXECUTION`; it does **not** reveal private source text, original exception payloads, or internal filesystem paths. On any timeout, nonzero process return, malformed results, head/source drift, or downstream gate failure, the pipeline still halts and reports `INCOMPLETE_OR_FAILED`, `release_state=HOLD`, `may_publish=false`. The existing R19 successful receipt schema, SHA256 fingerprints and all 13 stages remain unchanged.

## Synthetic regressions (never claimed as real-world safety approval)

`python -I -m unittest discover -s preparedness/tests -p 'test_r106_*.py' -v`: 60 deterministic cases exercising a synthetic 9,060-test/216-second result, the old 180-second failure, passing 480-second native budget, invalid unbounded/boolean/noninteger budgets, preservation of other stage limits, 13 original gate order, source-unchanged fake checkout and correct fail-closed timeout/exit/custody receipt categories. No tests sleep, call the internet, or mutate tracked author files. The actual full suite must separately run in the trusted hosted runner, and both `validate.py` and `build.py` must run.

The R106 exact-head private diagnostic workflow also checks the eight independent Git refs and the four-file-only diff. It invokes the real preflight, then the immutable R19 workflow-contract and full 13-step receipt checks. The **separate mandatory GitHub workflow must pass independently**; a diagnostic green does not override mandatory failure.

## Source/citation and editorial exclusions

35 original full-length article drafts, one complete tool, 30 human-unreviewed shared-URL groups, the original seven contributor branches plus RC, individual citation context, author notes, publication-status gates, historic evidence, 15 safety exceptions and 22 editorial decisions are neither edited nor approved here. Five planned tools remain unfinished. No WordPress/CMS, page, navigation, URL, public or homepage change.

**Required before any publication:** successful complete mandatory integrity; independent source-to-claim review (including all 30 shared URLs and 5 contributor-provenance discrepancies); qualified review of high-consequence emergency/medical instructions; browser/print QA; resolution of safety/editorial holds; actual independent QD approval and explicit publication authorization. Passing the machine gate is still `HOLD`, not a release.
