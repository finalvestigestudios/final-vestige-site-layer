# R192 — SpendMap full-collection source custody before callbacks

**Status: draft / HARD RELEASE HOLD.** This is a direct Python API audit-integrity fix for SpendMap Lite, not a product release or attestation of financial correctness.

## Reproduction on the exact R191 source

R191 `fvs_suite/spend_input.py` (Git blob `62c4f729b6008729d23d609a19c8503daf0968e8`) copied each input dictionary only when the generator reached that record. A caller-provided vendor/date/money callback for physical line 2 could modify an as-yet-unvisited line 3, or append/delete/replace/reorder the caller-owned list. The subsequent report then attributed *the modified data* to the supplied source SHA even though no new source-byte snapshot was taken.

Local synthetic reproduction before fix:

```text
input rows:            [row=2 ACME 10.00, row=3 BETA 25.00]
normalizer mutates:    row=3 -> row=99 FORGED 1000000.00
reported parsed rows: [row=2 ACME 10.00, row=99 FORGED 1000000.00]
```

## Repair

`validated_spend_rows` now makes a complete collection of **native dictionary-storage copies before calling any normalize_vendor, parse_date, or parse_money callback**. Subsequent calculations consume only owned copies, not the mutable original list or original dictionaries. Native `dict.keys`/`dict.items` avoid subclass-overridden lookup/iteration hooks. The existing 200,000-row guard applies before copying. The source list is never intentionally edited by the engine. Missing or nonnative records and field names fail before callbacks. Existing input ordering and original physical source-row labels, including deliberately out-of-order direct API inputs supported by R68, are preserved.

This is a **point-in-time Python-memory copy**, not a concurrency lock, a verification of source hash authenticity, a cryptographic attestation, or protection against adversaries changing a file on disk. CSV ingestion retains its independent descriptor/snapshot checks. No payment approval or compliance decision is automated.

## Exact-source verification (local isolated Linux)

- Original source reconstructed to **exact R191 Git blob SHA-1** `62c4f729b6008729d23d609a19c8503daf0968e8` before applying the patch.
- Fixed module Git blob SHA-1 `fdc9864d81e1ce1ac082c29145891d204e6905ab`.
- Focused synthetic test module Git blob SHA-1 `4914574e14e31b7f78edd3cf24404563056d037f`.
- **23/23 normal Python PASS**, **23/23 Python -OO PASS**, **46/46 local focused executions**, no skips/failures/errors. `compileall` passed.
- Coverage: callback-induced future-row overwrite, amount/date/category changes, deletion/replacement/append/reversal of records, malicious dict subclasses, source-row order compatibility, early malformed mapping/key rejection, secret-safe errors, low precision/trapping Decimal contexts, no duplicate row regressions.
- Exact test command from `products/desktop` with `PYTHONPATH=.`:

```sh
python -m unittest discover -s tests -p 'test_spend_collection_snapshot_r192.py' -q
python -OO -m unittest discover -s tests -p 'test_spend_collection_snapshot_r192.py' -q
```

**Limitations:** Local verification was from an isolated exact-source module/test copy, NOT full-repository integration, Windows 11, GitHub-hosted CI, or packaged executable execution. The synthetic regression fixture does not use real financial data. Inherited tests (including R68 and Policy Delta's real-file integration cases) are committed to the workflow but were not all executed locally in this sprint.

## CI / review / release requirements

Two independent mandatory R192 steps are added to `.github/workflows/desktop-build.yml`: Ubuntu `source-tests` and Windows `windows-build`, each running normal and optimized tests. PowerShell checks `$LASTEXITCODE` after *each* test call. The existing full source-suite gate and release protections are unchanged.

Prior R191 [GitHub Actions #41892608628](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41892608628) completed in failure, with both jobs reporting no executed steps. There is no basis to claim hosted R192 tests or Windows builds passed. An owner must inspect the exact Actions failure banner, billing/usage limits, permissions and runner provisioning; restore allocation and rerun the unchanged R192 head. No bypass or substitute test result authorizes release.

**QD acceptance remains separate:** full inherited and 14 outstanding Policy Delta real-file integrations; build/smoke/checksum six private Windows x64 EXEs; physical Windows 11 accessibility and AV/EDR checks; signing/SmartScreen decisions; protected premium entitlement and delivery; independent QD and founder approval. **All six programs remain UNRELEASED.** No live WordPress or production changes, no public binaries, no premium files/URLs.
