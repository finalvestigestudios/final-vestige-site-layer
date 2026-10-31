# Labs R77 — Policy Delta Desk invisible Unicode evidence display

**Draft engineering increment, not a release or legal interpretation.** This
change is stacked on R76. QD and founder approvals remain mandatory.

## Why this matters

R76 made tabs, carriage returns and literal backslashes unambiguous in Policy
Delta Desk reports. Some otherwise permitted Unicode format characters are
invisible in most text viewers (for example U+200B ZERO WIDTH SPACE, U+200C
ZERO WIDTH NON-JOINER, U+200D ZERO WIDTH JOINER, U+00AD SOFT HYPHEN and U+2060
WORD JOINER). Unicode variation selectors can also silently change glyph
presentation. A removed or added source character could therefore appear
visually identical to the reviewer even though the diff and SHA-256 differ.

## Behavior and boundaries

Source lines (added, removed and context) render the following characters as
ASCII escapes: Unicode category `Cf`, U+034F (combining grapheme joiner),
U+180B–U+180F (Mongolian variation selectors), U+FE00–U+FE0F and
U+E0100–U+E01EF (variation selectors). BMP characters display as `\\uXXXX`;
supplementary ones as `\\UXXXXXXXX`, with lowercase hexadecimal digits.
Literal source backslashes are doubled before displayed escapes so a source
containing the six literal characters `\\u200b` cannot impersonate U+200B.

All other allowed Unicode text stays readable. Source tabs and CR keep R76's
`\\t` and `\\r` notation. Original raw source bytes, SHA-256 fingerprints,
source order, diff hunk coordinates, line endings and no-final-newline markers
are preserved. The displayed report is **not** a machine-applicable patch.
Previously rejected ANSI/terminal controls and bidi override characters remain
rejected *before publication*. The renderer neither changes source files nor
makes legal/compliance decisions.

This is a deliberately scoped mitigation, **not a claim to detect all Unicode
confusables or all default-ignorable code points**. Human reviewers must
consult source documents and original-byte fingerprints when authenticity is
material. No automatic approval, policy interpretation or payment action.

## Test evidence and outstanding gates

Tests use real local read-once file snapshots and atomic report publication
with synthetic TXT inputs. Coverage includes Unicode `Cf`, BMP/supplementary
variation selectors, literal escape collision prevention, context lines,
headers/hunks, CR/tab compatibility, exact SHA-256, no-overwrite and input
rejection. The packaged Policy Delta smoke fixture adds invariants 49–51.

Local isolated harness: Python 3.13.5 on Linux, `python -W error` and
`python -OO -W error` focused unittest discovery, plus compilation. **These do
not prove full-checkout CI or real Windows EXE behavior.** The upstream GitHub
Actions runner-start issue #75 blocks native build validation. Next: restore
runner allocation, run normal and `-OO` full test suites, six real Windows x64
packaged smoke tests, Windows GUI accessibility, independent QD and founder
review. Do not distribute unsigned/unverified binaries or expose premium files.
