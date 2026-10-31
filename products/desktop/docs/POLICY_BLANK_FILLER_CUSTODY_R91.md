# R91 — Policy Delta Desk blank-filler source custody

**DRAFT / RELEASE HOLD.** Offline text-diff display improvement, not legal interpretation, compliance approval, Windows executable release, or download authorization.

## Reproduced review gap

Policy Delta Desk already escaped control/format marks, Unicode non-ASCII spaces, CR, tabs, variation selectors and literal backslashes. However, seven visually blank non-control characters were missing from its source-line renderer, despite already being inventoried for premium financial review:

| Character | Codepoint | Unicode category |
| --- | --- | --- |
| Hangul Choseong Filler | U+115F | Lo |
| Hangul Jungseong Filler | U+1160 | Lo |
| Khmer Vowel Inherent AQ | U+17B4 | Mn |
| Khmer Vowel Inherent AA | U+17B5 | Mn |
| Braille Pattern Blank | U+2800 | So |
| Hangul Filler | U+3164 | Lo |
| Halfwidth Hangul Filler | U+FFA0 | Lo |

A source line with U+2800 between Approve and payment differs in source bytes from an ordinary ASCII space, but may appear equivalent in viewers. In the predecessor, the character still appeared as a blank glyph. R91 changes only the display of these seven glyphs to visible lowercase Unicode escapes. Example:

    -Approve\u2800payment
    +Approve payment

Literal source text containing a backslash followed by u2800 remains distinct: the existing backslash escaping displays a doubled backslash. The text report explicitly documents the escape convention. This is not a byte-exact patch format.

## Implementation and invariants

- The policy-diff module now consumes the existing, pure, shared unicode_hazards.is_visually_blank_filler predicate; no separate drifting Unicode list.
- Escaping covers removed, added and context source lines, not diff headers/hunk locations.
- Source SHA-256 fingerprints cover originally read bytes, before rendering; original files are never rewritten.
- No changes to TXT/MD/CSV acceptance, input size/line limits, local-only processing, atomic no-overwrite publication, or legacy CR/tab/backslash/variation escaping.
- No legal or compliance determination; human review remains mandatory.
- Narrow seven-character protection, NOT comprehensive Unicode confusable/spoof detection.

## Tests and limitations

The newly committed tests/test_policy_blank_filler_r91.py has **22 end-to-end unittest methods** using synthetic local files: seven fillers, ordinary-space and empty-codepoint differences, literal escapes, context/add/delete lines, hunk coordinates, unterminated lines, TXT/MD/CSV, SHA-256, originals preserved, Unicode, CR/tab/backslash, identical/BOM review, invalid control/UTF-8 rejection, immutable output, no partial files, 1,200 context lines, and deterministic output.

**Executed source-only Linux Python 3.13 preflight:** four source modules (policy_diff.py, unicode_hazards.py, csv_snapshot.py, atomic_text.py) were exact GitHub R90 blob copies before patching. Both updated policy_diff.py and the test module match their committed R91 Git blob SHA-1 values. Predecessor (red) run produced **26 failed assertions/subtests** across 22 methods. Corrected real-source run passed **22/22 normal** and **22/22 with python -OO**, and compileall succeeded. This was **not** a complete private-repository checkout; legacy suites and native Windows tests remain unexecuted.

**Release gates:** restore GitHub Actions runner allocation (#75); run full desktop suites normal/optimized and native Windows 11 x64 six-EXE packaging/installation/keyboard/screen-reader smoke; verify binaries/checksums/antivirus/protected premium entitlements and independent QD/founder approval. No site or premium download publication authorized.
