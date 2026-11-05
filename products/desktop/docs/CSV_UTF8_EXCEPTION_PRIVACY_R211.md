# Final Vestige Labs R211 — UTF-8 evidence and sanitizer-error privacy custody

**Scope:** Shared `products/desktop/fvs_suite/atomic_reports.py` for all six local-first utilities. **DRAFT / HARD RELEASE HOLD.** This work is stacked on R210, not `main`, and does not publish files or bypass the QD/founder gates.

## Reproduced defects

1. Python native strings may contain lone UTF-16 surrogate code points (`U+D800`–`U+DFFF`). The R210 renderer accepted them. A following `TextIOWrapper` UTF-8 write raised `UnicodeEncodeError` (potentially including sensitive report data in the exception object) instead of the static, privacy-safe CSV boundary error.
2. A caller-supplied cell sanitizer could raise an exception containing sensitive claim values; R210 propagated that exception unchanged to callers that might present it in desktop UI/error logs.

Both failures occurred even though the writer correctly removed partial output. R211 now rejects all surrogate code points **after** invoking the sanitizer and before writing to the CSV encoder, and converts ordinary sanitizer exceptions into `ValueError("CSV report cell sanitizer failed") from None`. It does not swallow `KeyboardInterrupt` or `SystemExit`.

The new check applies to headers, declared fields, and ignored extra fields. Valid supplementary-plane characters, UTF-8 BOM, quoted multiline cells, Decimal text formatting, and negative amounts remain supported. The converter is still called exactly once per supplied cell. No change to accounting math, schema identity, report naming, audit provenance, compliance conclusions, or publication semantics.

## Local regression evidence (2026-11-05)

Environment: Linux CPython 3.13.5. The isolated harness reproduces **exact Git blob content** of the shared writer, new R211 tests, and inherited R27 tests; does **not** establish full repository integration.

- **RED** (unmodified R210 writer + 14 new tests): 5 failures and 2 errors; 7 tests passed. Unpaired surrogates produced `UnicodeEncodeError`, and sanitizer exceptions retained private text.
- **GREEN** after R211 writer patch: R211 14/14 normal, 14/14 optimized (`python -OO`).
- **Inherited R27**: 11/11 normal and 11/11 optimized (including BOM, multiline, prior-file overwrite resistance, POSIX symlink resistance, private permissions, 5,000-row lazy iteration and rollback).
- **Combined:** 25/25 normal plus 25/25 optimized; **50/50 test executions passed**. `python -m py_compile` PASS.
- **Git blob verification:** writer `c8767290f430748950b8063ea849982ec1f6fb44`; R211 tests `8b404769c75cdc661f2b79e8988119a733bc7f52`; inherited R27 tests `d5b02b5e0be0c1a9d31a6181191b29212d02740a`. Matches the source files obtained from GitHub. All tests used synthetic fixtures.
- Workflow `.github/workflows/desktop-build.yml` now includes R211 normal/optimized tests on Ubuntu and Windows with non-zero-exit enforcement and suppressed unittest output.

## Still blocked / NOT verified

- R211 GitHub-hosted Ubuntu/Windows CI steps: **not yet verified**, pending the draft PR's run. Prior R210 run [#42040941149](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42040941149) showed `source-tests` and `windows-build` failed with no exposed step records; root cause not confirmed. Owner should inspect Actions banner, billing/usage cap, permissions, runner availability; restore and rerun the **unchanged R211 commit**.
- Full inherited R207–R210 matrix, six real GUI-to-export paths, actual Windows x64 binaries, Defender scans, accessibility on Windows 11, code signing, premium access controls, independent QD review and founder approval are **not** complete.
- `from None` suppresses an exception's *displayed* context, not its internal `__context__` reference; the UI/logging layer still must avoid introspecting and logging underlying exception objects.

## Next highest-impact step

Restore hosted CI and execute complete inherited regression and all six application's real export paths (including encoding-error and sanitizer-error behavior), then privately build, hash, scan and smoke-test Windows x64 candidates. QD must independently verify privacy, installation, licensing and accessibility; founder must approve release. **No WordPress deployment, direct `main` merge, public download, or ungated premium distribution.**
