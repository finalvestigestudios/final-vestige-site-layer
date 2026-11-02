# Release and rollback procedure (PROPOSED - nothing here has been run on production)

**Production:** WordPress.com site `256784396` (finalvestige.com), Personal plan, single environment, theme Assembler. Homepage = page ID 6. No staging exists; the existing `wpcomstaging.com` host is the same site, not a clone.

## What changes (exactly)

**Operation 1 (the release):** `page-sections.replace` on page 6, **block index 1**, `core/html`, replacing the old Studios hero (SHA-1 `1c97fec5cc356a02fb2f51a092f749c81efcd98c`, 4,288 bytes) with `production-change/replacement-block-index1.html` (114,355 bytes; bytes and hashes in `PROPOSED_PRODUCTION_CHANGE.json`). The flagship's CSS and JS travel **inside that block**; no plugin is installed or updated.

**Operation 2 (optional accessibility fix, run only after operation 1 and with fresh lock tokens):** `page-sections.replace` on **block index 2**, the Focus CTA (SHA-1 `abc983ae1b3cf45d35589c7e5366ccc522cb0462`), with `replacement-block-index2.html`, which is identical except the button's `aria-label` is removed so its accessible name equals its visible text (WCAG 2.5.3). Its original was read raw from the page and hashes to the live block hash.

Not changed: blocks 0, 3, 4, 5 (72 Margins strip, the home shell with the **native Jetpack Dispatch block**, Enter-the-record, Organization JSON-LD), theme, navigation, templates, site settings, plugins, Jetpack configuration, subscribers, any other page. PR #49 untouched.

Lock tokens read on 2026-11-02 (again before this round, unchanged): `modified` `2026-10-30T09:14:14`, `content_hash` `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. If either differs at execution time, stop and re-review. After operation 1 the page `content_hash` changes; re-list before operation 2.

## Preconditions (all must be true; none is true yet)

1. Independent QD review of the exact head approved by a named reviewer, recorded in the PR.
2. Hosted CI green on that exact head.
3. Founder approval of the visual result and of decision D1 (long page).
4. Editorial/legal sign-off on the three archival images (credits already in the markup).
5. Step 1 below passed.

## Steps

**0. Freeze and record (read-only).** Run `page-sections.list` on page 6; confirm 6 sections, block 1 `1c97fec5...`, block 2 `abc983ae...`, and the lock tokens above. Save the raw page via `pages.get context=edit` to private storage (not the repo) as the full-page backup, and note the WordPress.com revision list for page 6. (Blocks 1 and 2 are already backed up in `production-change/`.)

**1. Dry run on WordPress.com (authorized; draft page 1902 exists).** Done so far: the inline `<style>`, `<script>` and `<noscript>` and hazard characters are stored byte-for-byte (`dry-run/WORDPRESS_COM_DRAFT_VERIFICATION.md`). Still to do, needs a signed-in browser: put the exact replacement block into draft 1902 (`pages.update`, status `draft`), confirm `page-sections.list` shows its `block_hash` equals the SHA-1 of `replacement-block-index1.html`, view the preview, run `wp-candidate/qa/run_wp_qa.py` against it, capture screenshots, then trash the draft. **If anything was stripped, stop:** fall back to a plugin delivery through the governed Site Layer lane.

**2. Apply.** `page-sections.replace` with the parameters in `PROPOSED_PRODUCTION_CHANGE.json` -> `apply`. Idempotent; the call is rejected if the lock tokens or block hash no longer match.

**3. Verify (within minutes, read-only).**
- `page-sections.list`: still 6 sections; blocks 0, 2, 3, 4, 5 have the same `block_hash` values as before; block 1 hash equals the replacement's SHA-1.
- `GET https://finalvestige.com/`: 72 `.fv-margin-strip__item`, `form#subscribe-blog` with an email input, 2 `/focus/` links in the preserved blocks, one `<main>`, no "DESIGN CANDIDATE" text.
- `run_wp_qa.py --url https://finalvestige.com/` at seven widths (this only reads the site; its POST blocker prevents any form submission) and a Lighthouse run for the record.
- Do **not** submit the Jetpack form to test it with a real address; use the founder's own address only if the founder asks for that.

**4. Watch.** Compare Jetpack Stats / Search Console traffic and subscribe-form conversions against the prior week; the form markup is unchanged so a drop would point to layout.

## Rollback

Trigger: any broken interaction, stripped markup, layout regression, form regression, or founder request. Roll back in the reverse order of application.

**If operation 2 was applied (reverse it first):**
1. `page-sections.list`; block 2 `block_hash` must equal the SHA-1 of `replacement-block-index2.html` (`PROPOSED_PRODUCTION_CHANGE.json` -> `operation_2_optional`).
2. `page-sections.replace` index 2 with `original-block-index2.html` using `operation_2_optional.rollback_params`. Verify block 2 is `abc983ae1b3cf45d35589c7e5366ccc522cb0462` again.

**Operation 1:**
1. `page-sections.list`; block 1 `block_hash` must equal the replacement's SHA-1 (`apply.replacement_sha1`).
2. `page-sections.replace` index 1 with `original-block-index1.html` using `rollback`.
3. Verify block 1 is `1c97fec5cc356a02fb2f51a092f749c81efcd98c` again. **Only when both operations are reverted** does the page `content_hash` return to `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`; that equality proves the page is byte-identical to the pre-release state.
4. Alternative if the section API is unavailable: restore the page 6 revision dated 2026-10-30T09:14:14 in the editor.

Both original blocks were checked against the live `block_hash` values (block 1 rebuilt from the public page, block 2 read raw from the editor), so the rollback copies are the live bytes. The production-change files are marked `-text` in `.gitattributes` so that no checkout can rewrite their line endings and invalidate the hashes.

## Not covered by this procedure

Packaging through the governed Site Layer lane (`production` branch deploy), Focus Popup placement, trimming sections below the flagship (D1), and any affiliate or Mind/Inspire3 content: each needs its own approval and verification.
