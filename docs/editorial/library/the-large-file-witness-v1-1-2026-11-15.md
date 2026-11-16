# The Large File Witness v1.1 — collection-level integrity companion

**Owner:** Final Vestige Studios Library Resource Studio  
**Date:** November 15, 2026 Pacific  
**Public status:** HOLD; WordPress Library draft #2393 (*The Copy You Can Check*) remains unpublished/no new Library card.

## Why this sprint
Continued [issue #1971](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1971) rather than making another draft. Earlier offline v1.0 could hash large source files in 2 MiB chunks and compare filenames, sizes, SHA-256. But a selected-file receipt does not reveal an additional unlisted file in the directory. v1.1 introduces explicit `selected-files` versus `complete-folder` scope: a complete-folder receipt also detects added files and symlinks on subsequent verification. Selected-file receipts can opt into `--check-extras`. The old `fv-fixity-ledger/1.0` schema remains readable.

## Provenance + scope
Reference pages retrieved Nov 15:
- [NIST FIPS 180-4](https://csrc.nist.gov/pubs/fips/180-4/upd1/final), published August 2015: basis for SHA-256.
- [NDSA Levels of Digital Preservation](https://www.ndsa.org/publications/levels-of-digital-preservation/), v2.1 March 2026: preservation context.
- [NARA Digital Preservation](https://www.archives.gov/preservation/digital-preservation), page last reviewed Oct 29 2026.
- [LOC Personal Digital Records](https://digitalpreservation.gov/personalarchiving/records.html): independent copies and version retention.
- Related studio [What Survives](https://finalvestige.com/what-survives/) and [The Page That Changed](https://finalvestige.com/free-resources/the-page-that-changed/).
All software, synthetic sample and graphics are original. No government scans, photos, matrices, institutional seals or third-party artwork were reproduced. Item-specific rights remain unverified for any future user-supplied archival object.

## Direct verification
- Standard-library Python regression suite: **20/20 passed** on Linux Python 3.13. Includes SHA-256 known-answer, full/single scope, extra file detection, changed/missing/symlink, Unicode paths, 3 MiB streaming, path traversal/duplicate/overwrite rejection, invalid receipt and old-schema compatibility.
- Synthetic sample: complete-folder receipt MATCH, then adding an unlisted file produced UNEXPECTED and return code 2.
- Original standalone HTML guide: local Chromium via Playwright, 320/390/768/1440 px, JS on/off: **8/8** no whole-page overflow, one H1, SVG descriptive title, source ledger visible; 390/1440 screenshots visually examined.
- WordPress draft #2393: optimistic-lock appendix created exactly one scoped supplementary core/html section with ID `FV-LARGE-FILE-WITNESS-V11-20261115`; authenticated readback verified original first-block SHA-1 unchanged `6819e83cbc407f5787992624152ac988942b0b10`, second section added once, status still draft. No public link to an unhosted tool was added.

## Delivery
Complete self-contained v1.1 Python source, 20 tests, HTML, sample receipts, dated rights/source ledger, desktop/mobile screenshot evidence, QA and checksum files are delivered in the corresponding Library Studio conversation ZIP `FV_Library_Large_File_Witness_v1-1_20261115_HOLD.zip`. Local conversation attachment is not a public WordPress URL and a GitHub issue alone does not establish anonymous download.

## Release HOLD
- Need actual production-theme readable screenshots and keyboard/screen-reader QA (local Chromium != production).
- Need anonymous source/guide download hosting and verification.
- Need enforceable first-publication Jetpack suppression `_jetpack_dont_email_post_to_subs=true`; WordPress connected publishing action does not expose it.
- No Windows/macOS runtime validation yet.
No public WordPress content/navigation, subscriber emails, spending, Grok accounts, Preparedness, Investigations, or homepage engineering changed. This is an integrity tool, **not** a forensic proof of historical authenticity, record completeness, copyright or custody.
