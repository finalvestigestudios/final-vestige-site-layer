# R81 — Premium source-reference display integrity (pre-release)

## Problem

GrantAudit Studio Pro and ProcureGuard Studio Pro verified the report/journal bytes, but their review Treeview showed raw imported source keys and flags. Register CSV export also included these strings. A field with U+202E (right-to-left override), U+200B (zero-width space), U+2029 (paragraph separator), variation selectors or a nonbreaking space could mislead reviewers while the source hash was valid.

## Correction

The pure offline audit_display.visible_source_text escapes ASCII/C1 controls, Unicode format and directional controls, surrogate, private-use and unassigned characters, line/paragraph separators, non-ASCII spaces, combining grapheme joiner, Mongolian and standard/supplementary variation selectors. Literal backslashes are doubled so the actual U+202E control rendered as \u202E differs from literal source text \u202E rendered as \\u202E. Supplementary codepoints use \UXXXXXXXX. Ordinary ASCII spaces, readable multilingual text and combining accents remain unchanged.

The premium review Treeview uses visible_review_row; register source_key and original_flags cells now use visible_source_text. These **display columns are not byte-for-byte raw data**; inspect the original report with its SHA-256 for exact source. Original input bytes, raw source cases and flags in verified journal events, case identifiers, physical row references, immutable source hashes, human decisions, reviewer identities, timestamps, CSV injection handling and Decimal arithmetic are unchanged. This is not a universal confusable detector or a payment/compliance approval. Older exports are not rewritten.

## Verify on full checkout

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_audit_display_r81.py' -v
    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_register_render_r81.py' -v
    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_source_visibility_integration_r81.py' -v
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -v

Twenty-four isolated Linux boundary/consumer tests passed locally (20 pure display; four register tests with **stub** atomic CSV writer and snapshot verification). Five additional committed integration regressions still require full repository source and authentic atomic writing. Native Windows GUI, complete source CI, AV/signing/installation, premium entitlement and distribution remain unverified.

## Release gate

Stacked draft branch only. No production/main changes or executables published. All six products unreleased. Restore GitHub Actions runners (incident #75), run source and actual Windows 11 x64 tests, then independent QD and founder approval. This release gate cannot be waived by isolated source tests.
