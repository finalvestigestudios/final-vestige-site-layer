# The Log Was Not the Voyage — 57-Link Source Access & Rights Register
**Checked:** 2026-11-18 (Pacific); **owner:** Final Vestige Studios Library; **scope:** WordPress draft pages #2886–#2894; **status:** RELEASE HOLD. This is an editorial read-only verification, not an image-use license, WordPress rendering certification, or a guarantee that all visitors can access the sites.

## Decision

The nine guides are **not ready to publish**. We audited every one of the **57 distinct absolute href/src URLs** in the live saved Gutenberg source (including two PDF page fragments and a PDF base link), mapped their use to individual WordPress draft IDs, and checked each destination against current public web research access. NARA, NOAA, the Cape Ann Museum finding aid, Memorial University DAI and the Titanic inquiry transcripts are broadly accessible from the research client. Specific catalog record IDs, the Library of Congress item page and UK National Archives guide have access limits; NHHC pages returned timeouts or gateway errors; several FV routes triggered the research tool's rate limiting. **No access-limit response establishes a broken public link or confirms rights to reproduce an item.** All links remain unchanged.

## Snapshot and safety

- WordPress draft readback: **9/9 draft**, parent **#77**, `jetpack_seo_noindex=true` across nine; none published. No edits to WordPress or site navigation during this audit.
- Content captured from authenticated `context=edit` readback: 249,818 characters; **253 href/src occurrences**, **57 unique absolute URLs**. The broad link count includes internal fragments and relative references not covered by this outbound register.
- The `#page=31` and `#page=32` PDF references were checked against scanned actual page images of Memorial University's *Titanic* report; PDF existence and page content verified, but a browser's page-fragment navigation mechanism still requires device testing.
- Original diagrams in the drafts are explanatory FV work. **No external scans, photos, charts, or video were uploaded or reused** in this run.
- Public Library and Editorial Standards reviewed; [draft PR #2922](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2922), [coordination #2923](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/2923), [site QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) checked before work; do not duplicate other agents' drafts.

### Access outcomes
- `CONTENT_RETRIEVED`: 42 unique URLs
- `RATE_LIMIT_429`: 3 unique URLs
- `UNAVAILABLE_DIRECT`: 2 unique URLs
- `PDF_BASE_AND_TARGET_PAGE_VISUALLY_CHECKED`: 2 unique URLs
- `RESEARCH_CLIENT_DISABLED`: 2 unique URLs
- `TIMEOUT`: 2 unique URLs
- `INDEX_ONLY_403`: 2 unique URLs
- `SHELL_ONLY`: 1 unique URL
- `GATEWAY_502`: 1 unique URL

**State definitions:** `CONTENT_RETRIEVED` means the research client returned identifiable page content; not a browser QA PASS or an assurance of permanent availability. `PDF_BASE_AND_TARGET_PAGE_VISUALLY_CHECKED` means source PDF pages examined, while fragment behavior remains untested in a real browser. `SHELL_ONLY` means the application loaded but record content was not independently available. `UNAVAILABLE_DIRECT` means a record-specific dynamic page was inaccessible via client. `INDEX_ONLY_403` means an external search index returned substantive content but direct retrieval was blocked; not a public 404. `TIMEOUT`, `GATEWAY_502`, `RATE_LIMIT_429`, and `RESEARCH_CLIENT_DISABLED` are access limitations, not proof of a broken URL.

## Rights and citation conditions — source-specific

1. **Memorial University DAI**: [DAI Rights](https://dai.mun.ca/help) states a CC BY-NC-ND license for items, with low-resolution download/print rights for personal or educational use. This project is a studio with potentially commercial pages; **link to the digitized historical report but do not embed, alter, crop, or rehost the DAI scan without written clearance**. The report's historic underlying copyright status and DAI's digitization/platform terms are distinct questions. Institutional source: Memorial University, DAI, *Shipping Casualties (Loss of the Steamship Titanic)*, 1912 scan, PDF pp. 31–32 (printed pp. 27–28).
2. **Cape Ann Museum**: [Ships Log Book Collection A18](https://www.capeannmuseum.org/media/library_and_archives_finding_aids/a18_-_ships_log_book_collection_finding_aid.pdf), cover p. 1, explicitly directs requests for permission to publish materials to its Librarian/Archivist. **Finding aid may be linked and quoted briefly within license and fair-use limits; no collection images reproduced.**
3. **National Archives (U.S.)**: [NARA Copyright and Permissions](https://www.archives.gov/research/still-pictures/permissions) clarifies federal works may be public domain in the U.S., but NARA holdings also include rights-restricted materials. **Catalog record presence is not a reuse license; inspect item provenance before importing media.**
4. **Library of Congress**: the indexed [1912 *Titanic* report (LCCN 2025847774)](https://www.loc.gov/item/2025847774/) describes a 1912 U.S. Congressional Serial Set printing (S. Doc. 62-933) and says the vast majority of that series is U.S. government work, while reprinted third-party rights may vary. Direct page gave a research-client 403; **use only a link, not copied scans**.
5. **UK National Archives**: the merchant crew/log guidance is indexed and describes sampled surviving crew lists. Direct access returned 403; **do not infer the page or its record series is gone**. For reuse check UK item-level or Crown Copyright terms. Link only.
6. **TitanicInquiry.org**: third-party transcriptions of historical testimony and report excerpts were retrieved; **link and cite carefully, do not copy full transcriptions or treat them as the original manuscript**. The Memorial University scan supplies independent contemporary-report comparison.
7. **NOAA/NGS and NHHC sources**: government agency web pages are linked, with no charts or images downloaded. The NHHC pages need independent ordinary-browser reachability testing because the research client timed out or received 502.

## Priority follow-ups before release

**P0:** Actual authenticated WordPress production-theme screenshots for each of nine child pages at 320 / 390 / 768 / 1440, plus keyboard focus, screen-reader, interactive worksheet, mobile overflow and print QA. [Site QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) owns the browser remedy; this register does not purport to close that gate.

**P0:** Confirm that `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false` can be enforced *on each first-publication transaction*, with independent no-email/no-social readback. Newsletter default=false is insufficient. Hold public nav/card updates and publication until this is proved.

**P1:** In an ordinary unrestricted browser, check exact [NARA Catalog ID 285104169](https://catalog.archives.gov/id/285104169), [ID 4719508](https://catalog.archives.gov/id/4719508), [LOC item 2025847774](https://www.loc.gov/item/2025847774/), and the [UK TNA merchant guide](https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/merchant-navy-ships-records-crew-lists-musters-and-log-books/); confirm correct target identity and accessibility, not merely a generic site shell. Review the three NHHC pages as well.

**P1:** Recheck FV internal crosslinks that returned transient 429/disabled research access via ordinary browser, verify HTTP 200, canonical, no accidental moved slugs, and keep publication release dependency ordering so cross-guide links do not point at unpublished siblings.

**P1:** Audit each published page's visible images, media, outbound links, canonical, SEO metadata and absence of old unpublished preview IDs. Re-verify the serialized post SHA after any edit.

**Grok (planning only):** The educational short can compare *a ship log that is absent*, *a crew member absent from a log*, and *a wireless warning never delivered to the captain*. No cross-posting or account access until Library material is live and provenance-complete.

## Complete absolute URL register

**Rightmost policy field is a conservative handling category, not a declaration of copyright ownership or license clearance.**

| # | Destination | Research access result | Referencing draft IDs | Conservative rights posture |
|---:|---|---|---|---|
| 1 | [catalog.archives.gov/](https://catalog.archives.gov/) | SHELL_ONLY | 2887 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 2 | [catalog.archives.gov/id/285104169](https://catalog.archives.gov/id/285104169) | UNAVAILABLE_DIRECT | 2886, 2887, 2888 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 3 | [catalog.archives.gov/id/4719508](https://catalog.archives.gov/id/4719508) | UNAVAILABLE_DIRECT | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 4 | [dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf](https://dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf) | CONTENT_RETRIEVED | 2893 | CC_BY_NC_ND_PLATFORM_NOTICE_LINK_ONLY |
| 5 | [dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf#page=31](https://dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf#page=31) | PDF_BASE_AND_TARGET_PAGE_VISUALLY_CHECKED | 2893 | CC_BY_NC_ND_PLATFORM_NOTICE_LINK_ONLY |
| 6 | [dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf#page=32](https://dai.mun.ca/PDFs/cns_tools/ShippingCasualtiesLossOfTheSteamshipTitanic.pdf#page=32) | PDF_BASE_AND_TARGET_PAGE_VISUALLY_CHECKED | 2893 | CC_BY_NC_ND_PLATFORM_NOTICE_LINK_ONLY |
| 7 | [dai.mun.ca/about](https://dai.mun.ca/about) | CONTENT_RETRIEVED | 2893 | CC_BY_NC_ND_PLATFORM_NOTICE_LINK_ONLY |
| 8 | [dai.mun.ca/help](https://dai.mun.ca/help) | CONTENT_RETRIEVED | 2893 | CC_BY_NC_ND_PLATFORM_NOTICE_LINK_ONLY |
| 9 | [finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/](https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/) | RATE_LIMIT_429 | 2889, 2890, 2892, 2893 | FV_EXISTING_CROSSLINK_ONLY |
| 10 | [finalvestige.com/contact/](https://finalvestige.com/contact/) | CONTENT_RETRIEVED | 2889, 2890, 2891, 2892 | FV_EXISTING_CROSSLINK_ONLY |
| 11 | [finalvestige.com/editorial-standards/](https://finalvestige.com/editorial-standards/) | CONTENT_RETRIEVED | 2886, 2887, 2888, 2890, 2891, 2893 | FV_EXISTING_CROSSLINK_ONLY |
| 12 | [finalvestige.com/free-resources/](https://finalvestige.com/free-resources/) | CONTENT_RETRIEVED | 2892, 2893, 2894 | FV_EXISTING_CROSSLINK_ONLY |
| 13 | [finalvestige.com/free-resources/research-sources/](https://finalvestige.com/free-resources/research-sources/) | RATE_LIMIT_429 | 2893, 2894 | FV_EXISTING_CROSSLINK_ONLY |
| 14 | [finalvestige.com/free-resources/the-box-behind-the-citation/](https://finalvestige.com/free-resources/the-box-behind-the-citation/) | RESEARCH_CLIENT_DISABLED | 2888 | FV_EXISTING_CROSSLINK_ONLY |
| 15 | [finalvestige.com/free-resources/the-same-story-twice/](https://finalvestige.com/free-resources/the-same-story-twice/) | RATE_LIMIT_429 | 2887 | FV_EXISTING_CROSSLINK_ONLY |
| 16 | [finalvestige.com/the-archive-trail/](https://finalvestige.com/the-archive-trail/) | CONTENT_RETRIEVED | 2886, 2887, 2889, 2890, 2891, 2893, 2894 | FV_EXISTING_CROSSLINK_ONLY |
| 17 | [finalvestige.com/the-last-fix/](https://finalvestige.com/the-last-fix/) | RESEARCH_CLIENT_DISABLED | 2886, 2891 | FV_EXISTING_CROSSLINK_ONLY |
| 18 | [finalvestige.com/the-moving-noon/](https://finalvestige.com/the-moving-noon/) | CONTENT_RETRIEVED | 2886, 2887, 2888, 2891 | FV_EXISTING_CROSSLINK_ONLY |
| 19 | [historicalcharts.noaa.gov/](https://historicalcharts.noaa.gov/) | CONTENT_RETRIEVED | 2891 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 20 | [nauticalcharts.noaa.gov/updates/how-accurate-are-nautical-charts/](https://nauticalcharts.noaa.gov/updates/how-accurate-are-nautical-charts/) | CONTENT_RETRIEVED | 2891 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 21 | [text-message.blogs.archives.gov/2013/12/02/know-your-records-u-s-navy-muster-rolls-and-personnel-diaries/](https://text-message.blogs.archives.gov/2013/12/02/know-your-records-u-s-navy-muster-rolls-and-personnel-diaries/) | CONTENT_RETRIEVED | 2890 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 22 | [www.archives.gov/boston/finding-aids/maritime.html](https://www.archives.gov/boston/finding-aids/maritime.html) | CONTENT_RETRIEVED | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 23 | [www.archives.gov/kansas-city/finding-aids/html/rg36-series-title-list.html](https://www.archives.gov/kansas-city/finding-aids/html/rg36-series-title-list.html) | CONTENT_RETRIEVED | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 24 | [www.archives.gov/personnel-records-center/ompf-access-public](https://www.archives.gov/personnel-records-center/ompf-access-public) | CONTENT_RETRIEVED | 2890 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 25 | [www.archives.gov/research/guide-fed-records/groups/036.html](https://www.archives.gov/research/guide-fed-records/groups/036.html) | CONTENT_RETRIEVED | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 26 | [www.archives.gov/research/maritime/merchant-vessel-documentation](https://www.archives.gov/research/maritime/merchant-vessel-documentation) | CONTENT_RETRIEVED | 2888, 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 27 | [www.archives.gov/research/maritime/vessel-documents.html](https://www.archives.gov/research/maritime/vessel-documents.html) | CONTENT_RETRIEVED | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 28 | [www.archives.gov/research/military/logbooks/digitized-logs](https://www.archives.gov/research/military/logbooks/digitized-logs) | CONTENT_RETRIEVED | 2886, 2887, 2888, 2891, 2894 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 29 | [www.archives.gov/research/military/logbooks/merchant-vessels-old.html](https://www.archives.gov/research/military/logbooks/merchant-vessels-old.html) | CONTENT_RETRIEVED | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 30 | [www.archives.gov/research/military/logbooks/merchant-vessels.html](https://www.archives.gov/research/military/logbooks/merchant-vessels.html) | CONTENT_RETRIEVED | 2886, 2887 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 31 | [www.archives.gov/research/military/logbooks/naval-deck-logs](https://www.archives.gov/research/military/logbooks/naval-deck-logs) | CONTENT_RETRIEVED | 2886, 2887, 2888, 2889, 2892, 2894 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 32 | [www.archives.gov/research/military/logbooks/navy-deck-log-exemptions](https://www.archives.gov/research/military/logbooks/navy-deck-log-exemptions) | CONTENT_RETRIEVED | 2886, 2887 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 33 | [www.archives.gov/research/military/logbooks/navy-deck-logs-1941-1959](https://www.archives.gov/research/military/logbooks/navy-deck-logs-1941-1959) | CONTENT_RETRIEVED | 2889, 2890, 2894 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 34 | [www.archives.gov/research/military/logbooks/navy-deck-logs-1960-1978](https://www.archives.gov/research/military/logbooks/navy-deck-logs-1960-1978) | CONTENT_RETRIEVED | 2889 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 35 | [www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs](https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs) | CONTENT_RETRIEVED | 2886, 2887, 2889, 2890, 2891, 2894 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 36 | [www.archives.gov/research/military/logbooks/navy-online](https://www.archives.gov/research/military/logbooks/navy-online) | CONTENT_RETRIEVED | 2886, 2887, 2888, 2889, 2890, 2891 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 37 | [www.archives.gov/research/military/logbooks/noaa-vessels.html](https://www.archives.gov/research/military/logbooks/noaa-vessels.html) | CONTENT_RETRIEVED | 2891 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 38 | [www.archives.gov/research/military/logbooks/other-logs](https://www.archives.gov/research/military/logbooks/other-logs) | CONTENT_RETRIEVED | 2889, 2894 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 39 | [www.archives.gov/research/military/logbooks/rg45.html](https://www.archives.gov/research/military/logbooks/rg45.html) | CONTENT_RETRIEVED | 2893 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 40 | [www.archives.gov/research/military/logbooks/weather](https://www.archives.gov/research/military/logbooks/weather) | CONTENT_RETRIEVED | 2889 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 41 | [www.archives.gov/research/military/navy/muster-rolls](https://www.archives.gov/research/military/navy/muster-rolls) | CONTENT_RETRIEVED | 2890 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 42 | [www.archives.gov/research/still-pictures/permissions](https://www.archives.gov/research/still-pictures/permissions) | CONTENT_RETRIEVED | 2886, 2887, 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 43 | [www.archives.gov/san-francisco/finding-aids/holdings-guide-02.html](https://www.archives.gov/san-francisco/finding-aids/holdings-guide-02.html) | CONTENT_RETRIEVED | 2892 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 44 | [www.archives.gov/veterans/military-service-records](https://www.archives.gov/veterans/military-service-records) | CONTENT_RETRIEVED | 2890 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 45 | [www.capeannmuseum.org/media/library_and_archives_finding_aids/a18_-_ships_log_book_collection_finding_aid.pdf](https://www.capeannmuseum.org/media/library_and_archives_finding_aids/a18_-_ships_log_book_collection_finding_aid.pdf) | CONTENT_RETRIEVED | 2886 | MUSEUM_PERMISSION_REQUIRED_FOR_REPRODUCTION |
| 46 | [www.history.navy.mil/about-us/services-and-policies/scan-copyright.html](https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html) | TIMEOUT | 2888 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 47 | [www.history.navy.mil/research/histories/ship-histories/danfs/a/abbot-dd-184-i.html](https://www.history.navy.mil/research/histories/ship-histories/danfs/a/abbot-dd-184-i.html) | GATEWAY_502 | 2888 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 48 | [www.history.navy.mil/research/histories/ship-histories/danfs/a/abbot-dd-629-ii.html](https://www.history.navy.mil/research/histories/ship-histories/danfs/a/abbot-dd-629-ii.html) | TIMEOUT | 2888 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 49 | [www.loc.gov/item/2025847774/](https://www.loc.gov/item/2025847774/) | INDEX_ONLY_403 | 2893 | GOV_PUBLICATION_MIXED_ORIGIN_ITEM_CHECK |
| 50 | [www.nationalarchives.gov.uk/help-with-your-research/research-guides/merchant-navy-ships-records-crew-lists-musters-and-log-books/](https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/merchant-navy-ships-records-crew-lists-musters-and-log-books/) | INDEX_ONLY_403 | 2886 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 51 | [www.ngs.noaa.gov/NCAT/](https://www.ngs.noaa.gov/NCAT/) | CONTENT_RETRIEVED | 2891 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 52 | [www.ngs.noaa.gov/datums/faq.shtml](https://www.ngs.noaa.gov/datums/faq.shtml) | CONTENT_RETRIEVED | 2891 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 53 | [www.senate.gov/about/powers-procedures/investigations/titanic.htm](https://www.senate.gov/about/powers-procedures/investigations/titanic.htm) | CONTENT_RETRIEVED | 2893 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |
| 54 | [www.titanicinquiry.org/BOTInq/BOTInq14Boxhall01.php](https://www.titanicinquiry.org/BOTInq/BOTInq14Boxhall01.php) | CONTENT_RETRIEVED | 2893 | THIRD_PARTY_TRANSCRIPTION_LINK_ONLY |
| 55 | [www.titanicinquiry.org/BOTInq/BOTInq21Adams01.php](https://www.titanicinquiry.org/BOTInq/BOTInq21Adams01.php) | CONTENT_RETRIEVED | 2893 | THIRD_PARTY_TRANSCRIPTION_LINK_ONLY |
| 56 | [www.titanicinquiry.org/BOTInq/BOTReport/botRepMessages.php](https://www.titanicinquiry.org/BOTInq/BOTReport/botRepMessages.php) | CONTENT_RETRIEVED | 2893 | THIRD_PARTY_TRANSCRIPTION_LINK_ONLY |
| 57 | [www.visitthecapitol.gov/artifact/s-6412-act-regulate-radio-communication-radio-act-1912-may-20-1912](https://www.visitthecapitol.gov/artifact/s-6412-act-regulate-radio-communication-radio-act-1912-may-20-1912) | CONTENT_RETRIEVED | 2893 | GOV_OR_GOV_ARCHIVE_LINK_ONLY_ITEM_CHECK_IF_REUSED |

## Interpretation and editorial standard

A returned 403, 429, disabled fetch, or timeout can arise from client restriction or rate limiting. It cannot be silently rewritten as "dead link." A searchable catalog title is not proof that underlying record pages were examined. Likewise, the existence of a public-domain government report does not automatically authorize reuse of a particular institutional scan or a third-party transcription. This preserves the distinction required by [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/) between the documentary record, inference, and unknowns.

**Method limits:** Live public-web fetches and image inspection were performed November 18; WordPress readbacks authenticated and checked status/parent/noindex. No browser automation or HTML render of the editor-authenticated drafts; no real keyboard/screen-reader/print/JS acceptance; no direct institutional access to the blocked records; no publication, new spending, email or social account action.
