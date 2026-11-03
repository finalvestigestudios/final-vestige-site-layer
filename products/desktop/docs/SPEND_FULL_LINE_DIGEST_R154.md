# Labs R154 — SpendMap full vendor/month source-line membership digest (DRAFT / RELEASE HOLD)

**What it fixes.** R153 exposes a deliberate navigation preview of the first 32 physical CSV record-start lines for each normalized vendor/month, with exact contributor and omitted counts. With 33–200,000 contributors, a preview cannot distinguish complete source-line membership sets that share the same earliest 32.

**R154 adds one report column: vendor_month_evidence_sha256.** This lowercase 64-character SHA-256 fingerprint covers the entire numerically sorted list of contributing physical CSV record-start lines, including omitted lines. It binds original source snapshot SHA-256, normalized vendor/month key and contributor count. The same digest repeats across category buckets belonging to the same normalized vendor/month. The digest is computed offline. It is NOT a digital signature, independent source verification, proof of authenticity, compliance decision, refund match, or authorization of payment. Do not sum repeated vendor/month measures across category rows.

## Exact reproducible v1 byte format

Build this *ASCII* stream with an LF (0x0A) after EVERY line:
1. Constant domain line: FVS-SPEND-VENDOR-MONTH-LINES-v1
2. Original descriptor-verified input snapshot SHA-256 in 64 lowercase hex characters
3. Normalized vendor key (ASCII uppercase letters/digits)
4. Month as YYYY-MM
5. Decimal contributor count without leading zeros
6. Every contributing physical CSV start line, base-10 decimal, sorted numerically ascending, one per LF-terminated line.

Then compute SHA-256 of the full byte stream and render lowercase hex. Multiline quoted CSV records use their *physical start line*, not their logical record ordinal or last physical line. The existing source snapshot SHA-256 is retained separately in the report. A full digest is computed even when only 32 of the physical start-line references are visible. Note: an LF is one 0x0A byte (not the two characters backslash and n). SHA-256 membership alone does not independently attest to original bytes being genuine; keep the SHA-bound source and review it.

## Backwards compatibility

Existing source_rows remains category-only. Existing vendor_month_evidence_rows, vendor_month_evidence_count and vendor_month_evidence_omitted values are unchanged. R154 inserts the new field immediately after omitted and immediately before the vendor/month gross figures; all seven existing terminal export columns remain in order. Strict whole-header CSV consumers must update their expected schema; the R59, R135, R141 and R153 tests assert this exact addition. Financial sums, Decimal-safe cents, zero rows, source snapshots, no-clobber output, privacy, review flags and premium restrictions remain unchanged.

## Test scope and release

28 source-owned synthetic tests cover independently calculated expected SHA values; 1/32/33/70/500 contributor boundaries; hidden line membership; quoted multiline physical start lines; month/vendor isolation and collision; same-group reuse across categories; zero-amount contributors; low-precision Decimal traps; original input preservation, deterministic re-export, and invalid input. The fixed-inventory zero-skip/quiet runner is mandatory under normal and optimized (-OO) Python on Ubuntu and Windows: 28 methods x 2 modes x 2 OS = 112 planned targeted executions. Internal Windows x64 CI packaging does not establish independent physical Windows 11 acceptance.

**HARD RELEASE HOLD:** all six standalone apps remain unreleased until independent physical Windows 11 accessibility evidence (46 observations), genuine Defender/EDR review, code signing, authenticated premium distribution, independent QD and founder authorization. No production merge, public executable, or unrestricted premium download is approved.
