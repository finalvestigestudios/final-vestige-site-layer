# R150 — Policy Delta compatibility-folding evidence (DRAFT / RELEASE HOLD)

## Scope and review semantics

Policy Delta Desk now recognizes **NFKC-only equivalence** as a *distinct audit cue*, never as a legal/compliance equivalence finding. When the full UTF-8 decoded texts differ and are **not NFC-equivalent**, but NFKC normalization produces identical texts, the report emits an explicit **REVIEW** warning. This catches visually similar or confusable substitutions such as fullwidth A vs ASCII A, fi ligatures, circled numbers vs ordinary digits, superscripts, halfwidth katakana and mathematical presentation letters. These may have genuinely different legal or operational meaning; humans must consult the source originals.

The report includes a **maximum 16 sorted U+... compatibility-sensitive codepoint identifiers** whose aggregate source occurrence counts differ between before and after. This is navigational evidence, not a claim that every listed character belongs to a changed hunk. Where character counts are equal but order changes, the report says so explicitly; physical line citations and original SHA-256 source fingerprints remain authoritative. No full policy text is repeated beyond the preexisting diff report.

This is deliberately separate from R149's NFC canonical-composition cue (e.g. é vs e + combining accent). Byte-identical, BOM-only, CRLF-only, canonical-only, and arbitrary real wording changes MUST NOT be mislabeled NFKC-only. Existing bounded stable descriptor-read snapshots, Unicode control rejection, private file paths, no-overwrite publishing and local processing remain unchanged. No financial money logic or premium entitlements are changed.

## Test and CI evidence requirements

Source-owned 30-method regression suite: `python products/desktop/scripts/safe_unittest_r150.py` and `python -OO products/desktop/scripts/safe_unittest_r150.py` with Python import path `products/desktop` (set `PYTHONPATH=products/desktop` outside the CI Windows step). CI requires **all 30 exact named tests with zero skipped** in both modes on Ubuntu and Windows (120 total targeted method executions across systems). Do not assert pass until exact-head job logs confirm it.

No physical Win11 46-check human acceptance, genuine Defender/EDR assessment, signing, gated premium distribution, independent QD review, founder approval or production/WordPress release is provided by this source sprint. Six applications remain UNRELEASED. No binaries or premium downloads may be published without the independent release gates.
