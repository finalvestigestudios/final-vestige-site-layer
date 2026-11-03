# c-change-blindness: publish record

- **Status:** published and verified, 2026-11-02
- **WordPress.com post ID:** 1922 (site 256784396, finalvestige.com)
- **URL:** https://finalvestige.com/2026/11/02/change-blindness/
- **Published at:** 2026-11-02T20:51:39 (site time)
- **Article source:** `c-change-blindness/article.html`, SHA-256 (LF-normalised) `083201378d6c2d3b81461865c3e539b46a7dc266049eb264b2776ea44e34030d`
- **Live text hash:** SHA-256 `66955a20242e62ba1cb257638f3c46590f6a2b1e1d2484dcd5c04cfd8d631af5` of the concatenated visible text blocks (paragraphs, list items, headings, captions with 25+ characters) as checked against the live page
- **Sources:** see `evidence.md` (every source opened, claim-to-source map, image rights)

## Read-back verification (anonymous fetch of the live URL)
- HTTP 200; canonical equals the URL; one H1; SEO title and meta description as in `meta.json`; no `noindex`
- 38 of 38 source text blocks found in the live HTML; 0 missing
- JSON-LD on the page: Person, Article, BreadcrumbList, FAQPage (all parse)
- 8 outbound and image URLs in the source checked; see notes
- Draft was created first and its stored content read back (script and JSON-LD survived) before status was changed to publish
- Subscriber email and Jetpack social auto-share were switched off for this post before publishing

## Notes
Inline demo script survived WordPress.com storage and ran correctly when the served markup was executed in headless Chrome (start, I see it, reveal, new scene). Reduced-motion path and screen readers not tested. 2005 review and 1999 gorillas paper cited by abstract only.

## Rollback
1. Set post 1922 back to `draft` with `posts.update` (`status: "draft"`), which removes it from the public site, sitemap and feeds.
2. To remove permanently, delete the post in wp-admin (`/wp-admin/post.php?post=1922&action=edit`).
3. Page 6 (homepage), plugins, theme and navigation were not touched by this package, so nothing else needs reverting.
