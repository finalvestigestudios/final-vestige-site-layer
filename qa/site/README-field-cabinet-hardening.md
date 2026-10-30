# Field Cabinet import and saved-link hardening — staged, NOT deployed

## Confirmed issue in published WordPress source

The published **Field Cabinet** page at `https://finalvestige.com/field-cabinet/` (page ID **531**) embeds its browser-only saves/import logic as one inline `<script>` within a single top-level `core/group` block.

The existing code accepts URL and reading-record fields from a user-selected JSON import and later uses the imported strings in `innerHTML` as clickable `href` attributes. It HTML-escapes quote characters, but does **not check URL schemes**. For instance, a crafted backup file could supply `"url":"javascript:alert(1)"`; the click-through HTML would contain a `javascript:` URL even though the HTML attribute is escaped. **This requires a user to import an untrusted file and interact with the resulting link; it is not evidence of remote zero-click compromise.**

Existing saved/imported records may also contain malformed arrays and reading-map values, which can break rendering or merge unsafe URLs. The copy/export workflow makes it worthwhile to sanitize imported records rather than silently reproducing them.

## Staged correction

- `field_cabinet_hardened_wp_block.html`: proposed replacement of the existing inline script, preserving all current UI, labels, rendering, export, import, local save, reading progress and guest/signed-in behavior.
- `field_cabinet_page531_candidate.blocks.html`: **full single Gutenberg group-block candidate** derived from the exact published page source, with ONLY the existing script replaced. This is a *review artifact*, not something currently installed or auto-deployed.
- `test_field_cabinet_hardening.cjs`: 14 Node built-in test cases for safe links, dangerous URL schemes, control-character tricks, credentials in URLs, valid imports, reading state, malformed data, HTML escaping and 2-MB file cap.

The new code:
1. Accepts only explicit `http:` and `https:` URLs via the browser `URL` parser; rejects `javascript:`, `data:`, `vbscript:`, `file:`, control characters, overly long URLs and URLs with embedded credentials. Relative site paths are resolved against the current site's origin.
2. Filters untrusted records *before* inserting HTML and again when importing and loading localStorage data. Unsafe links are not rendered.
3. Validates reading-progress entries, omits prototype-control keys, and caps imported records.
4. Rejects JSON import files greater than 2 MiB.
5. Preserves previous legitimate saves and all existing UI controls and URLs.

**Local evidence:** A directly executed mock-DOM adversarial check against the exact committed script succeeded for legacy stored data, malicious JSON import and oversized-file rejection. The checks used a custom URL-parser mock because the connected JavaScript evaluator does not expose the browser's built-in `URL` object. The 14 Node tests are committed for independent execution; **do not claim those Node tests have run until an actual Node runner executes them**.

Run after checkout:

```bash
node --test qa/site/test_field_cabinet_hardening.cjs
```

## Production deployment procedure — specific user approval required

1. Retrieve a fresh `pages.get` and `page-sections.list` for WordPress page **531** in `edit` context.
2. Verify the page remains published, contains one `core/group` top-level block and the original inline Field Cabinet script exactly once; check that no other agent has edited the page.
3. Compare the candidate replacement against the fresh `core/group` content; **only the script may differ**. If the page changed since the candidate was built, regenerate the candidate against the new revision; do not overwrite stale content.
4. Use `page-sections.replace` with `index:0`, `expected_block_type:"core/group"`, and fresh `expected_modified`, `expected_content_hash`, `expected_block_hash`. Set `user_confirmed:true` ONLY after explicit user consent to this specific change.
5. Immediately read back status/content/section hash, and verify exactly one script, unchanged group structure, original navigation/export/import buttons and all legitimate links.
6. Test in an **actual** desktop/mobile browser: save articles, export a backup, reimport it, recover reading progress, try safe HTTP(S) and malicious-scheme imports, keyboard-focus and click the resulting cards. Confirm localStorage guest saves still work and account-backed favorites are unaffected. Browser testing not yet performed.
7. Save a rollback copy and the prior block hash so the original script can be restored with another approved optimistic-locked edit if any unexpected regression occurs.

## Scope

No changes to `/focus/`, homepage PR #49, Preparedness Archive, plugin installation, sitewide navigation, subscriber data, account permissions or billing. This draft is for security QA review only and **does not authorize a WordPress write**.
