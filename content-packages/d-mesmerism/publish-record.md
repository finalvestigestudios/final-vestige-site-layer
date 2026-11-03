# d-mesmerism: publish record

- **Status:** published and verified, 2026-11-02
- **WordPress.com post ID:** 1924 (site 256784396, finalvestige.com)
- **URL:** https://finalvestige.com/2026/11/02/mesmerism/
- **Published at:** 2026-11-02T20:52:58 (site time)
- **Article source:** `d-mesmerism/article.html`, SHA-256 (LF-normalised) `51d458a6b76b11ed400e29c1b76fd8308f9c45303cf000104c4c66ce825ea067`
- **Live text hash:** SHA-256 `2919ebb596120469afabe56721bfc08d06031791d0947dc4b41f895a6ece16c7` of the concatenated visible text blocks (paragraphs, list items, headings, captions with 25+ characters) as checked against the live page
- **Sources:** see `evidence.md` (every source opened, claim-to-source map, image rights)

## Read-back verification (anonymous fetch of the live URL)
- HTTP 200; canonical equals the URL; one H1; SEO title and meta description as in `meta.json`; no `noindex`
- 40 of 40 source text blocks found in the live HTML; 0 missing
- JSON-LD on the page: Person, Article, BreadcrumbList, FAQPage (all parse)
- 6 outbound and image URLs in the source checked; see notes
- Draft was created first and its stored content read back (script and JSON-LD survived) before status was changed to publish
- Subscriber email and Jetpack social auto-share were switched off for this post before publishing

## Notes
Source is a 1785 English translation; Public Domain Review essay is interpretive and attributed as such. Draft post 1358 (Puységur memoir, noindex) untouched.

## Rollback
1. Set post 1924 back to `draft` with `posts.update` (`status: "draft"`), which removes it from the public site, sitemap and feeds.
2. To remove permanently, delete the post in wp-admin (`/wp-admin/post.php?post=1924&action=edit`).
3. Page 6 (homepage), plugins, theme and navigation were not touched by this package, so nothing else needs reverting.

## Revision 2: evidence corrections (2026-11-02, 22:02–22:04)
Corrected after the QA table; before/after text in `../CORRECTIONS-LOG.md`. Post 1924: modified `2026-11-02T22:04:16`, WordPress content_hash `6c22e567c9848fd9bc7893c57282563c8cb6a563`. Article source SHA-256 (LF) now `492aff79e4c4e3f590d6856b568a96c8fa976a3f5aa1184c68f7635d9cc7f5cc`. Re-read live: one Article, one FAQPage, one BreadcrumbList; all text blocks match; FAQ JSON-LD equals the visible FAQ. Rollback of this revision: restore the earlier block text from the log, or revert the post to its 20:xx revision in the WordPress.com revision history.
