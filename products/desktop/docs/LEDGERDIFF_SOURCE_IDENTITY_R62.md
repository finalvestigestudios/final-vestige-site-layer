# LedgerDiff Lite R62 — dual-source identity and accidental self-comparison review

**Status: draft source change only; all six Windows x64 apps remain unreleased.**

LedgerDiff cited left/right physical CSV lines and original transaction IDs, but did
not identify which exact *versions* of both files generated those rows. Selecting
the same CSV for both sides can also misleadingly produce a matched report.

R62 imports each side with the existing descriptor-verified CSV reader and obtains
the SHA-256 of **the same raw bytes that were parsed**, without reopening paths.
It appends three columns after the nine existing columns:

| New CSV field | Meaning |
| --- | --- |
| left_source_sha256 | Canonical lowercase SHA-256 digest of imported left CSV bytes |
| right_source_sha256 | Canonical lowercase SHA-256 digest of imported right CSV bytes |
| input_identity_review | identical_source_bytes_review if both byte snapshots are identical; otherwise blank |

Validation rejects malformed digests even when imports have no data. All nine
existing report fields remain in their order. Exact Decimal money, normalization
collision review, missing-side/variance/duplicate statuses and physical row
references are unchanged. A matched row with an input identity review warning
requires **human verification of independent input provenance**. Equal bytes do
not establish an error; different bytes do not prove independent sourcing.

A Windows reviewer can verify preserved originals with:

    Get-FileHash -Algorithm SHA256 -LiteralPath '.\left.csv'
    Get-FileHash -Algorithm SHA256 -LiteralPath '.\right.csv'

The report contains hashes only, not local filesystem paths or additional
customer data. Inputs are read sequentially, not atomically as a pair. An
input could be modified *after* its snapshot; the report still identifies
the bytes that were parsed. These hashes are NOT signatures, trusted timestamps,
fraud findings, independent-origin proofs, compliance approvals, or payment
authorizations. Someone who alters both the source and the report can defeat
this method.

**Known limit:** two valid header-only inputs yield a header-only output, so no
data row contains their hashes or the identical-input warning. Do not treat
such output as a complete evidence manifest.

## Verification and release constraints

Focused pure-code tests: normal and optimized Python (-OO).
Nine added real-engine integration tests cover quoted multi-line/BOM CSV,
physical lines, exact left/right digests, identical files and distinct paths
with identical bytes, newline changes, source mutation after import,
missing-side and empty imports, and fail-closed bad input. Packaged ledger
smoke adds a SHA-256 invariant and same-input review assertion. The complete
repository suite and real Windows x64 executable checks require a trusted full
checkout and functioning runners; source tests alone do not authorize release.

No binaries, public download URLs, premium entitlements, WordPress pages, or
production/QD approvals changed. GitHub Actions infrastructure is issue #75.
