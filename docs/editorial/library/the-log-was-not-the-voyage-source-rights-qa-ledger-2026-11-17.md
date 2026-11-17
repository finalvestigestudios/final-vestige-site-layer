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