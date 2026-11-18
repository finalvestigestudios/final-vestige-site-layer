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


## Addendum — 2026-11-17, 17:32–17:39 Pacific: Three Pages. One Day. Three Different Witnesses

**Work delivered:** original 1,751-word field instrument `the-log-was-not-the-voyage-three-pages-one-day-2026-11-17.html`, with a custom vector infographic distinguishing monthly title, daily remarks and columnar/weather pages; a seven-pass archive reading workflow; five-row claim-strength matrix; 14-field printable single-entry witness card; seven linked U.S. National Archives research guides. The explanatory SVG is **not an archival scan or reconstruction of a real log**. No borrowed photos, logos, original logbook sheets, third-party graphics, or audio/video were uploaded. New content remains in WordPress **draft page 2870** in the **fourth** `core/html` block, under published Library parent 77; no public nav/card or other editorial section changed.

**Independently opened source and rights trail, last checked 2026-11-17:**
- NARA, *An Introduction to Navy Deck Logs*: https://www.archives.gov/research/military/logbooks/naval-deck-logs . Agency editorial guidance, not direct evidence of a particular ship's voyage. Provides purpose, basic format, 24-hour remarks chronology, title-page incompleteness and physical custody caveats.
- NARA, *1941–1959 Deck Logs*: https://www.archives.gov/research/military/logbooks/navy-deck-logs-1941-1959 . Authority for typical three-part monthly-title/daily-remarks/daily-columnar format, officer lists through spring 1956, and variable fullness; institutional last-reviewed 2023-03-28.
- NARA, *Columnar Pages & Weather Research*: https://www.archives.gov/research/military/logbooks/weather . Weather observations and discontinuation of separate sheets in 1965; institutional last-reviewed 2022-02-03.
- NARA, *1960–1978 Deck Logs*: https://www.archives.gov/research/military/logbooks/navy-deck-logs-1960-1978 . Format transition: truncated in-line columns in 1960–1964 and changed layout from 1965; period qualifiers are essential.
- NARA, *Other Logs*: https://www.archives.gov/research/military/logbooks/other-logs . Rough vs smooth terminology and signed corrections, plus other logs' retention limits. Do not infer fraudulent intent from differences.
- NARA, *Information NOT Included in Deck Logs*: https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs . Limits on people and off-ship activities; silence is not evidence of absence.
- NARA, *Navy Deck Logs Available in National Archives Catalog*: https://www.archives.gov/research/military/logbooks/navy-online . Index/discovery only. **No original individual deck-log page image was independently reviewed** for this chapter.

**Cross-links and rights:** Published https://finalvestige.com/the-archive-trail/ and https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/ opened successfully; source text warns not to apply modern U.S. Navy form rules to the older Franklin expedition. Corrections URL was initially written incorrectly (`/corrections-contact/`, inaccessible), identified in link review and corrected to the live https://finalvestige.com/contact/ **in both GitHub and WordPress before completion**. Original vector diagram and worksheet: author/publisher Final Vestige Studios, 2026-11-17, original source path in same GitHub HTML companion, editorial work owned by FV; no third-party license required; no permission to relicense archival items implied. Caption and SVG `title`/`desc` identify it as explanatory. No third-party assets reproduced. NARA's preservation of a record alone never establishes public-domain rights for a separately authored object: reuse must be evaluated at item level before any later image addition.

**Structural QA and readback:**
- Pre-write 10/10 assertions passed: single Gutenberg HTML block, unique element IDs, fully scoped CSS, accessible original SVG description, accessible horizontal-scroll table, 560px/mobile breakpoint and print rules, seven-plus institutional URLs, specific reuse qualifications, relevant internal links, no third-party image or remote script.
- Added block length 18,792 characters after correcting contact link; 1,751 approximate visible words (source-level estimate, not a production rendering count).
- GitHub blob `1a7105e9d99c8e911c072310ad5c921b71822926`; WordPress raw edit-content has an exact substring match of this complete committed block. WP total 82,704 characters, section count four, modified `2026-11-17T17:37:32`, final new block hash `46d309601b1cb88454d9069d10802041b2d9ed0e`.
- The three preceding block hashes were retained unchanged: `0c83c5133fe85a1bb1e94e2cc125a97a9695a999`, `c8dff9a37a03896f23d655fcc1193692321299b0`, `cbb84af92b52b10b0e988b0481685994ff211eba`.
- Draft status/noindex/parent confirmed; signed-out `/?page_id=2870` returns HTTP 404 as intended; published Library #77 modification still `2026-11-07T19:39:01`, published Research Sources #1338 `2026-11-03T22:12:43`. No public changes.
- Real production WordPress theme pixel QA at widths 320, 390, 768, 1440, keyboard screen-reader review, visual overflow/contrast checks, and publication-specific email/social suppression **not verified**. No release permitted. This is a source-level review, not a passed browser/accessibility sign-off.

**Pending gate:** Finish actual visual and assistive tests using an authenticated draft preview or equivalent production-theme browser, verify notification suppression including the requested `_jetpack_dont_email_post_to_subs=true` behavior and automatic social posting, and inspect record images only if making page-level historical claims. Only then publish and create a carefully scoped Library navigation card. Existing shared QA gate #1589 remains the appropriate coordination route. Optional Grok concept after release: *Three log pages, three different questions*; no social-account action authorized.


## 2026-11-17 18:43 PT — The Sailor Was Not in the Log

**Scope and motivation.** Existing five-block Library draft #2870 now includes a reader-facing **crew-record witness** module to address a discrete problem: locating naval service members when deck logs do not name them. This is a companion to, not a rewrite of, the vessel-identity, missing-log and log-page anatomy research. It avoids making up a sailor, a muster-roll image or a command's specific roster entries. Reader can use a 12-field form or printable fallback to document a supported claim and gaps; plain-text export happens only when requested. No third-party image/scan copied, no user data transmitted by the tool itself.

**Source trail — last opened 2026-11-17 (America/Los_Angeles):**
1. NARA, *U.S. Navy Muster Rolls, 1798–1939*, https://www.archives.gov/research/military/navy/muster-rolls . Quarterly enlisted lists; earlier Archives I holdings, later Archives II; selected 1938–1971 online material may require commercial provider. Source page last-reviewed 2020-06-25. The National Archives catalog and genealogy index should never be construed as access to every page.
2. NARA Textual Records Division / Onaona Guay, *Know Your Records: U.S. Navy Muster Rolls and Personnel Diaries* (2013, 2020 update), https://text-message.blogs.archives.gov/2013/12/02/know-your-records-u-s-navy-muster-rolls-and-personnel-diaries/ . Personnel diaries report status changes, muster rolls attachment by reporting period. 1939–1956 officer/enlisted distinction and officer + enlisted rosters from March 1957. Post-1970 privacy/FOIA restrictions. Historical staff commentary may contain superseded fulfillment methods; guide links directly to living NARA access pages for current requests.
3. NARA, *1941–1959 Deck Logs*, https://www.archives.gov/research/military/logbooks/navy-deck-logs-1941-1959 . Monthly title, remarks and columnar pages, often monthly officer lists through spring 1956. Qualification: format varies by vessel; not a perfect ship-wide standard.
4. NARA, *Information NOT Included in Deck Logs*, https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs . Day-to-day crew duties and off-ship activities are usually not recorded.
5. NARA, *Digitized Deck Log Index*, https://www.archives.gov/research/military/logbooks/navy-online . USS Abbot DD-629, February 1951 **catalog discovery only**, no crew name or underlying scanned page claim.
6. NARA, *Access to OMPFs for the General Public*, https://www.archives.gov/personnel-records-center/ompf-access-public and *Request Military Service Records*, https://www.archives.gov/veterans/military-service-records . Rolling 62-year separation rule and privacy of non-archival files; copying may cost money, no purchase initiated.

**Evidence constraints:** 'Assigned' is not 'present at a particular place/hour'; a name missing from a deck log is not negative roster evidence. The apparent overlap in source descriptions of 1956–March 1957 is reported as a transition qualification, not a universal ship-specific adoption day. No individual service or medical record inspected. Do not request, store in worksheet or display SSNs or current private addresses. No claims about a specific crew assignment or a particular person's actions.

**Artwork/media, rights and accessibility:** Newly authored explanatory SVG and HTML/CSS/JS, Final Vestige Studios, 2026-11-17, source: docs/editorial/library/the-log-was-not-the-voyage-sailor-not-in-log-2026-11-17.html. Its caption, SVG title and desc identify it as schematic (not an archival document), original FV creation. No NARA, Navy, Ancestry, commercial, or third-party image copied. External institutional pages linked only; item-level rights must be checked before future image reproductions. The form uses twelve explicit labels, a live status region and an accessible text receipt; diagram is keyboard-scrollable with readable min-width under 600px, table has its own keyboard-scroll region. Print CSS and no-JS fallback included. Not certified WCAG or screen-reader tested in browser.

**QA/readback results (static/API only):** 16/16 assertions passed: exact source parity; exactly one occurrence of final 22,751-character Gutenberg block inside 105,455-character WordPress raw edit-content; five top-level HTML blocks; original four SHA-1 block hashes unchanged; draft #2870 parent #77 and jetpack_seo_noindex=true; unique DOM IDs; 12 correctly associated labels; keyboard-scroll diagram/table; SVG title/desc; print/mobile rules; no-JS content; inline script JavaScript syntax compile; no remote JS; seven-plus institutional link occurrences; no third-party img tags. GitHub source blob SHA \`1d38a767a824383ffb8ceded02a236afc69d2bc1\`, reviewed commit \`452b5ed962d38330361147ca7ea62aad0b8beb65\`. WordPress modified \`2026-11-17T18:43:15\`. Source has ~1,700 HTML-stripped tokens/words (rough estimate; not final rendered word count). Existing public /free-resources/ and /free-resources/research-sources/ independently returned HTTP 200; no changes made.

**Release HOLD:** The WP production Assembler theme has not rendered this unpublished module in an authenticated browser at 320/390/768/1440; text input/save/clear/export interactions and screen reader have not been exercised there. Newsletter \`email_new_posts_by_default=false\` and earlier posts have \`never_sent_opted_out\`, but explicit per-first-publication email and Jetpack Social suppression remain unproven through this API. Do not publish, modify the Library navigation, merge this draft PR, email subscribers or operate social accounts. The public Research Sources page has an unrelated 60-card body / 90-card SEO-description discrepancy managed by its own issue; do not alter its content in this lane.

**Grok coordination concept only:** *The name isn't in the ship's log. That doesn't mean the sailor wasn't aboard.* Requires content-lane owner approval; no social publishing or edits.
