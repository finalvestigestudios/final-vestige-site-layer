# Private offline WordPress Playground bundle — Experience 2.0 (2026-11-01)

**Review-only companion to PR #451 (exact parent SHA `0a8af90a31d6acd80875d341fb9a7742117ed97d`). NOT a WordPress or WCAG release pass.** Frozen #49 and production page ID 6 are untouched.

## Why this is necessary
The existing 19-step private Playground Blueprint downloads the Assembler theme and Apollo/Franklin/NYPL files at *execution time*. In restricted or offline developer environments, this fails even when WordPress/Playground is available. Official WordPress Playground supports ZIP **Blueprint bundles** with `{"resource":"bundled","path":"/..."}`, eliminating all four live theme/media requests during Blueprint execution. Reference: https://developer.wordpress.org/playground/blueprints/bundles/ and https://wordpress.github.io/wordpress-playground/tl/blueprints/steps/resources/.

## What this adds
`make_offline_private_bundle.py` reads the exact source-pinned **integrated** Gutenberg Blueprint accepted by PR #451's existing `check_blueprint`; it also invokes the original PR #451 `check_manifest`. It requires an independently reviewed SHA-256 for the official Assembler ZIP and the three original public archival image files, checks ZIP paths/structure and image signatures, then produces a private deterministic ZIP containing ONLY `blueprint.json`, `assembler.zip` and `media/{apollo.webp,franklin.jpg,nypl.jpg}`. It replaces precisely four remote resources with bundled references; the protected 19-step content and local-only environment guard are unchanged. No WordPress content, user/subscriber records, credentials, production database, or other media are fetched or copied.

## Command — only after independent source/rights review
Keep files under a private local folder (permissions 700 for folder, 600 for each input) including:
- `integrated-blueprint.json` — exact private PR #414-generated 19-step integrated candidate; **not** the earlier seven-chapter-only PR #388 Blueprint.
- `source-media-manifest.json` — independently reviewed original URL / bytes / SHA-256 records, as required by PR #451.
- `assembler.zip` — official downloaded Assembler theme ZIP, separately reviewed SHA-256.
- `media/apollo.webp`, `media/franklin.jpg`, `media/nypl.jpg` — *actual* independently verified original downloads; never commit uncertain-rights images to GitHub.

Run from `experience2/home-flagship/qa/playground`:

```bash
python make_offline_private_bundle.py \
  --blueprint /private/fv/integrated-blueprint.json \
  --blueprint-sha256 <independently-approved-64-hex-digest> \
  --media-manifest /private/fv/source-media-manifest.json \
  --media-dir /private/fv/media \
  --assembler-zip /private/fv/assembler.zip \
  --assembler-sha256 <independently-approved-64-hex-digest> \
  --out /private/fv/complete-private-playground.zip
```

The resulting ZIP can be supplied to a separately installed local Playground CLI without fetching the theme or archival images again:

```bash
npx @wp-playground/cli server --blueprint=/private/fv/complete-private-playground.zip --port=19400
```

Only run in a local isolated developer environment. After launch, the existing `verify_playground_browser.py` can test `http://127.0.0.1:19400/` with independently pinned axe-core and the trusted original-image manifest; Lighthouse must be **actually executed** separately. PR #451's one-command launcher currently expects a source JSON Blueprint and **does not yet accept this new ZIP**; do not present the ZIP pathway as a successful #451 launcher run. Never use production tokens or public URL storage for the ZIP; never sync a development database into production.

## Verification conducted
- New synthetic-only regression suite **11/11 PASS**, including deterministic repeat build; wrong media SHA, wrong media type, wrong media URL, wrong theme hash, ZIP traversal, symlink, nonprivate output, existing output and wrong original resource rejected.
- Parent PR #451 unchanged regression suite **24/24 PASS** in the same environment.
- GitHub fetched blob IDs of committed files were independently compared to the locally tested exact blobs.
- Additional honest source-only Chromium art/interaction preview executed at **320/360/390/768/1024/1440/1920**, 5 interaction assertions, no-JS and reduced-motion. This overlaps established PR #382 static source QA and **is not new WordPress staging**. Founder screenshot package preserved outside repo, without authentic source image bytes.

**NOT TESTED:** actual integrated private WordPress/Assembler render, hosted Atomic behavior, real source image HTTP transfers/rights clearance, real axe/WCAG 2.2 AA, lab Lighthouse, p75 CWV, Jetpack delivery, Safari/AT, exact CI/QD and founder release approval. Synthetic images used only in tests; they are never authentic historical images.

**RELEASE HOLD.** This PR is a private staging *transport/preparation* capability. It requires approved original bytes and installed Playground runtime before producing the real bundle and collecting end-to-end evidence.
