# Release and rollback procedure (PROPOSED - nothing here has been run on production)

**Production:** WordPress.com site `256784396` (finalvestige.com), Personal plan, single environment, theme Assembler. Homepage = page ID 6. No staging exists; the existing `wpcomstaging.com` host is the same site, not a clone.

## What changes (exactly)

One write: `page-sections.replace` on page 6, **block index 1**, `core/html`, replacing the old Studios hero (SHA-1 `1c97fec5cc356a02fb2f51a092f749c81efcd98c`, 4,288 bytes) with `production-change/replacement-block-index1.html` (see `PROPOSED_PRODUCTION_CHANGE.json` for its bytes and hashes). The flagship's CSS and JS travel **inside that block**; no plugin is installed or updated.

Not changed: blocks 0, 2, 3, 4, 5 (72 Margins strip, Focus CTA, home shell with the Jetpack Dispatch form, Enter-the-record, Organization JSON-LD), theme, navigation, templates, site settings, plugins, Jetpack configuration, subscribers, any other page. PR #49 untouched.

Lock tokens read on 2026-11-02: `modified` `2026-10-30T09:14:14`, `content_hash` `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. If either differs at execution time, stop and re-review.

## Preconditions (all must be true; none is true yet)

1. Independent QD review of the exact head approved by a named reviewer, recorded in the PR.
2. Hosted CI green on that exact head.
3. Founder approval of the visual result and of decision D1 (long page).
4. Editorial/legal sign-off on the three archival images (credits already in the markup).
5. Step 1 below passed.

## Steps

**0. Freeze and record (read-only).** Run `page-sections.list` on page 6; confirm 6 sections and that block 1's `block_hash` is `1c97fec5...`. Save the raw page via `pages.get context=edit` to private storage (not the repo) as the full-page backup. Note the WordPress.com revision list for page 6.

**1. Dry run on WordPress.com (needs explicit founder authorization: it creates one private draft page).** `pages.create` status `draft`, title "FV flagship dry run - delete after", content = the composed body from `wp-candidate/qa` stage output (`page-content.html`, inline mode). Check `_content_warnings` is empty, view the preview while signed in, run `wp-candidate/qa/run_wp_qa.py` against the preview, confirm the inline `<style>` and `<script>` survived and every interaction works. Trash the draft afterwards. **If anything was stripped, stop:** fall back to a plugin delivery (the stage plugin in `wp-candidate/build_candidate.py` is the prototype) through the governed Site Layer lane.

**2. Apply.** `page-sections.replace` with the parameters in `PROPOSED_PRODUCTION_CHANGE.json` -> `apply`. Idempotent; the call is rejected if the lock tokens or block hash no longer match.

**3. Verify (within minutes, read-only).**
- `page-sections.list`: still 6 sections; blocks 0, 2, 3, 4, 5 have the same `block_hash` values as before; block 1 hash equals the replacement's SHA-1.
- `GET https://finalvestige.com/`: 72 `.fv-margin-strip__item`, `form#subscribe-blog` with an email input, 2 `/focus/` links in the preserved blocks, one `<main>`, no "DESIGN CANDIDATE" text.
- `run_wp_qa.py --url https://finalvestige.com/` at seven widths (this only reads the site; its POST blocker prevents any form submission) and a Lighthouse run for the record.
- Do **not** submit the Jetpack form to test it with a real address; use the founder's own address only if the founder asks for that.

**4. Watch.** Compare Jetpack Stats / Search Console traffic and subscribe-form conversions against the prior week; the form markup is unchanged so a drop would point to layout.

## Rollback

Trigger: any broken interaction, stripped markup, layout regression, form regression, or founder request.

1. `page-sections.list`, confirm block 1 `block_hash` equals the replacement's SHA-1.
2. `page-sections.replace` with `PROPOSED_PRODUCTION_CHANGE.json` -> `rollback` (puts back `original-block-index1.html`).
3. Verify: block 1 hash is `1c97fec5cc356a02fb2f51a092f749c81efcd98c` again, and the page `content_hash` returns to `7afdb933d2ec68fd993ef015c97a6eb9edfe0576`. That equality proves the page is byte-identical to the pre-release state.
4. Alternative path if the section API is unavailable: restore the page 6 revision dated 2026-10-30T09:14:14 in the editor.

The original block is reconstructed from the public page and verified against the live `block_hash`, so the rollback copy is the live bytes, not an approximation.

## Not covered by this procedure

Packaging through the governed Site Layer lane (`production` branch deploy), Focus Popup placement, trimming sections below the flagship (D1), and any affiliate or Mind/Inspire3 content: each needs its own approval and verification.
