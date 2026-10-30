# Focus Fieldbook edition metadata QA — review only

## Verified October 29, 2026 WordPress CMS inconsistency

Published page **1579** (`/focus/`) has a hero stating **“complete 52-page fieldbook”**, and the published Library and Collection pages separately call it **52 pages**. WordPress SEO field `advanced_seo_description` for /focus/ still reads:

> A free 7-page fieldbook: a twelve-minute routine, a seven-day log and a checklist for judging any meditation audio. Enter your email to get the PDF.

The incorrect 7-page claim predates the upgrade to the 52-page Complete Edition. The WordPress SEO `jetpack_seo_html_title` is `Free Seven Day Focus Fieldbook | Final Vestige`. `jetpack_seo_noindex=false` and the page is `publish`.

**Claim scope:** This is a **confirmed CMS metadata-to-page copy inconsistency**. It is **not** proof that a search engine currently shows an incorrect snippet or that visitors see a wrong browser-visible meta tag. The public site could not be fetched through the testing environment.

## Read-only regression gate

```bash
node --test qa/seo/test_focus_metadata_guard.cjs
node qa/seo/focus_metadata_guard.cjs sanitized_focus_snapshot.json
```

The sanitized JSON must contain `{id, slug, status, content, meta:{advanced_seo_description}}` from a fresh authorized WordPress read, or wrap it as `{page: {...}}`. No credentials, subscribers, email addresses or private content belong in this file. The guard has no HTTP, WordPress, subscriber or write capability. Exit **0** matches, **1** documented CMS mismatch, **2** inconclusive/review.

## Recommended surgical editorial fix — NOT applied

With owner authorization and after refreshing the latest revision of page 1579, change *only* the WordPress SEO description field to an accurate 52-page Complete Edition description. Suggested copy:

> Get the free 52-page Seven Day Focus Fieldbook: a 12-minute starting routine, seven guided days, a 30-day log, and a guide to evaluating meditation audio claims.

Optional title improvement, subject to search snippet length review:

> Seven Day Focus Fieldbook — Free 52-Page PDF | Final Vestige

Preserve the WordPress page body, slug, subscriber list, Jetpack block, 5 CTAs, existing CSS autofill patch, PDF media ID 1737, and welcome message. Do **not** alter live SEO settings or page while Claude edits. When authorized, use the least-invasive metadata-only edit with stale-revision detection; independently read back the saved meta and verify published HTML `<meta name="description">`, where accessible, before declaring a browser-visible correction.

This work does not duplicate #127 (general site), #130 (signup funnel), #133 (HTTP/PDF), #141 (fragment link) or #143 (proposed anchor fix). No production changes or merge/deploy were made.
