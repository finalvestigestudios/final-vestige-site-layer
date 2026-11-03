# EX2: full-source Assembler front-end rendering admission — RELEASE HOLD

Date: 2026-11-03. New isolated draft stacked on PR #816 exact head `f211c47aa992444356e7341cee9bc95b1dcd3b10`. Frozen PR #49, production WordPress page 6, Apollo #158 and Mind #171 are untouched.

## Gap closed in source, pending execution evidence

PR #816 proves real Gutenberg editor byte-exact Save for 120,064 bytes of source-controlled seven-chapter markup, but **not front-end theme rendering**. This PR provides a testable path to that missing gate. Reuse the existing synthetic-only owned-draft bridge and its required HMAC/cleanup checks. After the browser editor Save is verified, mount the **free official Assembler theme ZIP** into that same ephemeral WordPress Playground instance, activate `assembler` and verify the active theme, preview the **same saved disposable draft** through WordPress, then exercise real Chromium.

The new workflow downloads Assembler from `https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip` into a throwaway GitHub runner; it validates ZIP traversal, symlinks and size, prints the archive SHA-256, reads the actual theme version, and removes the ZIP and extracted files. **The download is not immutable/pinned**, and even a matching version would not recreate WordPress.com's live templates, global styles or CDN/Jetpack behavior. Do not overclaim host parity.

## New gate / explicit pass conditions

- Exact-source `write_source_flagship_playground_candidate.py` still loads the **actual 11 Git-controlled seven-chapter files** and **synthetic-only** 72 Margins + Jetpack fixtures. No actual private page-6 source, subscriber records, production DB/settings, credentials or cookies enter the repository or artifacts.
- The existing real editor gate requires SHA-identical stored content and mandatory owned-draft deletion in `finally`; failure of the new render checks cannot bypass cleanup.
- Render preview with Assembler theme at CSS widths **320, 390, 768, 1440, 1920**. Assert all **seven** chapter anchors/targets, **72** Margins elements, Focus references, HTML headings, four source scripts and no horizontal overflow.
- Inject real `axe-core` (not a stub) for the WCAG 2/2.1/2.2 A/AA tag set at each width; fail closed on any reported violation or unavailable axe.
- Fetch referenced first-party archival image **response bodies**, checking HTTP 200, image MIME, positive byte sizes and SHA-256. Screenshots at 390 and 1440 may be retained for three days; **no HTML source, auth, database or live subscribers** are uploaded.
- Check a 720 CSS-pixel / 450 height viewport as an **approximation** to desktop 200% zoom; this is **not** true manual browser zoom parity. Check 390px no-JavaScript document for 7 chapters, 72 Margins and a meaningful H1.
- Prevent test browser from contacting production administration, affiliate destinations or analytics; permit loopback plus public source media hosts only. Record blocked hostnames.
- WordPress is never allowed to publish the candidate; the source SHA-256 and all 9 original editor checks must pass before rendering begins. Retain release HOLD independent of CI result.

## How to reproduce

From this draft exact checkout run `.github/workflows/ex2-assembler-front-render-HOLD.yml`. The pinned runtime packages are `@wp-playground/cli@3.1.56`, `playwright@1.56.1` and `axe-core@4.10.3`. CI must finish and supply actual exact-head receipts before claiming any visual, theme, accessibility or media pass. The workflow writes screenshots of the **synthetic source-controlled study only**; an axe failure correctly FAILS the gate, not the site. If the official Assembler ZIP differs from the site's active v0.0.126, record the mismatch as an explicit qualification gap.

## Known scope limits / independent release gates

A CI pass would certify only this isolated test. It is **not** an actual WordPress.com Personal hosted clone, exact page-6 render, a Jetpack subscription interaction, manually verified WCAG 2.2 AA, physical-device Safari/touch/200% zoom, accurate LCP/INP/CLS, full rights clearance, or independent QD. Preserve all 72 real published Margins, the 52-page Focus Fieldbook and original Jetpack signup at future integration. The NYPL Malbone capture remains withheld pending image-specific reuse clearance; its museum catalog links stay.

**NO release:** No WordPress production edits, new subscriptions, plugin installs, merge or deployment until the founder explicitly authorizes and independent gates pass. Maintain all three existing art directions pending founder choice. Do not modify frozen PR #49.
