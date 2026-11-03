# R151 — Policy Delta local NFKC substitution custody (DRAFT / RELEASE HOLD)

## Why this matters

R150 correctly warned when **entire decoded policy versions** were NFKC-equivalent but not NFC-equivalent. However, a realistic policy revision can contain an NFKC-only character replacement *and* an unrelated real sentence change. In that case whole-document NFKC equality is false, so the existing R150 review cue disappears. For example:

```text
BEFORE: Limit ⑩
        Owner: Old
AFTER:  Limit 10
        Owner: New
```

R151 adds **local hunk review evidence**, still using the source-owned unified diff and its exact physical-line counters. It does not weaken or replace the R150 whole-document cue.

## Algorithm and conservative limits

- Collect changed removed and added physical source lines *from the existing unified-diff stream*, without a second expensive diff pass. Line numbers are those of the original files, not display row numbers.
- Within each individual hunk, compare removed/added line values under Unicode NFKC. A candidate exists only when the complete lines normalize to the same value, remain different under NFC, and have exactly one corresponding deleted and added line for that normalized value. Ambiguous duplicate lines are **not** confidently paired.
- Sort evidence by hunk and physical source-line numbers. Emit at most **16** review pairs; print the number of extra unique pairs without emitting unbounded report material.
- For each candidate, emit exact before/after physical line numbers plus bounded codepoint counts from the R150 routine. No new source text is copied into the local review note.
- Whole-document NFC/NFKC-only flags remain unchanged. Arbitrary numerical or wording changes on the same line are **not** NFKC-only candidates. Changes in unrelated lines do not hide genuine NFKC-only line pairs.
- These are navigation aids, **not semantic equivalence, legal interpretation, payment approval, policy compliance, a fraud verdict, or an assertion that confusable Cyrillic/Latin letters are Unicode-normalization equivalent**.

## Safety invariants

No telemetry/network account; immutable SHA-256 fingerprints of the original physical source bytes including BOM; existing UTF-8/control checks; descriptor-bound source snapshots; current unified diff and source-line index; private filenames; atomic no-overwrite publication. No changes to Decimal money arithmetic, any premium engine, premium entitlements, WordPress or binary distribution.

## Exact verification contract

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r151.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r151.py
```

Run both on Ubuntu and Windows CI; **29 named zero-skip methods in each of four executions = 116 intended method executions**, alongside the full inherited six-app smoke/source gates and Windows internal build. CI results must be checked on the exact new commit before claiming success. Synthetic cases include mixed revisions, distant hunks, ambiguous duplicates, bounded 16-pair output, Windows line endings, missing final newline, normalization false positives, deterministic replay, source hashes, no overwrite, and privacy-safe invalid-input rejection.

The six standalone Windows x64 products remain **UNRELEASED**. Exact-head CI is not real Win11 accessibility/46-check acceptance, physical Defender/EDR scanning, code-signature trust, authenticated premium delivery, independent QD authorization or founder approval. Keep this draft stacked on R150; HARD HOLD on publication.
