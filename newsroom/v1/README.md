# FV Newsroom V1 — isolated review candidate

**Not installed or deployed.** The Site Layer release process and QD exact-SHA approval remain mandatory. This is a standalone plugin candidate under newsroom/v1, not a change to the production runtime. No paid APIs, external publishing, automatic image copying, newsletter sends, or tracking changes.

## Objective
Build an editorially independent news destination at /news/ with responsive image-led cards, eight topic desks, chronological articles, real publication dates, source links, original contribution, and image-level provenance. Investigations remain the evergreen archive. News is time-sensitive, not a cloned feed.

## Included
- WordPress custom post type and taxonomy, native archive and pagination.
- Scoped responsive archive design, image slots and evidence section on article pages.
- First-party NASA discovery adapter, admin-only bounded lead queue, age and URL validation, source health, and five-minute WP-Cron interval. Discovery disabled unless FV_NEWS_DISCOVERY_ENABLED is explicitly true. WP-Cron is not a guaranteed clock; use an approved server scheduler and measure latency.
- Draft-first review metadata and basic publish checks for source, image, alt, reviewer and desk. The checks are NOT a substitute for editorial review, are not content-hash-bound, and need REST/block-editor, scheduled-post, concurrent update and permission tests before use.
- No fake sample articles or invented dates.

## Editorial workflow
Detect source lead -> classify FV relevance -> verify primary record and independent corroboration where necessary -> author original reporting and historical context -> item-level image rights review -> actual reviewer approval -> publish -> monitor corrections -> link related investigation -> offer existing consent-verified Dispatch signup. Label news, analysis, research/preprint, developing and disputed claims. Never report a press release as independently verified fact without checking.

## Expansion sources (candidate, not configured or tested)
NASA feed directory https://www.nasa.gov/rss-feeds/
USGS https://www.usgs.gov/news/news-releases/national-news-releases
NOAA https://www.noaa.gov/rss-feeds
ESA https://www.esa.int/Applications/Observing_the_Earth/FutureEO/RSS_feeds
Smithsonian https://www.si.edu/newsdesk
National Archives https://www.archives.gov/press
Add NTSB, CSB, universities, archaeology institutes, journals, official UAP reports, Crossref and museum feeds after endpoint, usage terms and update validation. No RSS image reuse presumed licensed.

## Launch milestones
1. Verify no existing /news/ route conflicts; confirm canonical host, permalink rules, theme integration and exact standards URL. Install only in staging after exact-SHA approval.
2. PHP lint and full WordPress integration suite: editor/REST, source feed failover, timezone/age, dedupe, pagination, public privacy, no published item without human review, rollback, edit invalidation, no global effects. Verify that the chosen installation supports plugin activation.
3. Expand adapters and source health/queue triage; build exact-content reviewer approval and robust locked ingestion. Confirm feed-level terms and real timestamps. Add refresh signaling only when published content actually changes.
4. Implement validated NewsArticle markup or extend existing SEO plugin (no duplicate JSON-LD), canonical URLs, author identity, image size variants, original publication vs update dates, Open Graph, XML news sitemap with two-day window, Google Search Console checks and indexing policy. See https://developers.google.com/search/docs/appearance/structured-data/article and https://developers.google.com/search/docs/crawling-indexing/sitemaps/news-sitemap . These are requirements, not shipped functionality.
5. Real image-rights-cleared seed reports across desks; staging desktop/mobile rendering, accessibility, performance and rights audit. No fictitious news. Then release navigation link, verify signed-out destinations.
6. Coordinate Claude/Grok/Praxxis through existing relay; no competing video pipeline. Track qualified human news sessions, returning readers, confirmed subscriber conversions, attributed settled net revenue. Daily performance review.

## Reliability
Target collection 5 minutes (not a guarantee); publication as quickly as verification permits. Never claim live or breaking unless timestamps and facts support it. On feed outage retain last valid leads and show internal error; never invent content. Queue is limited to 150 recent links; no original news report is created automatically. Review concurrency and update semantics before production.

## Release status
Candidate only. No native PHP or WordPress integration tests run from the connector. No public site changes, production merges, route creation, menu updates, feed activation or news publishing.
