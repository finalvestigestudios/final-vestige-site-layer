# Invoice Twin Scout — R134 local review-window configuration

**Status:** DRAFT; NOT A RELEASE. Tracked under [Issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R133 without changing production or any QD approval requirement.

## What a reviewer can do
Import a local invoice CSV as before. Invoice Twin Scout now shows a keyboard-focusable **Near-match days (0-365)** field, default **7**. Enter an integer and select **Generate review report**. The setting applies to same-vendor, same-amount invoices with **different** normalized invoice keys, which are candidates only if their calendar dates differ by at most the chosen number of days (inclusive). An exact normalized vendor + invoice-number match is **always** reported, regardless of dates and configured window. Exact matches outside the configured window receive a **distant_dates_review** flag, not a fraud determination.

| Setting | Meaning |
| --- | --- |
| 0 | Same-day near matches only |
| 7 (default) | Previous seven-day near-match behavior |
| 14 | Expanded manual review |
| 365 | Maximum permitted span |

The CSV includes **review_window_days** on every finding, plus unchanged actual physical source lines, imported-byte SHA-256, candidate reference and explicit review flags. For an empty report the header still includes all provenance fields. The candidate reference remains a stable locator for source rows and status, *not* proof of reviewer choice; compare **review_window_days** whenever two reports use different settings. Do not treat a flag, missing candidate or unmatched window as a legal, fraud, payment or compliance conclusion.

## Safety and regression evidence
The GUI accepts only ASCII whole numbers 0 through 365 (after trimming whitespace). Minus signs, scientific notation, floating values, Unicode digits and out-of-range numbers are rejected without writing a partial report or echoing private text. The engine independently rejects non-integer, boolean, out-of-range window arguments. Existing 200k-row / 100k-candidate limits remain; invoices/amounts use bounded Decimal math. The application never uploads source data or changes originals. Neither premium product is modified or unlocked.

CI runs **16 named integration and contract tests** in normal and `-OO` Python on **Linux and Windows** (target 64 executed tests), plus inherited full source tests and six private Windows EXE smoke/integrity, four-free/two-premium lock checks, R106 keyboard focus, R107 native 200%/400% scale scroll/focus, and R108 actual Tk accelerator/cancel safety. CI status must be verified against the exact final SHA; local headless tests alone do not establish real Windows compatibility.

## Release gates still outstanding
Physical Windows 11 independent custody of all six binaries; all 46 hands-on accessibility witness checks; real Defender/EDR assessment; code signing; protected premium payment/download/entitlement distribution; independent QD and founder approval. No publicly downloadable EXE, premium file, private evidence payload, production code, or site editorial content is published by R134.
