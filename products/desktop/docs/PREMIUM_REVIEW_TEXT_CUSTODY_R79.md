# R79 — Premium human-review text custody (draft, not released)

Scope: GrantAudit Studio Pro and ProcureGuard Studio Pro only. This is an
engineering change stacked on R78, not an approved installer, compliance
determination, payment authorization, or request to publish premium files.

## Defect

Reviewer identities and rationale fields were checked against C0 ASCII
controls (U+0000–U+001F and DEL) but still admitted Unicode bidirectional
overrides/isolates, C1 controls, format characters, embedded Unicode
paragraph/line separators, UTF-16 surrogate codepoints, and zero-width
variation selectors. These could make a journal or spreadsheet display
different from the characters that were actually hash-chained, even when a
reviewer was required to supply a name and an explanation.

An audit record may carry a valid **unkeyed** SHA-256 event chain and still
contain misleading display text. A hash chain is not a signature or a
human attestation.

## Implemented boundary

The shared `exception_review._text` validator now rejects:

- Unicode categories Cc (including C1), Cf (including bidi override/isolate
  and zero-width formatting), Cs (surrogates), Zl and Zp.
- Combining Grapheme Joiner U+034F, Mongolian variation selectors
  U+180B–U+180F, basic variation selectors U+FE00–U+FE0F and supplementary
  variation selectors U+E0100–U+E01EF.

This validation is applied before every new human action writes/locks a
journal and on every event loaded from an existing review journal. Invalid
existing data fails closed, including records where someone has recomputed
the unkeyed SHA-256 hash. Neither the report nor the journal is silently
rewritten, normalized, or migrated.

Ordinary multilingual letters, readable punctuation, decomposed combining
accents (apart from CGJ/variation selectors), and internal spaces remain
accepted; approved text is preserved byte-for-byte after existing outer
whitespace trimming. The previous length limits and human-only decisions
remain unchanged.

**Compatibility:** a legacy review journal containing disallowed Unicode
will now require human investigation/archival; do not automatically strip,
reinterpret, rehash, or "repair" a prior signed-looking record. Source
documents and untrusted review files are never uploaded. This is not a
comprehensive Unicode confusable or identity-verification defense.
Conservative refusal can affect legitimate formatting such as ZWJ emoji or
some scripts. A reviewer should enter a plain-text explanation rather than
using invisible formatting; exceptions require a separately reviewed product
decision, not a silent bypass.

## Regression acceptance

Synthetic, offline `tests/test_review_unicode_custody_r79.py` covers 16 test methods,
including a matrix of 20 invisible/control characters in both reviewer and
rationale fields, legal multilingual examples, category boundaries,
source-file preservation, both premium human-review append paths, and
hash-valid tampered review journals that must fail closed for both products.
No real customer or beneficiary information is used.

From repository root (when the full checkout is available):

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_unicode_custody_r79.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_review_unicode_custody_r79.py' -v
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -v
python -m compileall -q products/desktop/fvs_suite/exception_review.py products/desktop/tests/test_review_unicode_custody_r79.py
```

Local isolated verification (if performed) is narrower than a complete
repository run. Actual Windows 11 x64 executables, packaged smoke, screen
readers, AV, premium entitlement, and release-gate integrity must all be
separately verified. CI runner allocation failure is tracked in issue #75.

Do not merge stacked drafts to main or change the published website without
independent QD and founder approval; premium binaries must remain gated.
