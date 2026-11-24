# R465 QA receipt — 2026-11-24
Read source commit 2f5657c53369ae5d00623ce0bf19e524f6c8dbb9 through GitHub:
- edition.txt blob 055608a79b2171e5eeab807d2f2930c2c6dce1fc
- edition.html blob 356ccccc0aa433238c523f164e7545135d63b771
- RELEASE_DOCKET.md blob 366abe9702651dff693431cb84b67b972358e721
- test_edition.cjs blob 231af49a594a45b4b6ae77fac9bc079dc74d0ed2

21/21 mirrored static V8 conditions passed against retrieved content, including language, viewport, single H1, one primary CTA plus two source links, tag parity, no script/form/remote image or merchant link, hard-stop legal placeholders and semantic table markup. All seven narrative paragraphs matched exactly across escaped HTML/plaintext. Three deliberate unsafe mutations (duplicate CTA, script, merchant URL) detected. Calculated nominal color contrast: CTA 11.97:1, body 15.70:1, source links 9.79:1. Subject 42 chars, proposed preheader 75 chars, narrative 256 words. No real browser/mobile/client or assistive technology test, no native Jetpack Preview or received email. Portable Node test committed but not natively executed. Original #175 immutable head d57ccdba3aee8f065e143e101c2945f4f3d01647: six conditions mirrored independently in V8, 6/6 PASS; native Python exact-head execution was already reported in R464, not repeated today due to container GitHub DNS failure. No invented production metrics.

Signed-out WP server-render summary gave 200 for both tagged and canonical Utsuro article URL with same canonical, publicly visible. QA request not a human click. Analytics ingestion, redirect behavior in actual clients, and signups remain unverified. No email or test email, no WordPress changes, no merchant activation, no account or expense, no merge. HOLD UNSENT.
