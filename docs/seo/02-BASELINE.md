# 02 - Live-site baseline (2026-11-02)

Source: `tools/crawl_public_site.py` run against the public site (140 published URLs: 79 pages, 61 posts), raw output `evidence/crawl-baseline-2026-11-02.json`. Raw stored values come from `evidence/seo-prestate-2026-11-02.json`, read from wp-admin with `context=edit` (read-only). Full pre-edit post/page bodies are kept **outside the repo** at `Projects/fv-release-backups/seo-2026-11-02/raw-content-2026-11-02.json`.

| Check | Result |
|---|---|
| HTTP status | 140 of 140 return 200 |
| Canonical | every page's canonical equals its own URL |
| Title and description | every URL has a non-empty `<title>` and meta description; no duplicate titles or descriptions |
| H1 | one `<h1>` and one `<main>` on every sampled page (the first crawl reported 0 H1 on 30 URLs because of a regex bug, `<h1[\b>]`; fixed to `<h1[\s>]` and re-checked on 4 of them) |
| Title style | 104 end "\| Final Vestige"; 18 end "– FINAL VESTIGE" (no custom title); 18 other |
| Titles over 70 characters | 39 posts (max 125) |
| Descriptions | 87 over 160 characters; 18 over 200; 3 under 80 (policy pages: 29, 42, 77) |
| Structured data | 63 posts: Article + BreadcrumbList + Person; 75 pages: BreadcrumbList only; 1 ProfilePage; homepage: Organization, WebSite, Organization (outside the page-6 block; not touched) |
| Internal links in `<main>` | posts: median 17, min 13; pages: median 2, 14 pages with 0 |

**Counting limit.** Internal links were counted inside `<main>` only. The site-wide header and footer navigation (e.g. footer links to Investigations, The Public Record, Labs, The Library, History Lab, Field Notes, The Exchange) are outside `<main>` and are *not* in these counts, so pages such as `/labs/` and `/history-lab/` (0 inbound in content) are reachable from the footer and are not orphans.

## Lowest inbound internal links from page/post content

0: `/labs/`, `/history-lab/`, `/about/disclosures-policies/` (footer-linked). 1 each: the accountability case pages and their category hubs, and 21 of the 24 "the-..." guide pages (the only content link is from `/free-resources/`). Full list: `03-INTERNAL-LINK-MAP.md`.

## Protected state

Page 6 (homepage): modified `2026-11-02T17:48:13`, 6 top-level blocks, whole-content SHA-1 `1207973a80fb6618dcc91bd56131140a82854979`. The flagship block's SHA-1 (`8c0dd5c3adce073fd58f5001e0f90d523ffad277`) is re-verified through `page-sections.list` before and after the change set; page 6 is in no edit list.
