# R149 — Policy Delta Unicode normalization and combining-mark evidence (DRAFT / HOLD)

## Problem and fix

A policy can change from precomposed é (U+00E9) to e plus combining accent U+0301 without an obvious visual change. Reviewers need exact codepoint evidence, not a claim of legal equivalence.

- Policy Delta now displays all Unicode nonspacing (Mn) and enclosing (Me) combining marks as explicit U+XXXX or U+XXXXXXXX escape sequences in diff source lines, including unchanged context. Literal backslashes are escaped first, so source text that merely spells an escape cannot masquerade as a combining mark.
- When source codepoint sequences differ but NFC normalization yields the same text, the report emits a generic review-only normalization-equivalence notice. It never declares legal, regulatory, financial or semantic equivalence.
- BOM-only and CRLF-only revisions do not receive an NFC notice. NFKC compatibility-equivalent content (e.g. fullwidth A versus ASCII A) is NOT labeled canonically equivalent.
- Ordinary letters, emoji, visible spacing marks (Mc), and ASCII spaces remain readable. Display escaping is non-patch notation; the original files and exact SHA-256 hashes remain authoritative.
- Diff hunk coordinates, the physical-line change index, source fingerprints, stable snapshot reads, atomic no-overwrite publication, offline operation, private-path redaction and invalid-control rejection remain intact. Premium engines and access controls are untouched.

## Illustrative synthetic evidence

Before has precomposed Café; after has Cafe followed by U+0301. In the report, the changed lines are visibly different: removed precomposed Café; added Cafe followed by escaped U+0301. The line citation remains before L1 / after L1. The report also displays a generic NFC-equivalence REVIEW notice and original source hashes.

## Validation

- Code: products/desktop/fvs_suite/policy_diff.py.
- End-to-end synthetic tests: products/desktop/tests/test_policy_normalization_evidence_r149.py — 30 distinct methods for canonical composition/reordering, multilingual and supplementary combining marks, literal escapes, ordinary letters and Mc, source hunk positions, exact SHA, unchanged original files, deterministic output, no-overwrite, invalid UTF-8 and bidi rejection, private paths, BOM and line endings.
- Exact-inventory zero-skip private runner: products/desktop/scripts/safe_unittest_r149.py.
- CI: 30 methods x two Python modes (normal and -OO) x two runner OSes (Ubuntu and Windows) = 120 required targeted method executions, in addition to inherited source/smoke/native x64/sealed premium gates. Check exact commit job outcomes before claiming PASS.

## Unreleased / independent approval

Stacked draft feature PR only; never merge to main without the site's QD workflow. CI and synthetic observations do not substitute for 46 independent physical Windows 11 accessibility checks, real Defender/EDR, code signing, authenticated premium distribution, independent QD review and founder release authorization. All six apps remain UNRELEASED. No binaries or premium files may be published.
