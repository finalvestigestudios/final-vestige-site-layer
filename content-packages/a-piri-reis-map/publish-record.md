# a-piri-reis-map: publish record

- **Status:** published and verified, 2026-11-02
- **WordPress.com post ID:** 1917 (site 256784396, finalvestige.com)
- **URL:** https://finalvestige.com/2026/11/02/piri-reis-map/
- **Published at:** 2026-11-02T20:48:54 (site time)
- **Article source:** `a-piri-reis-map/article.html`, SHA-256 (LF-normalised) `862691b6abb1bcf115d60298ecb2f17dcf9e9dcf0f2d5cd445196103729e9f37`
- **Live text hash:** SHA-256 `79691ab8a220f4da141e3fe9f6372977777bf6c2b0c715e83d66ec0b144605e7` of the concatenated visible text blocks (paragraphs, list items, headings, captions with 25+ characters) as checked against the live page
- **Sources:** see `evidence.md` (every source opened, claim-to-source map, image rights)

## Read-back verification (anonymous fetch of the live URL)
- HTTP 200; canonical equals the URL; one H1; SEO title and meta description as in `meta.json`; no `noindex`
- 42 of 42 source text blocks found in the live HTML; 0 missing
- JSON-LD on the page: Person, Article, BreadcrumbList, FAQPage (all parse)
- 12 outbound and image URLs in the source checked; see notes
- Draft was created first and its stored content read back (script and JSON-LD survived) before status was changed to publish
- Subscriber email and Jetpack social auto-share were switched off for this post before publishing

## Notes
One external link (Center for Inquiry PDF) refuses HEAD requests from scripts (HTTP 403); it was opened in full earlier through the Firecrawl PDF parser. Caveats carried in the article: McIntosh and Hapgood books read only through publisher description / Jolly; Jolly issue date unconfirmed.

## Rollback
1. Set post 1917 back to `draft` with `posts.update` (`status: "draft"`), which removes it from the public site, sitemap and feeds.
2. To remove permanently, delete the post in wp-admin (`/wp-admin/post.php?post=1917&action=edit`).
3. Page 6 (homepage), plugins, theme and navigation were not touched by this package, so nothing else needs reverting.
