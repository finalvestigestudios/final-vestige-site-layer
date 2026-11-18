# The Log Was Not the Voyage — independent nine-guide release audit

**Last checked:** November 18, 2026, 03:40–04:00 PST (same-session authenticated WordPress reads and public-source review). **Scope:** Library draft IDs 2886–2894 only. **Disposition:** HOLD / unpublished. **Owner:** FV Library Resource Studio.

## Why this is useful

The Library now has nine independently reviewable maritime research guides, but their navigational links point to nine unpublished peers. Before a public card can invite readers into this collection, the source trail, structural consistency and suppression of automated notifications must survive an independent release gate. This audit deliberately checks current stored WordPress content rather than trusting earlier implementation summaries, and leaves all editorial pages unchanged.

A new **read-only, fail-closed preflight** is versioned at [ship-logbook-read-only-release-preflight-2026-11-18.mjs](ship-logbook-read-only-release-preflight-2026-11-18.mjs), commit `0b0fa748f4f55b72d5bc34d3c99382ebc6cf976a`. It requires Node 20+, no dependencies, reads WordPress REST edit-context pages with separately supplied credentials or saved JSON fixtures, and reports structural failures, warnings and six manual release gates. Its `readyForPublication` output is **always false**: static source checks cannot certify first-publication safety. No credentials are logged, no WordPress changes are made.

## Nine authenticated draft readbacks

| ID | Guide | Serialized characters | Gutenberg blocks | All anchors resolve? | Unique IDs? | Peer links |
|---:|---|---:|---:|---|---|---:|
| 2886 | Locate the ship logbook | 30,653 | 3 | Yes | Yes | 8 |
| 2887 | Missing-log outcomes | 26,972 | 3 | Yes | Yes | 8 |
| 2888 | Vessel identity | 21,058 | 3 | Yes | Yes | 8 |
| 2889 | Three pages, one day | 23,716 | 3 | Yes | Yes | 8 |
| 2890 | Sailor and crew evidence | 27,674 | 3 | Yes | Yes | 8 |
| 2891 | Position versus track | 29,077 | 3 | Yes | Yes | 8 |
| 2892 | Port entry versus docking | 26,512 | 3 | Yes | Yes | 8 |
| 2893 | Wireless acknowledgment versus delivery | 37,763 | 4 | Yes | Yes | 8 |
| 2894 | Authorized log corrections | 26,393 | 3 | Yes | Yes | 8 |

**Totals:** 9/9 pages read from WordPress `context=edit`, 249,818 stored-content characters, 253 `<a>` links, 72 deliberately staged peer links, 57 distinct absolute URLs (includes FV pages), three local interactive-script modules. Each page independently reported `status=draft`, `parent=77` and `jetpack_seo_noindex=true`; each has one `aria-current=page` marker, zero duplicate element IDs, zero missing local fragment targets, zero empty/JavaScript `href` values, and no image element missing an alt attribute. Nine page-specific original explanatory SVGs and responsive CSS were present; their actual browser rendering was **not** certified.

## Public readbacks / canonical, metadata and layout evidence

WordPress signed-out rendered-page inspection: [The Library](https://finalvestige.com/free-resources/) HTTP **200**, canonical unchanged, Jetpack SEO meta description and one top-level H1 present. [Editorial Standards](https://finalvestige.com/editorial-standards/) and [Research Sources](https://finalvestige.com/free-resources/research-sources/) were independently fetched as readable public pages. The unissued first child [ship-logbook-archive-route](https://finalvestige.com/free-resources/ship-logbook-archive-route/) is HTTP **404** to signed-out visitors, appropriate for a draft. No public Library card, site-wide nav, URL, redirect or subscription setting was changed.

The WordPress screenshot service returned `status=ready` for live Library captures requested at **320, 390, 768 and 1440px**. Those links show the *published Library index*, not the protected draft pages. Pixel inspection, text-overflow measurements, screenshot acceptance and screen-reader acceptance **have not been performed**. They must not be counted as pass results.

## Source and access check — November 18, 2026

The following official underlying resources were opened and their subject, role and accessibility checked, not merely copied from earlier ledgers:

- NARA: [Navy deck-log overview](https://www.archives.gov/research/military/logbooks/naval-deck-logs), [digitized log index](https://www.archives.gov/research/military/logbooks/navy-online), [digitization context](https://www.archives.gov/research/military/logbooks/digitized-logs), [1941–1959 formats](https://www.archives.gov/research/military/logbooks/navy-deck-logs-1941-1959), [1960–1978 formats](https://www.archives.gov/research/military/logbooks/navy-deck-logs-1960-1978), [not included](https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs), [missing/classified](https://www.archives.gov/research/military/logbooks/navy-deck-log-exemptions), [RG 45](https://www.archives.gov/research/military/logbooks/rg45.html), [NOAA survey vessels](https://www.archives.gov/research/military/logbooks/noaa-vessels.html), [merchant logs](https://www.archives.gov/research/military/logbooks/merchant-vessels.html), [historic merchant guide](https://www.archives.gov/research/military/logbooks/merchant-vessels-old.html), [merchant documentation](https://www.archives.gov/research/maritime/merchant-vessel-documentation), [vessel documents](https://www.archives.gov/research/maritime/vessel-documents.html), [muster rolls](https://www.archives.gov/research/military/navy/muster-rolls), [OMPF public access](https://www.archives.gov/personnel-records-center/ompf-access-public), [Kansas City RG 36 finding aid](https://www.archives.gov/kansas-city/finding-aids/html/rg36-series-title-list.html), [still-photo permissions](https://www.archives.gov/research/still-pictures/permissions).
- NOAA: [NGS datum FAQ](https://www.ngs.noaa.gov/datums/faq.shtml) and [nautical-chart accuracy](https://nauticalcharts.noaa.gov/updates/how-accurate-are-nautical-charts/).
- Final Vestige: [Archive Trail](https://finalvestige.com/the-archive-trail/), [Moving Noon](https://finalvestige.com/the-moving-noon/), [Same Story Twice](https://finalvestige.com/free-resources/the-same-story-twice/) and [Franklin investigation](https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/) were fetched; two other crosslinks, [The Last Fix](https://finalvestige.com/the-last-fix/) and [The Box Behind the Citation](https://finalvestige.com/free-resources/the-box-behind-the-citation/), were directly confirmed `publish` through authenticated WordPress despite the public research fetch client refusing them.
- **Access limitations:** the [UK merchant Navy guide](https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/merchant-navy-ships-records-crew-lists-musters-and-log-books/) returned HTTP 403 to this client; the [LOC catalog item](https://www.loc.gov/item/2025847774/) also returned 403. Neither is called a broken public link solely from these responses. The full 57-URL matrix is not yet completely verified.

This run produced **no third-party media copies**. Existing SVGs are described as original explanatory illustrations, not scans or shipboard records. The National Archives' [copyright/permission guidance](https://www.archives.gov/research/still-pictures/permissions) does not license every item the agency holds; future reproduction requires item-level review. The historic inquiry PDF in draft #2893 remains *linked*, not rehosted.

## Subscriber, release and QA controls — blocking

WordPress Newsletter `get_settings` at **2026-11-18 11:40 UTC** returned `subscriptions=true`, `email_new_posts_by_default=false`. Recent sends include `never_sent_opted_out`, but those were separate published **posts**, not proof that these **pages** will suppress email/social on first publication. The available page connector does not support independently set/read `_jetpack_dont_email_post_to_subs=true` and social-permission equivalents. **Do not publish on the strength of a default.**

Real responsive screenshots and keyboard/screen-reader/print interaction must be verified against the *protected article rendering*, not only the index. Require measured overflow and click/keyboard evidence at 320/390/768/1440; check the three browser-local worksheet scripts, 8 sibling links on every page, canonical/noindex after public release, every source access qualifier, and per-item image rights. Coordinate independent site QA through existing issue #1589 and the related navigation/notification work. The published Research Sources inventory issue #1788 is separately owned.

## Release disposition

**HOLD; 0 public pages changed; 0 subscriber emails; 0 social posts; 0 spending.** No Preparedness, Investigations or homepage engineering edits. No Grok actions; a potential short film about three different meanings of a missing record can be offered after confirmed publication. Carry this audit as part of existing draft [PR #2922](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2922) and Library coordination [issue #2923](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/2923).
