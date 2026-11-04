# R179 — Policy Delta Desk numeric Unicode evidence, release HOLD

## Scope and reason

R178 identifies uniquely paired NFC-equivalent changed policy lines but cites only physical line positions. When a reader or screen reader cannot distinguish composed and decomposed glyphs, the report has no machine-readable character-level navigation cue. R179 adds **bounded non-ASCII codepoint count differences** to each of the first 16 canonical candidates, while leaving original source bytes, SHA-256 fingerprints, the unified diff, and all human legal/compliance review requirements authoritative.

Examples (entirely synthetic): `Café` → `Cafe` + `U+0301` reports `U+00E9 1->0, U+0301 0->1`; reordered marks with the same totals report `non-ASCII counts unchanged; inspect codepoint order`. The metadata never prints source text, cannot confirm legal equivalence, and does not call a network service.

## Bounds and privacy

At most **16** unique canonical candidate pairs are displayed; per displayed pair, at most **12** changed non-ASCII codepoints are described. If either line contains more than **64 distinct non-ASCII characters**, the cue is withheld rather than allocating a potentially huge count map. Omitted diagnostic counts are explicit. Ambiguous or cross-hunk matching remains prohibited. The existing output text is extended, not otherwise normalized or rewritten.

## Testing and evidence boundary

Synthetic 24-method test module covers precomposed/reordered marks, Hangul/Japanese, privacy, non-equivalence, BMP/supplementary Unicode, limits, truncation, unchanged codepoint totals, source row order and deterministic replay. `scripts/safe_unittest_r179.py` fails closed if inventory or methods drift, if any test skips, or if any method fails. Execute in normal and `-OO` modes; CI gates are added to Ubuntu and Windows stages, but Actions runners may still fail before allocation. Local isolated tests require real copies of R178's `policy_canonical.py` and R178 tests, and must never be represented as full-repository or native Windows verification.

## Release/QD

Keep draft stacked on R178 rather than `main`. All six executables remain internal/unreleased; no premium binary or download exposed. Mandatory physical Windows 11 accessibility witness, Defender/EDR, signing, protected premium distribution, QD review, and founder release authorization are not bypassed. Next priority: restore Actions runner allocation, run full inherited tests plus seven R178 end-to-end integration cases and internal Windows packaging, then independent Windows 11 witness acceptance.
