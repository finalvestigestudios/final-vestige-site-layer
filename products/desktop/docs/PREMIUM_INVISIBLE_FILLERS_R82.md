# R82 — Invisible filler custody for premium financial reviews (source-only)

## Threat and reproduced gap

A small set of Unicode **non-control** glyphs commonly renders blank or near-blank. The earlier category-based guard escaped/rejected Cc/Cf and selected format characters, but missed U+115F, U+1160, U+17B4, U+17B5, U+2800, U+3164 and U+FFA0 because their categories are Lo, Mn and So. A record identifier or human reviewer identity could differ without an obvious visual indication.

## Change

The shared offline `unicode_hazards.is_visually_blank_filler` predicate enumerates these **seven** glyphs. `audit_display.visible_source_text` now renders them as explicit `\\uXXXX` sequences in the premium review table and human-readable CSV register, preserving the raw report, source SHA-256, physical row references, journal events and case keys. Literal source backslashes remain doubled, preventing the rendered escape from impersonating an actual raw escape sequence.

`exception_review._unsafe_review_character` now rejects these glyphs in **new reviewer names and rationales**, and while validating **existing journal events**, for both GrantAudit Studio Pro and ProcureGuard Studio Pro. A previously accepted journal with such text may now fail verification: retain the originals, investigate the identity, and resolve the record through a documented human procedure. **Never manually alter a hash-linked journal or auto-migrate its history.** Normal multilingual text, combining accents, ASCII spaces and previously allowed non-ASCII spaces are otherwise unchanged.

This is a narrow visual-ambiguity safeguard, **not** comprehensive Unicode confusable detection, a fraud finding, legal interpretation, payment approval, code signing, or an encryption entitlement.

## Test commands on full checkout

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_unicode_fillers_r82.py' -v
    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_filler_integration_r82.py' -v
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -v

R82 source-only local test evidence must be reported separately from complete checkout integration or Windows 11 x64 EXE evidence. Run independent QD and founder release approval after CI, packaging, malware scanning, checksum verification and premium entitlement/distribution checks. Never publish premium binaries or untested downloads.
