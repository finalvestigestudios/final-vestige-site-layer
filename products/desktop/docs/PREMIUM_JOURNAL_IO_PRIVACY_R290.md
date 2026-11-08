# Labs R290 — premium journal I/O privacy and empty-file custody

**Status: DRAFT; issue #73.** Stacked on R289 head `8c89127b79e807820db01ef17028421f109ffba5`. The independent QD/founder approval hold remains mandatory; no changes to `main`, live catalog, payments, premium distribution, or published binaries.

## Defects reproduced

Both premium apps share `fvs_suite.journal_io` to read and append offline human-review records. Before R290, permission errors from `lstat`, `open`, `fstat`, `write`, `fsync` and the verification callback could propagate raw `OSError` objects containing private customer paths. An internal path-disappearance branch explicitly chained the original `FileNotFoundError` into a `ValueError`, exposing the path through `__cause__`. Suppressing traceback printing alone is insufficient: the exception's `__context__` and `__cause__` are inspectable.

The pre-write failure cleanup for a *new* journal previously checked only the inode and zero-byte size. A touched or metadata-changed empty journal with the same inode could be unlinked despite uncertain custody.

## Fix and contract

- `_redact_os_errors` translates raw filesystem `OSError` into a fixed `ValueError` **after leaving** the handler, so the raised object has neither a private-path cause nor context. Existing deliberate domain `ValueError` and process interruptions retain their semantics.
- `_same_path` reports disappearance without attaching the underlying private-path `FileNotFoundError`.
- On a failed *new, unwritten* append, remove an empty file only if the same-view **complete pathname snapshot** is unchanged, including size, timestamps, link count and identity. If inspection never reached a confirmed pathname baseline or detects drift, leave the evidence for a person to inspect.
- A partially written or fsync-failed journal is **not rolled back**; it remains indeterminate and requires manual review, rather than claiming a successful event.
- Existing R47 tests expecting raw `FileNotFoundError` / `OSError` were changed to assert the new, more restrictive privacy contract.
- No changes to Decimal arithmetic, compliance judgments, payment approvals, offline processing, licensing, or the four free applications. These checks do not defeat privileged filesystem mutation or guarantee Windows-specific behavior.

## Measured local test evidence — 2026-11-08

Local Linux Python, synthetic temporary financial journal names, actual files/descriptors, injected permission/IO failures:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_io_privacy_r290.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_io_privacy_r290.py' -v
python -m py_compile products/desktop/fvs_suite/journal_io.py products/desktop/tests/test_journal_io_privacy_r290.py
```

- **12/12 PASS** standard and **12/12 PASS** optimized: **24/24 focused method executions**; compilation PASS.
- Replacing the candidate source with the exact committed R289 parent blob produced **11 failures/errors out of 12 tests** (9 errors, 2 failed assertions). The normal byte-for-byte success control passed both versions.
- Exact source custody: R289 parent `journal_io.py` blob `938155bbd8f967e23e2057d281e75bbc37c5a8e2`; R290 implementation blob `1850df4c21412f579c7100d8697e8ed396bae7dd`; new regression blob `749b1f064caf5bf1e234186020945cb4cb521ba4`. Local Git-blob hashing and GitHub blob SHA comparisons match.
- Ubuntu and Windows GitHub Actions definitions include explicit normal and optimized R290 tests, but **hosted execution, inherited full-suite integration, and native Windows x64 acceptance are not verified**. The synthetic Windows mock/fixture suite was not run locally.

## Release blockers and next highest-impact acceptance

R289 parent [Actions run #42523330174](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42523330174) failed with Ubuntu and Windows jobs both showing `steps: null`, with no recorded test/build work; the root cause remains unknown. Owner action: inspect Actions billing and spending limits, workflow permission policy, and available runners. Then rerun the unchanged R290 commit on an approved runner.

On a trusted Windows 11 x64 environment, execute full repository regressions, six real portable EXE builds and smoke tests, SHA-256, Microsoft Defender, keyboard/screen-reader witness checks, and *private* premium delivery/entitlement verification. No executable or public download URL is ready. **Do not merge or release until independent QD and founder authorization.**
