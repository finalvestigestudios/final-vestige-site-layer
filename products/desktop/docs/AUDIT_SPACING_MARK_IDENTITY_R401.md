# R401 — Spacing-mark source identity evidence (2026-11-13)

**Scope:** issue #73, human-display layer shared across Final Vestige Labs. **Draft / QD + founder HARD HOLD.** No binary, entitlement, download, production branch, source CSV or compliance disposition changes.

## Reproduced gap

R400 made nonspacing/enclosing Unicode combining marks (Mn/Me) explicit for source identity labels, but left **spacing combining marks (Mc)** as rendered glyphs. Some canonical Unicode spellings differ exclusively in Mc codepoints. Synthetic Bengali examples:

| Source codepoints | NFC-equivalent? | Before R401 identity display | R401 identity display |
| --- | --- | --- | --- |
| U+0995 U+09CB | yes | কো | ক\u09CB |
| U+0995 U+09C7 U+09BE | yes | কো (visually equivalent) | ক\u09C7\u09BE |

The issue concerns **human-readable evidence**, not matching scores or equality. Source originals and provenance remain authoritative; these audit labels are a display-only transformation.

## Implementation

- In products/desktop/fvs_suite/audit_display.py, visible_source_text(reveal_combining=True) reveals Unicode mark categories Mn, Mc, Me as uppercase \uXXXX (or \UXXXXXXXX) escapes.
- visible_identity_label, visible_source_label_list and premium visible_review_row inherit the change without changing source matching, financial calculations, review decisions, or journal persistence.
- **Crucial compatibility:** the default visible_source_text(reveal_combining=False) still renders ordinary multilingual prose unchanged; ordinary flags/notes remain readable.
- Synthetic regression inputs include canonical Bengali, Odia and Tamil pairs, Devanagari and Myanmar Mc, mixed mark categories, literal escapes, separators, raw input immutability, list ordering, premium queue references and nonnative type rejection.
- Independent source-evidence workflow now invokes the new test file in standard and optimized Python on both OS matrix entries, **when runners become available**.

## Locally executed evidence

Prepatch exact-code reproduction: **13/24 R401 test methods failed** as expected on the original R400 renderer (display deficiency).

Postpatch local Linux CPython 3.13.5:
- Standard Python -W error: **24/24 PASS**.
- Optimized Python -OO -W error: **24/24 PASS**.
- python -m py_compile on renderer, shared Unicode helper and test: **PASS**.
- Exact committed Git *blob* identity was verified against the two executed local files:
  - Renderer 60e08fd12cfbc0e8825f50a22bbfd5a606982f3b
  - Tests 30715b194bafc6065cccc76fdbfe0b78464df341
- Unchanged dependency was locally reconstructed from the R400 GitHub file. **This was not a complete repository checkout**; it does not validate six-engine integration or native Windows.

## Limitations and hold

- Unicode Mc escapes make identity text more technical, including some naturally written non-Latin identifiers. Reviewers must be able to consult original source values. Do not replace stored source strings or assume a marked label proves fraud.
- This is **not** a general cross-script confusable detector or Unicode spoofing solution.
- Hosted Ubuntu/Windows Actions jobs from R400 recorded **no executed steps**, and earlier CI likewise failed before runner allocation. Exact infrastructure cause remains unconfirmed. R401 CI must not be counted as passing until GitHub records executions.
- Full inherited R81/R97/R399/R400 tests and complete financial, Decimal, source-provenance, AES-GCM, Ed25519, SQLite and packaging suites remain unverified for this new exact head.
- No public executable or premium distribution is authorized.

## Next highest-impact step

Restore hosted runner allocation (inspect failed-job annotations, Actions spend/billing settings and runner eligibility); rerun this exact SHA's independent Windows/Ubuntu source workflow and desktop-build workflow; verify the full inherited six-app financial/cryptographic suite; then perform genuine Windows x64 binary, Defender, keyboard/screen-reader QA and **premium gated-download** acceptance. Independent QD review and founder approval must precede any merge, release or website change.
