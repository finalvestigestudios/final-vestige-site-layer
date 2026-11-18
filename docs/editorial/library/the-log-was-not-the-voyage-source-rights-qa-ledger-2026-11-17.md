# Final Vestige Library — *The Log Was Not the Voyage*
**Editorial and release ledger | 2026-11-17 Pacific | HOLD — DO NOT PUBLISH**

## Coordination / scope
Checked live Library \`/free-resources/\`, Editorial Standards, Research Sources and all 74 published/draft child-page entries, plus GitHub Library issues (including #1589, #1788, #1724, #2879, #2138, #1705) and recent draft PRs. No child page or coordination issue specifically addresses the **custody route and interpretive differences between Navy deck logs, U.S. merchant statutory/operating logs, British merchant logs, and privately held navigational journals**. This is separate from The Moving Noon (timekeeping), The Last Fix (field navigation), The Archive Trail (general primary-source research), and Library #2280 The Name on the Stern (vessel identity).

New WordPress **draft #2870**, parent #77, slug \`the-log-was-not-the-voyage\`; noindex=true, comments closed. New isolated GitHub branch \`review/library-log-was-not-voyage-20261117\`. No published Library/nav, WordPress theme, homepage, Preparedness, Investigations, Dispatch, subscribers, or Grok accounts changed.

## Deliverable
- Original, Gutenberg-ready **25,725-character** field guide with 4-way source-route table, six-pass archive method, explicitly qualified 1951 *USS Abbot* catalog discovery example, missing-file interpretation, source/access ledger, print styles, keyboard-focusable comparison table, and original illustrated SVG with accessible title/description.
- Private, local-only **eight-field route receipt** for vessel identity, year, jurisdiction, clock basis, research question, exact catalog URL and access/rights caveats. Copy, local TXT download and clear controls; no network, cookies, localStorage, API or analytics. A no-JS printable workflow survives.
- Dynamic output is a **research lead**, not a claim of custody, availability, authenticity, image access or an actual historic voyage.
- No archival images, pages, photographs, excerpts, maps, logos, or videos reproduced. FV owns only the new text, design, schematic and code; linked archival source rights remain with their custodians/rightsholders.

## Source/provenance register
All below checked against web results **2026-11-17** unless stated. Access states are literal, not presumed.

| Authority / record | Exact URL | Verified support / qualification | Access and reuse |
|---|---|---|---|
| NARA Navy deck-log introduction, institutional review 2023-03-28 | https://www.archives.gov/research/military/logbooks/naval-deck-logs | Official purpose; commissioned ship and 24-hour day; generally 1940− Archives I, 1941+ Archives II, exceptions | HTML opened; link-only |
| NARA digitized Navy month index | https://www.archives.gov/research/military/logbooks/navy-online | *Abbot* DD-629 February 1951 indexed to https://catalog.archives.gov/id/285104169 | Official index inspected; catalog destination HTML/JS shell only, **NO image/record contents verified** |
| NARA digitized deck-log search | https://www.archives.gov/research/military/logbooks/digitized-logs | Search without USS prefix, with Deck Log, hull/year; staged access | HTML opened; link-only |
| NARA U.S. merchant logs, institutional review 2016-08-15 | https://www.archives.gov/research/military/logbooks/merchant-vessels.html | Official versus operating logs; RG 41, 26, 178; port and number routes | HTML opened; link-only |
| The National Archives (UK) merchant ships guide | https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/merchant-navy-ships-records-crew-lists-musters-and-log-books/ | Crew agreements, BT series, uneven survival; supporting search excerpt | Search retrieved; direct open **403**; manual reader QA required; link-only |
| Cape Ann Museum A18 Ships Log Book Collection, undated finding aid pp. 1–2 | https://www.capeannmuseum.org/media/library_and_archives_finding_aids/a18_-_ships_log_book_collection_finding_aid.pdf | Collection-specific historical noon-day and observation/DR cautions; 73 logbooks, dates 1751–1935 | PDF text **and page screenshots** inspected; collection specifically requests permission from Librarian/Archivist to publish content; **no reproduction** |
| NARA what deck logs exclude, institutional review 2022-02-03 | https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs | No full off-ship assignment, day-to-day work, individual aircraft movement | HTML opened; link-only |
| NARA missing, classified and withdrawn logs | https://www.archives.gov/research/military/logbooks/navy-deck-log-exemptions | Different absence/access reasons; custodians and request identifiers | HTML opened; link-only |
| NARA permissions | https://www.archives.gov/research/still-pictures/permissions | U.S. government material versus private/third-party holdings rights | HTML opened; link-only |
| Related FV published pages | https://finalvestige.com/the-moving-noon/ ; https://finalvestige.com/the-last-fix/ ; https://finalvestige.com/the-archive-trail/ ; https://finalvestige.com/editorial-standards/ | Cross-links from existing public FV pages | All live in web retrieval |

**Critical source distinction:** Cape Ann's collection-specific description of noon-to-noon days cannot be generalized to every ship, decade or Navy deck log. No automatic clock conversion is offered.

## Independent WordPress / GitHub QA
- WP \`GET edit #2870\`: **draft**, parent **77**, noindex **true**, modified \`2026-11-17T14:39:12\`; content **25,725 chars**.
- GitHub \`fetch_file\` on isolated branch: **byte-for-byte equal** to WordPress content, blob SHA \`389b9897361078402b87aa0ccae553e6887bba9a\`.
- **18 DOM IDs / 18 unique**, accessible SVG title+description, scope-prefixed CSS, 560px mobile and print media rules, keyboard-focusable overflow table, no-JS fallback, no network/storage JS APIs found by static scan.
- **18 external and internal link occurrences / 14 distinct**; presence in markup does not prove live access or publication rights. The UK guide and JS-rendered NARA catalog still require ordinary-reader verification.
- Public Library #77 \`publish\`, modified \`2026-11-07T19:39:01\`; Research Sources #1338 \`publish\`, modified \`2026-11-03T22:12:43\`; **unchanged**.
- Anonymous draft URL inaccessible through web retrieval, as expected for an unpublished item. This is **not** a fully characterized HTTP/browser 404.
- **NOT PASSED / NOT CLAIMED:** production WordPress-theme visual/pixel inspection at **320/390/768/1440**, actual keyboard+screen reader behavior, end-to-end copy/download/clear in production, external item/catalog image preview, subscriber/social suppression on first publication, automatic public metadata/canonical checks. Static HTML/API readback is not browser acceptance.

## Required before release
1. Authenticated in-theme Preview and screenshots at 320, 390, 768, 1440; check no horizontal page overflow, SVG legibility/description, no obstructive newsletter overlay, focus order/table keyboard scroll, print and reduced-motion behavior.
2. Exercise route generator across 4 jurisdictions, bad year, missing values, copy, download and reset in the actual WordPress page context; ensure JS policy permits the script and no console/network errors.
3. Verify The National Archives UK link with an ordinary browser and explicitly qualify any persistent access barrier. Inspect *Abbot* NARA catalog item only if making content claims; otherwise the qualified index-only example may stay.
4. Independently establish **first-publish email/social suppression**: \`_jetpack_dont_email_post_to_subs=true\` and \`jetpack_publicize_feature_enabled=false\` before status becomes publish. Current page connector does not expose those keys as writable meta. Do not guess.
5. Only after all gates, publish existing #2870, verify unauthenticated 200/canonical/meta/site CSS/source health, then add one minimal scoped card to Library #77. Preserve all other entries.
6. Grok promotional route (concept only): “A ship's log can be missing from your search and still be sitting in an archive. What exactly did you ask for?” Use original diagram, no documentary scan claims, only after live URL.

## Decision
**HOLD.** Do not merge PR or publish page or newsletter/social. No paid spend, no third-party asset copying.

---

## 2026-11-17 15:38 PT — Second-pass annex: *A Missing Log Has More Than One Meaning*

**Scope / reason.** First reviewed current public Library and Editorial Standards; authenticated WordPress listing shows 74 published/draft children. Reviewed GitHub coordination #2923 and draft PR #2922, plus the other Library work visible in PR/issue search. Avoided creating a duplicative child page: the second-pass instrument is one *new, separate Gutenberg HTML block* appended to existing draft #2870, preserving its first block. It addresses the distinct demand of **what to do when the archive returns no logbook**.

**Reader deliverable.** A 2,014-word, 22,015-character original annex with:
- seven evidence statuses presented as keyboard-native disclosure sections, with an actionable next question and direct NARA reference in each;
- an accessible original four-step analytical SVG that distinguishes record identity, public access, institutional custody, and relevance, not archival documentation;
- a four-row evidence-claim strength comparison;
- two adaptable archive inquiry scripts (Navy and U.S. merchant);
- an eight-line printable *Not Found Evidence Receipt* recording search terms, custody contacts, holdings response, limitations, next source, and rights;
- explicit index-only example for USS *Abbot* DD-629 February 1951, without making claims about uninspected scanned pages.

**Verified source ledger (last rechecked November 17, 2026):**
1. NARA, *Introduction to Navy Deck Logs*: https://www.archives.gov/research/military/logbooks/naval-deck-logs — commissioned/in-service distinction; NARA Washington vs College Park date boundary **with exceptions**. Web HTML accessed, direct link, no reproductions.
2. NARA, *Digitized Deck Logs*: https://www.archives.gov/research/military/logbooks/digitized-logs — search without USS prefix; incomplete indexed/catalog digitization; privacy review of later years. Web HTML accessed; no guarantee a given item has images.
3. NARA, *Classified, Withdrawn, and Missing Deck Logs*: https://www.archives.gov/research/military/logbooks/navy-deck-log-exemptions — distinct states, different reference/FOIA paths and missing volume limitations; institutional reviewed February 3, 2022. Web HTML accessed; **never assume a specific volume is missing/withheld**.
4. NARA, *Information NOT Included in Deck Logs*: https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs — off-ship events, aircraft manifests, day-to-day work, detailed yard repairs; reviewed February 3, 2022. Web HTML accessed.
5. NARA, *Logbooks of US Merchant Vessels*: https://www.archives.gov/research/military/logbooks/merchant-vessels.html — statutory/operating/engineering logs; RG 41, RG 26, RG 178 differ by purpose and arrangement. Web HTML accessed; do not conflate survival of series.
6. NARA, *Navy Deck Logs Available in the National Archives Catalog*: https://www.archives.gov/research/military/logbooks/navy-online — *Abbot* DD-629 February 1951 month entry linked to catalog ID 285104169. Web HTML accessed; **catalog scan pixels not inspected**.
7. NARA, *Copyright and Permissions*: https://www.archives.gov/research/still-pictures/permissions — federal government works usually public domain in US, but NARA holdings contain private/right-restricted materials; item-level reuse needed. No third-party image copied.
8. FV site links: \`/the-archive-trail/\` and \`/free-resources/the-same-story-twice/\` public HTML opened Nov 17; \`/the-moving-noon/\` received HTTP 429 from web client on this particular verification attempt (previous live checks in first-pass ledger). 429 is **not evidence that readers see an error**.

**Image rights:** One new original author-drawn, date-stamped SVG explanatory flow diagram only; author/owner Final Vestige Studios, created 2026-11-17, original source within GitHub annex file. Descriptive \`<title>\`, \`<desc>\`, caption and explicit illustrative—not archival—label. No archival scans, photos, logos or third-party videos reproduced. Original prose, HTML/CSS and worksheet are FV-created; linked sources remain under their own access/reuse terms.

**Static preflight:** 14/14 checks passed before write: unique IDs (5/5); absolute URLs; accessible SVG; seven \`<details open>\` sections; eight printable ruled fields; one \`<section>\`; print + 560px mobile CSS; no embedded external image; no JavaScript; institutional NARA links; dated source ledger; scrollable table; scoped CSS. **This is structural QA, not a browser or screen-reader result.**

**Write + independent readback:** GitHub companion file:
\`docs/editorial/library/the-log-was-not-the-voyage-missing-log-evidence-desk-2026-11-17.html\`, branch \`review/library-log-was-not-voyage-20261117\`, commit \`26581052aa4787183a1c5bae4cda55c8b98ec8e6\`. Used \`wpcom-page-sections-insert\` with exact \`modified/content_hash\` optimistic tokens, appended at index 1 to draft #2870. WP reported no stripping/warnings. Authenticated re-read:
- page #2870 \`draft\`, parent #77, \`jetpack_seo_noindex=true\`, modified \`2026-11-17T15:37:49\`;
- 47,775 character raw content total; first block hash **unchanged** \`0c83c5133fe85a1bb1e94e2cc125a97a9695a999\`; now 2 blocks;
- second block **exact string present** matching GitHub (22,050 characters including Gutenberg wrapper).
- new block hash \`c8dff9a37a03896f23d655fcc1193692321299b0\`, GitHub blob \`71e35f9659277a38aa759450927fbb80bcff39da\`.
- Public Library #77 \`publish\` unchanged since 2026-11-07T19:39:01, Research Sources #1338 unchanged since 2026-11-03T22:12:43; public Library read as HTTP 200 and canonical \`/free-resources/\`.

**RELEASE HOLD unchanged:** The WP production-theme preview at 320/390/768/1440, visual pixel review, real keyboard/screen-reader acceptance, signed-out preview behavior of the draft, item-level external access/accessibility, and reliable \`_jetpack_dont_email_post_to_subs=true\` plus social auto-publish suppression are not independently demonstrated. Because those conditions are not met, the annex is saved **only in draft**, no Library card/nav/other public page modified, no subscriptions or Grok account touched. Do not merge or change status until verified.


## Addendum — 2026-11-17, 16:35–16:40 Pacific: two-hull archival cross-check

**New companion:** [The Name Is Not the Ship's Record](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/review/library-log-was-not-voyage-20261117/docs/editorial/library/the-log-was-not-the-voyage-abbot-case-study-2026-11-17.html). Added on existing branch/PR #2922 and appended to **WordPress draft page 2870 as third independent core/html block**. Preserves all prior block content. This is not a duplicate of existing Library resource `The Name on the Stern` (draft #2280), whose remit is general vessel identity: this worked example asks **what a specific NARA logbook index heading permits us to claim when an official service chronology differs within the same month**. No public website changes.

**Verified institutional anchors, last checked 2026-11-17:**
1. Naval History and Heritage Command, DANFS, *Abbot I (Destroyer No. 184)* — `https://www.history.navy.mil/research/histories/ship-histories/danfs/a/abbot-dd-184-i.html`. Navy historical account of 1919 commissioning, 1940 transfer and renaming `Charlestown`. Search-result/indexed institutional text was accessible; direct source retrieval returned intermittent HTTP 502/timeout. **Ordinary-browser read remains outstanding**; no quote was lifted.
2. Naval History and Heritage Command, DANFS, *Abbot II (DD-629)* — `https://www.history.navy.mil/research/histories/ship-histories/danfs/a/abbot-dd-629-ii.html`. Navy history gives recommissioning 26 February 1951. Same direct-access qualification.
3. NARA, *Navy Deck Logs Available in National Archives Catalog* — `https://www.archives.gov/research/military/logbooks/navy-online`. Page explicitly indexes Abbot DD-629, February 1951. Independently opened, including the 'A' heading and the ship/month listing; NARA catalog locator `https://catalog.archives.gov/id/285104169` is **not** evidence that every underlying image was reviewed.
4. NARA, *Digitized Deck Logs* — `https://www.archives.gov/research/military/logbooks/digitized-logs`. Specific catalog query instructions; online coverage is progressive.
5. NARA, *An Introduction to Navy Deck Logs* — `https://www.archives.gov/research/military/logbooks/naval-deck-logs`. Records purpose, monthly title page and classification of in-service versus commissioned vessels.
6. NARA, *Merchant Vessel Documentation* — `https://www.archives.gov/research/maritime/merchant-vessel-documentation`. Merchant official-number research context; not interchangeable with Navy hull number.
7. NHHC, *Scanning, Copyright & Citation* — `https://www.history.navy.mil/about-us/services-and-policies/scan-copyright.html`. Official U.S. government documents/images generally public domain, but private/donated items vary; therefore this new material is link-only.

**Evidence boundary:** Two distinct naval vessels named Abbot, hull identities 184 and 629, different service dates. February 1951 is a cataloged month for DD-629, while the Navy's account says it was recommissioned on February 26. Do **not** interpret this as a contradiction proven by the original deck-log pages: actual daily pages are not examined and earlier-day contents are not asserted. The drawn two-lane chronology is conceptual, non-linear in scale, original FV SVG, has a screen-reader title and description, and contains no archival image or AI-generated reconstruction.

**QA evidence:** source contains 16137 characters; exact GitHub HTML was found in authenticated WordPress edit-context raw content as a complete substring. Draft status/noindex verified, three sections, no prior blocks touched; current WordPress modified `2026-11-17T16:35:24`. 12 source-level structural assertions passed before write: one Gutenberg html block, unique IDs, SVG accessible description, scoped style, 570px CSS breakpoint, print rules, keyboard-focusable responsive table, eight-plus institutional source links, explicit evidence qualifications, no script or third-party images. Actual 320/390/768/1440 production-theme layout, screen-reader/keyboard operation, and first-publish email/automatic social suppression **not tested**. Do not publish/merge, no Library navigation or other editorial area changes. Rights remain link-only for institutional resources; original graphics/text FV-owned.


### Post-write independent public-page and notification checks — 16:37 Pacific
- WordPress visitor-facing renderer: unpublished `https://finalvestige.com/?page_id=2870` returns **HTTP 404**; expected for a draft, not a published resource.
- Published `https://finalvestige.com/free-resources/` returns **HTTP 200**, canonical matches path; published `https://finalvestige.com/free-resources/research-sources/` returns **HTTP 200**, canonical matches path. Public pages were read-only in this operation.
- WordPress Newsletter `get_settings` currently reports `subscriptions=true` and `email_new_posts_by_default=false`. This is **not** equivalent to demonstrated post-specific `_jetpack_dont_email_post_to_subs=true` nor proof that automatic social publishing is disabled; do not launch based on default alone.
- NARA Catalog ID 285104169 resolved to the NARA catalog URL; dynamic viewer supplied no item text/images to the inspection client. The 'Abbot (DD-629) → February 1951' listing is therefore anchored to the independently fetched **NARA index**, not an examination of the PDF/images in the catalog.
- Public page renderer found the existing Research Sources descriptions inconsistent (visible 60 versus SEO 90). This is already owned by GitHub issue #1788; no overlapping edits made.
- Browser visual tests against the draft's **production theme** remain impossible via signed-out page because it is a draft, and the source was not independently rendered with browser at four widths. **Release HOLD unchanged.**
