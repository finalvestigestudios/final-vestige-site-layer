# Labs R297 — CSV parser hidden exception-chain privacy (DRAFT / HARD HOLD)

## Defect, scope, and mitigation
The shared `fvs_suite.engine.table` CSV importer catches `csv.Error` and `UnicodeError` at header and record boundaries. Its legacy `raise csv_input_error(...) from None` runs **inside** those exception handlers. This suppresses on-screen chained tracebacks, but does **not** clear `ValueError.__context__`. A UnicodeDecodeError can retain imported financial bytes in `.object`; automated error reporting can inspect the hidden context.

R297 introduces `safe_csv_header` and `safe_csv_rows` and integrates them into `table`. They translate parser errors into existing allowlisted `csv_input_error` diagnostics **after** their original exception handlers have ended, leaving no parser exception in the returned exception chain. An existing in-loop fallback is also moved outside its handler. No source text, customer identifiers, paths, or parser exception messages are interpolated into user-facing errors.

## Contracts preserved
- Same `csv.reader(strict=True)`, no encoding normalization or altered source bytes.
- Same physical `reader.line_num` and multiline CSV row attribution; same header aliases, CSV row and import byte limits, NUL checks, source SHA-256 and explicit column selection.
- Same empty-file handling, row traversal order, and fail-closed malformed-header/record errors.
- `KeyboardInterrupt`, `SystemExit`, `MemoryError`, and unrelated runtime exceptions are not silently suppressed.
- No changes to money/Decimal, audit decisions, privacy/network controls, premium gates, production, or site publication.

## Evidence and reproduction
Linux local isolated helper validation on synthetic parser fixtures (not the full private checkout):
```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_parser_privacy_r297.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_parser_privacy_r297.py' -v
python -m py_compile products/desktop/fvs_suite/csv_parser_privacy.py products/desktop/tests/test_csv_parser_privacy_r297.py
```
**18/18 PASS standard, 18/18 PASS optimized = 36 passing focused method executions** for the isolated helper and actual unchanged `csv_diagnostics.py` (synthetic inputs). Tests cover real invalid UTF-8 and strict malformed CSV, injected parser exceptions, no `__context__`/`__cause__`, bounded source line labels, row provenance, EOF and interrupt preservation. This does **not** claim full `engine.table` integration, complete inherited suite, GitHub CI execution or native Windows acceptance. Those remain mandatory.

## Release / CI / owner action
Prior R296 GitHub Actions run #42559512570 completed failure with both `source-tests` and `windows-build` showing `steps:null`; no test or runner execution evidence. Inspect Actions account billing/spending restrictions, runner assignment and workflow permissions; rerun this exact draft PR commit once runners are provisioned. Independently validate `engine.table` end-to-end with malformed private UTF-8 files on Windows, then full six-application portable EXE build/smoke, Defender, a11y, SHA-256 evidence, restricted premium delivery and independent QD/founder approval. **No merge or release is authorized by this patch.**
