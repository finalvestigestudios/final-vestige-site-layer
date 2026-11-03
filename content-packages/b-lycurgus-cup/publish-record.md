# b-lycurgus-cup: publish record

- **Status:** published and verified, 2026-11-02
- **WordPress.com post ID:** 1920 (site 256784396, finalvestige.com)
- **URL:** https://finalvestige.com/2026/11/02/lycurgus-cup/
- **Published at:** 2026-11-02T20:50:12 (site time)
- **Article source:** `b-lycurgus-cup/article.html`, SHA-256 (LF-normalised) `a10d1c02cdf5888476b492e0f5bef86c27df4688785db7c630a5d6edd2cc0643`
- **Live text hash:** SHA-256 `ad7b598eec102c30b98114f5b6e00a40bc57a15be0167b4e339c384b2d5ff033` of the concatenated visible text blocks (paragraphs, list items, headings, captions with 25+ characters) as checked against the live page
- **Sources:** see `evidence.md` (every source opened, claim-to-source map, image rights)

## Read-back verification (anonymous fetch of the live URL)
- HTTP 200; canonical equals the URL; one H1; SEO title and meta description as in `meta.json`; no `noindex`
- 38 of 38 source text blocks found in the live HTML; 0 missing
- JSON-LD on the page: Person, Article, BreadcrumbList, FAQPage (all parse)
- 8 outbound and image URLs in the source checked; see notes
- Draft was created first and its stored content read back (script and JSON-LD survived) before status was changed to publish
- Subscriber email and Jetpack social auto-share were switched off for this post before publishing

## Notes
British Museum record link refuses scripted HEAD (HTTP 403); the record was opened through Firecrawl. Study is the 2007 state of knowledge.

## Rollback
1. Set post 1920 back to `draft` with `posts.update` (`status: "draft"`), which removes it from the public site, sitemap and feeds.
2. To remove permanently, delete the post in wp-admin (`/wp-admin/post.php?post=1920&action=edit`).
3. Page 6 (homepage), plugins, theme and navigation were not touched by this package, so nothing else needs reverting.
