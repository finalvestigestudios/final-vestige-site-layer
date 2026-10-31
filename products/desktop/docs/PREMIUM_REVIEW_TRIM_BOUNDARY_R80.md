# R80 — Premium raw-review text boundary (draft, unreleased)

**Scope:** the shared human-review journal boundary for GrantAudit Studio Pro and ProcureGuard Studio Pro, stacked on R79.

## Defect and correction

R79 correctly rejected hidden/control Unicode in a field **after** outer whitespace trimming. Python `str.strip()` silently removes several controls when they occur at the beginning or end of a submitted string, including LF, CR, tab, vertical tab, form feed, C1 next-line and Unicode line/paragraph separators. An input such as `"Human Reviewer\\n"` could be accepted as `"Human Reviewer"` without alerting its author. A hash-valid journal constructed with such untrimmed raw values could also bypass R79's historical validation.

R80 checks **every code point of the original submitted/stored value before calling `strip()`**. Whitespace-only padding that contains no forbidden characters still follows the previous trimming and length rules; accepted multilingual text remains unchanged. No event is silently rewritten or rehashed, and a rejected pre-existing record requires separate manual investigation. Rejecting unsafe boundary controls is not identity proof or a cryptographic signature.

## Tests and limitations

`tests/test_review_trim_boundary_r80.py` has 14 test methods, including a 9-character matrix at both boundaries of reviewer and rationale fields, internal controls, controls surrounded by ordinary spaces, permitted multilingual text, privacy-safe errors, two actual premium append paths, and rehashed journal tampering followed by register-export refusal.

Run against a complete checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_trim_boundary_r80.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_review_trim_boundary_r80.py' -v
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -v
```

The isolated pure-validator checks can be run without all application dependencies but do not prove the end-to-end tests, Windows GUI binaries, AV/entitlement/release gates or QD approval. Processing remains local-first, deterministic and human-reviewed. Do not publish premium binaries or alter production.
