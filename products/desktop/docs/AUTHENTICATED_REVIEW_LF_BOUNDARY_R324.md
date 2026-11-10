# Labs R324 — source-bound premium review journal record framing

**DRAFT; independent QD + founder HARD HOLD.** Tracks issue #73. Branch builds on R323 draft #1857, never production. Neither application is released or licensed by this change.

## Why this is a code-level gap

R323 introduced LF-only framing to the **read-only restored-evidence inspector**. The actual premium audit-journal reader, `fvs_suite.exception_review.read_journal`, still used `bytes.splitlines()`. In Python that accepts a bare carriage return as a record separator. Two individually valid, hash-linked JSON events separated by **only CR** followed by the final LF could therefore be accepted by the authenticated vault restore's report-bound reader, despite not being LF-delimited writer output. This creates inconsistent acceptance rules between restore and external inspection.

## Implemented behavior

`fvs_suite.review_line_framing_r324.canonical_review_records` is a bounded, deterministic, local-only record framing parser. `read_journal` now uses it **before** existing per-event JSON schema, report/case binding, SHA-256 hash-chain and chronology checks. It accepts empty journals, LF-delimited events, and legacy CRLF; rejects incomplete endings, bare/internal CR, blank records, NUL, VT, FF, non-byte inputs, >20,000 records, and >16 MiB payloads. It returns only raw record bytes. **This is not a new event signer** or an approval mechanism and does not alter the writer, report bytes, review decisions, Decimal computations, licenses, or website.

## Reproduction and verification boundary

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_line_framing_r324.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_review_line_framing_r324.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_line_framing_integration_r324.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_review_line_framing_integration_r324.py'
python -m py_compile products/desktop/fvs_suite/review_line_framing_r324.py products/desktop/tests/test_review_line_framing_r324.py products/desktop/tests/test_review_line_framing_integration_r324.py
```

Local isolated Linux Python: **23 unit methods × normal and `-OO` = 46/46 passing executions** with actual code; compilation passed. The six full-import integration methods are committed and wired into both CI jobs, but **not executed locally** because the full private checkout is unavailable in the execution environment. They exercise valid two-event SHA chain on real synthetic report cases, CRLF compatibility, bare-CR evasion (previously passed), source byte preservation and no-journal behavior. Hosted CI and native Windows builds are unverified because prior Actions runs failed before steps/runners were allocated. Do **not** count integration methods as passed until executed.

Verified committed GitHub blob SHA equals locally executed source: `4302ff2064a5c914fbe823282801054d7249dc02`; unit-test blob SHA equals local: `96320e4ead50edfd1b1e6737b54968cd5cdb6618`; integration test file blob `e623fa4c3817e243839b6f21cf418b4eb84bdde1` is committed but not locally run.

## Remaining release HOLD

Real authenticated AES-GCM vault test gate (22 mandatory no-skip cases), full desktop suite, six private Windows x64 executable builds and smoke tests, Defender scan, checksums, keyboard/accessibility testing, and access-controlled premium delivery remain required. The apparent GitHub Actions runner/billing failure must be diagnosed by the owner. Independent QD and founder approval remain mandatory before merge/publication; no binaries or customer evidence published. Financial/review events remain local and human decisions remain explicitly required.
