# The Large File Witness — offline streaming SHA-256 companion

**Library Resource Studio; 2026-11-15 (Pacific); PUBLICATION HOLD.**

## Duplicate check and ownership
Existing WordPress Library draft [The Copy You Can Check #2393](https://finalvestige.com/wp-admin/post.php?post=2393&action=edit) already owns the browser-based file-fixity explanation and 100 MiB WebCrypto workbench. Existing coordination [issue #1971](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1971). This is **not another competing WordPress page**. The new self-contained original companion adds an offline, no-dependency Python 3.10+ streaming checksum receipt and verifier for larger files and repeatable catalog-scoped verification. Read-only WP check: draft/noindex, parent #77, modified 2026-11-14T17:40:44. No WP write.

## Completed user-facing asset
- `fv_fixity_ledger.py`: `create`, `verify`, `selftest`, 2 MiB streaming chunks, 64-character SHA-256 digests, byte lengths, institutional ID/custodian/source URL/acquisition date/rights note, JSON manifest; MATCH/CHANGED/UNAVAILABLE and nonzero failure exit. Rejects path traversal, symlink inputs, malformed manifests and overwrite of existing receipt.
- `the-large-file-witness.html`: original illustrated static research guide, rights table, four-pass method, copyable commands, FV crosslinks, labeled fictional-example commands; original accessible SVG diagram only.
- Source/provenance-rights ledger, synthetic demonstration and generated receipt, regression suite, local responsive screenshots, checksums and release package delivered as conversation artifacts.

## Test evidence — local, not live site
- Standard-library unittest: **13/13 passed**; includes a 12 MiB streaming fixture, tampering, Unicode filename, missing file, path safety and overwrite guard.
- Illustrative synthetic file create → verify: **MATCH**. Not historical evidence.
- Offline Chromium 320 / 390 / 768 / 1440 × JavaScript on/off: **8/8 local layout checks** passed without page-wide horizontal overflow, console errors; one H1; descriptive SVG title/desc. Screenshots visually checked; local only.
- Native Web Crypto from the existing WP tool is **NOT verified**: Chromium blocked localhost/secure-origin navigation with ERR_BLOCKED_BY_ADMINISTRATOR. Python companion doesn't need Web Crypto.
- WordPress screenshot service supplied URLs, **not inspectable pixels**. Production-theme visual/keyboard/accessibility and anonymous companion delivery are NOT passed.

## Official sources / item rights (2026-11-15 checked)
1. [NIST FIPS 180-4 (2015)](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) — digest specification; detects changed messages, not authenticity.
2. [NDSA Levels v2.1 (March 2026)](https://www.ndsa.org/publications/levels-of-digital-preservation/) — archival preservation framework.
3. [NARA Digital Preservation](https://www.archives.gov/preservation/digital-preservation) — page last reviewed 2026-10-29.
4. [Library of Congress personal digital records](https://digitalpreservation.gov/personalarchiving/records.html) — versions, organized copies, stewardship.
FV crosslinks verified: [What Survives](https://finalvestige.com/what-survives/), [The Page That Changed](https://finalvestige.com/free-resources/the-page-that-changed/), [Research Sources](https://finalvestige.com/free-resources/research-sources/). Rights: **links only**; no institutional photograph, seal, scan, or artwork copied. Original code/diagram/fictional demo only.

## Release conditions
**HOLD.** No live WordPress, navigation, subscribers, Grok, Preparedness, Investigations or homepage edits. Before first public release, verify real theme 320/390/768/1440 screenshots/keyboard/accessibility, anonymous asset hosting, all external links, metadata/readback, and **explicit** `_jetpack_dont_email_post_to_subs=true` plus social-publicize suppression. The connected authoring tools do not expose this first-publish safeguard; default newsletter off is insufficient. Linux Python tests passed; other OS remain untested. After publication Grok could consider “Same filename. Same file?” video, but no account action was taken.
