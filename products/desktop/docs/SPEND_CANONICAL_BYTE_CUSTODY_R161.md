# Labs R161 — native SpendMap CSV byte custody (DRAFT / RELEASE HOLD)

The R159–R160 independent verifier checks all 25 source-derived fields, historical review rules, vendor names and native column/row order. But `csv.DictReader` ignores blank physical records and permits equivalent alternative quoting, BOM omission and line endings. Consequently modified report bytes could receive a VERIFIED membership result even though they are **not** the deterministic native export.

R161 adds an **independent streaming serializer** in `fvs_suite/spend_report_envelope.py` (no generator calls). The original report must match canonical Python `csv.DictWriter` UTF-8-BOM, 25-field, minimal-quote, CRLF bytes by **both exact byte count and SHA-256**. All source-bound money/row review checks remain. Originals are never overwritten or uploaded. Error/CLI output uses generic HOLD messages, not client content. The check is NOT a signature, compliance verdict or fraud finding.

Run `python products/desktop/scripts/safe_unittest_r161.py` and `python -OO products/desktop/scripts/safe_unittest_r161.py`. 26 fixed-name synthetic tests; CI runs both modes on Ubuntu and Windows, giving **104 planned targeted method executions** (26×2×2), pending exact-head result. Test categories include valid Unicode/formulas, Decimal credits and multiline sources; rejected blank rows, CR/LF variants, absent/doubled BOM, missing newline, extra optional quotes, QUOTE_ALL, and CLI redaction.

R161 is stacked **only on R160 draft #778**, never main/production. No released apps, download links, unprotected premium EXEs or live site publication. Real Win11 46-check physical accessibility, genuine Defender/EDR, signing, premium entitlements, independent QD approval and founder authorization remain mandatory.
