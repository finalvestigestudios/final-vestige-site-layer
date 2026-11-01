# Isolated WordPress staging: public-input acquisition custody (Nov 1, 2026)

**Draft / release HOLD. Not WordPress execution, production deployment, or licensing approval.**

## Concrete integration gap closed
The existing offline Playground bundle builder requires four local source files but has no safe, repeatable acquisition path. This new read-only collector retrieves the *public* Automattic Assembler theme download and three public first-party image originals referenced by the source-controlled 19-step Blueprint. Nothing is fetched from private CMS APIs, and no WordPress site is written.

`python acquire_private_stage_inputs.py --private-dir /ABSOLUTE/MODE_700_PRIVATE_WORKSPACE`

The command creates a **new**, non-overwriting `fv-source-quarantine/` folder with `assembler.zip`, `media/apollo.webp`, `media/franklin.jpg`, `media/nypl.jpg`, and `UNREVIEWED_SOURCE_CANDIDATES.json`. All files are mode 0600; parent/media folders mode 0700. Output contains SHA-256 digests, byte lengths and explicit `UNREVIEWED_CANDIDATES_NOT_RELEASE_ADMITTED` status.

Sources are fixed constants already used by `launch_integrated_staging.py`, including official `https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip`. HTTPS and expected hosts only; reject redirects, HTML/error response bodies, wrong MIME, truncated files, oversized downloads and unexpected image signatures. Validate every theme ZIP member using the existing strict Assembler archive parser, but **DO NOT** treat the same-transfer SHA as independent approval.

## Independent review gates that remain OPEN
- A second, independent reviewer must establish file provenance, approved SHA-256 and **item-specific reproduction rights**; the collection receipt is **not** a valid `check_manifest` media approval and cannot be passed straight into `make_offline_private_bundle.py`.
- Verify actual WordPress.com Assembler version against collected package; GPL theme availability does not certify deployment equivalence.
- The original media bytes and source permission are distinct issues. Apollo / Franklin / NYPL each require reviewed source identity, attribution and permitted use.
- Existing Blueprint, Gutenberg 72 Margins, 52-page Focus Fieldbook link(s), original Jetpack block, 7 chapters, and no-JS fallback must pass private isolated WordPress/Assembler/Chromium/axe/Lighthouse. This collector does none of that.
- WordPress.com Personal cannot create native hosted staging; free Playground remains a **developer approximation**, not Jetpack or p75 field CWV certification.
- No approval to merge/deploy/publish, no change to frozen PR #49 or production page 6, and no change to Apollo #158 or Mind #171.

## Executed evidence and environment limits
On Nov 1, 2026, a networkless local Linux executor ran **11/11 offline synthetic tests** (successful mode-0600 quarantine, four fixed URLs, rewrite refusal, byte count, MIME, bad status, redirect, unsafe host, oversized ZIP, corrupt ZIP, permissions, no partial output on failure). The local executor cannot DNS-resolve github.com or wordpress.org, so real source transfer **was not executed**; no actual archival-image SHA, actual Theme ZIP hash, licensing verdict or WordPress render is claimed.

Official references: WordPress.com Assembler public theme page; Automattic's archived GPL theme source; WordPress Playground's Blueprint Bundle and CLI guides. Use the downloaded official version for source review, not the archived development copy as proof of current WP.com deployment.

**Next action on a network-enabled approved developer machine:** run collector into a fresh private directory, independently review fingerprints and reproduction rights, then build the existing sealed bundle and run the genuine native WordPress/Assembler acceptance path. Preserve the no-CMS-write/no-release gate.
