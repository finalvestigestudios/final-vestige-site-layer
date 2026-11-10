# EX2 Page 6 native Focus PHP custody — adversarial release blocker

**Status:** draft review only; **RELEASE HOLD**. Parent PR #1873 exact head `4a9bad9c5fbc3950d31902772e91cc7ce89e60b2`. Frozen v1 PR #49 untouched.

## Source-grounded problem (2026-11-10)

A fresh read-only `wpcom_mcp_pages_get(id=6, context=edit)` inspection returned public Page 6 modified 2026-11-05, with **five** Gutenberg Custom HTML blocks: first contains all **72 Hidden in the Margins** items, second the existing seven-chapter flagship, third the **original native `<section class="fv-focus-cta">` with `href="/focus/"`**, plus one serialized native Jetpack subscriptions block later in the page. The WordPress account exposes only production site ID 256784396, on the Personal plan. No isolated WP staging was available.

The generated local Playground PHP in PR #1873 matched `<section class="fv-focus-cta"> ... <a class="fv-focus-cta__button" href="/focus/"> ... </section>` **against the entire serialized Page 6 source**. A permissive cross-section regex could therefore accept a safe-looking link from a different section or the replaceable flagship when the preserved, original WordPress conversion action had disappeared or been redirected. Its nominal pass was not proof of the original Focus funnel's custody.

## Reproduced failure (isolated PHP; WordPress APIs mocked)

Original pre-fix PHP returned exit 0 on all four malformed, SHA-recomputed synthetic pages:

1. Native Focus button redirected off-site; unrelated later section supplied a safe-looking `/focus/` link.
2. Native Focus section renamed/removed; replaceable seven-chapter candidate supplied an impersonating native Focus section.
3. Original native Focus section duplicated.
4. Native section's original button renamed, while an unrelated section supplied `fv-focus-cta__button`.

The amended PHP returned nonzero for all four, preserving both valid control destinations (`/focus/` and `https://finalvestige.com/focus/`). The parent guard was bypassed **in the isolated test only**; no production exploit or live site incident is asserted.

## Fix

Within the generated **local-only** `runPHP` Blueprint step:

- Partition serialized `<!-- wp:html --> ... <!-- /wp:html -->` blocks into **exactly one** flagship and retained outside blocks; enforce the expected custom-block count.
- Locate exactly one original `fv-focus-cta` section **outside** the flagship and exactly one `fv-focus-cta__button` **inside the same section**, not arbitrarily later in the page.
- Allow only the two source-observed Focus destinations. Reject duplicate sections/actions, spoofed flagship CTA, unrelated decoys, query/fragment/redirect.
- Preserve all earlier conditions: environment `local`, private page, hash verification, `parse_blocks`, original serialized Jetpack, 72 Margins, read-back content hash, and no production path.

Files: `tools/experience-2/build_page6_playground_bundle.py`, `tests/experience-2/test_page6_playground_bundle.py`, new adversarial `tests/experience-2/test_page6_php_native_focus_custody.py`. No homepage design assets, public CMS pages, signup code, commercial links, or analytics scripts changed.

## Verification scope

In a local source-equivalent fixture, existing Blueprint regression tests **14/14 PASS**, the additional PHP adversarial suite **7/7 PASS**, with four parent false-positives independently reproduced before correction (old exit 0 → fixed nonzero). These tests run PHP 8.4 with mocked WordPress functions and do **not** establish real WordPress/Assembler, WordPress Playground, Jetpack confirmation, WCAG, media/network, CWV/Lighthouse, independent exact-HEAD CI, or QD approval.

The final commit SHA, file blobs, and PR statuses should be rechecked after PR creation. **No merge/deploy/WordPress writes**.

## Remaining release gates / handoff

1. Reconstruct an isolated local WordPress Playground or Docker/Assembler site from **public-only** content, never production subscriber/database content; run current Blueprint and `parse_blocks()` on genuine WordPress.
2. Conduct full 320–1920px + 200% zoom, keyboard, touch, reduced-motion, no-JS, axe/WCAG 2.2 AA, HTTP CSP, real archival image-byte and rights checks, measured Lighthouse lab metrics; browser screenshots must be genuinely tied to that checkout.
3. Independently verify native Jetpack signup/confirmation and 52-page Focus Fieldbook without creating unsolicited subscriber actions. Confirm source/medium attribution later with Claude's existing funnel implementation; do not add instrumentation here.
4. Obtain independent SHA-pinned CI/QD, founder visual acceptance and explicit release approval before any production change.

**Conversion contract:** offer = existing 52-page Focus Fieldbook; funnel step = historical evidence → original native Focus button → confirmed signup → paid conversion; blocker = false-positive admission for removed/redirected native CTA; change = original-block-only PHP validation; evidence = 4 reproduced bypasses corrected + 21 passing synthetic tests; commercial result = **not measured**. Attribution owner: Claude. Grok/Praxxis continue campaign/media lanes. No claim of added subscriptions, conversions, sales, or net revenue.
