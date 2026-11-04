# R193 — SpendMap full-collection shape and citation preflight (DRAFT; release HARD HOLD)

Tracks Labs issue #73: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73. This work is NOT a public software release and must remain on a feature branch / draft PR until independent QD and founder approval.

## Confirmed defect and repair

R192's fvs_suite.spend_input.validated_spend_rows froze the full input list before callbacks but performed physical-row and source-field checks inside the yielding loop. When a later row had a duplicate/noncanonical physical citation, missing required column or non-native text field, calling next() could already have yielded prior rows and executed vendor/date/money callbacks. Direct-API consumers could therefore observe partial evidence and premature callback effects from a structurally invalid collection.

R193 preserves R192's native-dict collection snapshot and adds a separate O(n) structural preflight over ALL frozen records before any parser callback or yielded record. It validates canonical physical row numbers, uniqueness and native text field types (including optional category), with privacy-safe errors. Only after the entire collection passes does existing validated normalization, date, exact Decimal and month logic execute in original record order.

Compatibility preserved: valid out-of-order physical rows, legacy missing/blank categories, callback order/once-per-record behavior, native Decimal exactness and fixed 200,000-row limit. No original files are written; no network or telemetry.

## Reproduction and local evidence (Linux CPython 3.13.5)

- Exact unmodified R192 spend_input.py Git blob: fdc9864d81e1ce1ac082c29145891d204e6905ab.
- Before repair: 13 of 24 new R193 regression methods FAILED, including late duplicate citations and missing/invalid fields whose earlier record had been yielded.
- After repair, locally executed source Git blob: 6f80964e315873673bb5e8443892c0497dced71e; new test file Git blob: bb76cc6d0da6dfe1cdb6ce3e5a3834761fe963ab. Both match branch blobs after upload.
- In a source-and-test copy at products/desktop: PYTHONPATH=. python -m unittest discover -s tests -p 'test_spend_collection_preflight_r193.py' -q; repeat with python -OO: 24/24 PASS in each mode = 48/48 local method executions. No skips. Python compilation PASS.
- Capacity check: 200,000 synthetic valid records processed (~1.34 s on one Linux 3.13.5 environment; not a Windows benchmark).
- Ubuntu and Windows CI now independently require both modes of the 24-method suite; Windows PowerShell checks every Python exit code.

These are isolated source-and-test results, NOT the full repository, hosted CI, native Windows binaries, GUI, signed installer or catalog. Revalidate committed hashes after any PR revision.

## Trust boundaries and limitations

This is structural preflight, NOT semantic, financial, or cryptographic source authentication. A later text-shaped but semantically invalid vendor/date/amount may still trigger earlier callbacks before the later value is parsed; the enclosing summarizer must not publish partial reports. The generator starts snapshot/preflight at first iteration, not at generator creation. Callers must bind records to an independently descriptor-owned source-byte SHA256 from the canonical importer. R193 does not approve compliance or change source-hash rules.

## QD release gates and next action

1. CI infrastructure: inspect GitHub Actions error banner, billing/usage, permissions and runner provisioning. Run unchanged R193 head with recorded Ubuntu and Windows steps. Earlier R192 Actions #41901752343 failed without recorded executed steps; cause unconfirmed.
2. Execute full inherited repository suite, especially Policy Delta real-file integrations and source-to-output provenance.
3. Privately build, scan, checksum and launch all six Windows x64 apps; capture Windows 11 keyboard/screen-reader/scale and Defender/EDR evidence.
4. Gate premium binaries by actual payment/license controls, complete signing/SmartScreen review and approve site distribution only after independent QD plus founder authorization.

Release HARD HOLD: four free and two premium apps remain unreleased. No production/WordPress update, premium exposure, download claim or executable distribution was authorized.
