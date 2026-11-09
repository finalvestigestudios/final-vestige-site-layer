# Final Vestige Labs R294 — strict CI job-mapping custody

**Status: draft; NOT a Windows binary acceptance, QD clearance, or release authorization.** Tracks [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Isolated R294 feature branch stacked on R293, not production main.

## Defect guarded against

The R293 source-contract checker validates root YAML keys, but previously scanned job bodies for approved commands without guaranteeing a single job-level `steps:` mapping. An additional `    steps:` key (or `steps :`, quoted keys, YAML merge aliases or a second `runs-on:` mapping) could introduce YAML parsing ambiguity while the lexical scanner still observed the original validation commands. Behavior under GitHub's exact YAML loader is not claimed; this is a fail-closed source-policy hardening.

## Implementation

New `products/desktop/ci_job_mapping_r294.py` verifies both job headings and the **exact reviewed four-space job-key sequences**. It accepts the historic R57 fixture's minimal runner/steps form and the current CI's pinned Ubuntu and Windows runner/timeout forms, with source-only `PYTHONPATH` env on Ubuntu. Every duplicate, unknown, reordered or alternate-syntax direct child mapping fails. Comments and six-space-plus nested steps remain outside this narrow mapping guard; the existing step, action-pin, YAML key, upload-scope and source-gate validators are preserved. `ci_source_contract._jobs` invokes the new guard for each job and translates failures to a generic source contract error.

23 focused regression methods cover reviewed forms, comment tolerance, duplicate/quoted/alternate `steps`, duplicate runner, unreviewed job-level permissions/strategy/env/if, aliases, timeout drift and malformed inputs. The two-mode R294 test command is required in both independent Ubuntu and Windows workflow jobs. No EXEs or premium payloads are uploaded.

## Reproduced local evidence (Linux, isolated helper only)

- `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_ci_job_mapping_r294.py'`: **23 passed**.
- Same command with `python -OO -W error`: **23 passed**; total **46 focused test-method executions**.
- `python -m py_compile` on new helper and test: **pass**.
- Git blob hashes of locally executed files: helper `56ae58a97edf597fe9ca474353ed415e7b5983c0`, tests `93f91751a87524417231ee71b838bf68ef069b38`.
- Local private repository checkout was not available. Therefore actual integrated `ci_source_contract.verify_workflow`, inherited tests, Linux hosted jobs, Windows build/Defender, premium gating and customer accessibility **have not been locally verified**.

## Hold and next step

Latest observed previous R293 Actions run [#42543743771](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42543743771) completed failure, with `source-tests` and `windows-build` returning no recorded steps/log URLs; root infrastructure cause remains unconfirmed. Check Actions billing/spend cap, workflow permissions and runner assignment, then rerun **unchanged R294 head** after restoration. Next acceptance: full suite and private Windows x64 builds of all six distinct EXEs, binary SHA-256/smoke/Defender/keyboard-screen-reader and **protected premium delivery** proof. Keep independent QD and founder hard hold before merge/site distribution.
