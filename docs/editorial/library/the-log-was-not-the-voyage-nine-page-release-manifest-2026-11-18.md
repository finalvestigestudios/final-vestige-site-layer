# The Log Was Not the Voyage — nine-page release manifest

Last checked: November 18, 2026, approximately 00:40 PST. Owner: Final Vestige Library. STATUS: **DRAFT / QA HOLD**. Do not publish, merge, announce or spend.

## Release architecture

The original WordPress Library draft [#2870](https://finalvestige.com/wp-admin/post.php?post=2870&action=edit) contains 206,173 serialized characters: one original route map and nine researched maritime record modules. Publishing one enormous page would be difficult to navigate on mobile. This deliberate split establishes nine independently reviewable, reader-sized, source-preserving child **drafts**. All inherited factual claims and primary source links are from the existing source-controlled research; no new historical findings are claimed.

| Part | WordPress draft | Slug | Research task | Source HTML in this GitHub directory | Saved characters |
|---|---|---|---|---|---:|
| 1 | [#2886](https://finalvestige.com/wp-admin/post.php?post=2886&action=edit) | ship-logbook-archive-route | Locate the ship's logbook | [source](the-log-was-not-the-voyage-2026-11-17.html) | 26,067 |
| 2 | [#2887](https://finalvestige.com/wp-admin/post.php?post=2887&action=edit) | ship-logbook-missing-record | The missing-log search | [source](the-log-was-not-the-voyage-missing-log-evidence-desk-2026-11-17.html) | 22,387 |
| 3 | [#2888](https://finalvestige.com/wp-admin/post.php?post=2888&action=edit) | ship-logbook-vessel-identity | Vessel identity and two Abbots | [source](the-log-was-not-the-voyage-abbot-case-study-2026-11-17.html) | 16,474 |
| 4 | [#2889](https://finalvestige.com/wp-admin/post.php?post=2889&action=edit) | ship-logbook-page-anatomy | Three-page deck-log anatomy | [source](the-log-was-not-the-voyage-three-pages-one-day-2026-11-17.html) | 19,129 |
| 5 | [#2890](https://finalvestige.com/wp-admin/post.php?post=2890&action=edit) | ship-logbook-crew-identity | A sailor absent from the log | [source](the-log-was-not-the-voyage-sailor-not-in-log-2026-11-17.html) | 23,088 |
| 6 | [#2891](https://finalvestige.com/wp-admin/post.php?post=2891&action=edit) | ship-logbook-position-track | Position is not a track | [source](the-log-was-not-the-voyage-position-not-track-2026-11-17.html) | 24,492 |
| 7 | [#2892](https://finalvestige.com/wp-admin/post.php?post=2892&action=edit) | ship-logbook-port-dates | Port date versus docking | [source](the-log-was-not-the-voyage-port-date-not-docking-2026-11-17.html) | 21,923 |
| 8 | [#2893](https://finalvestige.com/wp-admin/post.php?post=2893&action=edit) | ship-logbook-message-chain | Message acknowledged versus delivered | [source](the-log-was-not-the-voyage-message-not-delivery-2026-11-17.html) | 18,755 |
| 9 | [#2894](https://finalvestige.com/wp-admin/post.php?post=2894&action=edit) | ship-logbook-correction-chain | Corrections in rough and smooth logs | [source](the-log-was-not-the-voyage-line-was-not-erased-2026-11-17.html) | 21,810 |

Each new draft has parent Library #77, status draft, noindex true, comments closed, an accessible original FV SVG and primary-source notes. Only the first child has its inherited internal H1 demoted to H2 with the matching CSS selector because the WordPress theme supplies the page title as H1. Every page has one short numbered series introduction. The original #2870 has **not** been deleted, modified, redirected or published; its orientation route map remains there. No public Library card or navigation links have been changed.

## Independent QA evidence — November 18, 2026

All nine pages were read back from authenticated WordPress **after creation**. In 9/9 cases: status draft, parent 77, noindex, exactly one HTML source module matching the parent module **byte-for-byte**, except the documented first-page semantic H1-to-H2 adaptation, with no sanitizer warnings. Structural checks found no duplicate element IDs, no broken internal fragment links, no empty/javascript hrefs, one SVG with a title and description on each page, and zero missing img alt attributes. Three pages include browser-local JS worksheet controls inherited from the original; **these have not passed real browser interaction testing**.

Signed-out visitor server readbacks: published /free-resources/, /free-resources/research-sources/, and /editorial-standards/ returned HTTP 200, with their existing canonical metadata, no empty links and no missing alt attributes in the server-rendered check. The new draft /free-resources/ship-logbook-archive-route/ returned HTTP 404 to an anonymous visitor, as expected. The existing public Library has not changed.

## Primary-source, rights and access ledger (checked November 18)

- US NARA [digitized Navy log index](https://www.archives.gov/research/military/logbooks/navy-online): readable; identifies the February 1951 index entry for USS Abbot (DD-629). The index itself does not prove a folio's contents.
- US NARA [Navy deck log introduction](https://www.archives.gov/research/military/logbooks/naval-deck-logs): readable; documents commissioned-vessel and record-retention distinctions.
- US NARA [merchant-vessel logbooks](https://www.archives.gov/research/military/logbooks/merchant-vessels.html): readable; distinguishes official and operating records and relevant record groups.
- US NARA [information excluded from deck logs](https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs): readable; a logbook is not a complete crew diary.
- US NARA [classified, withdrawn, and missing deck logs](https://www.archives.gov/research/military/logbooks/navy-deck-log-exemptions): readable; separate discovery and access outcomes.
- [NARA Catalog ID 285104169](https://catalog.archives.gov/id/285104169): direct research fetch unavailable; locator retained, underlying pages unexamined.
- [UK National Archives merchant crew guide](https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/merchant-navy-ships-records-crew-lists-musters-and-log-books/): research client HTTP 403; reader access not established.
- [Cape Ann Museum A18 logbook finding aid](https://www.capeannmuseum.org/media/library_and_archives_finding_aids/a18_-_ships_log_book_collection_finding_aid.pdf): source linked, not copied; recheck PDF pages in ordinary browser for exact clock claims.
- [FV Editorial Standards](https://finalvestige.com/editorial-standards/): accessible, aligns with separating evidence from inference and disclosing rights.

Rights: No third-party archival images, maps, videos, photographs or scans were reproduced in these drafts. The nine diagrams are FV-original explanatory material, not documentary facsimiles, with labels and accessible descriptions. A government or museum listing does not automatically establish the reuse rights of an individual scan. Consult [the main source and rights ledger](the-log-was-not-the-voyage-source-rights-qa-ledger-2026-11-17.md).

## Outstanding hard gates before any public release

1. Real authenticated WordPress production-theme screenshots and browser layout/overflow at **320, 390, 768, 1440 pixels** for the child pages, including header/signup overlays and printable worksheets.
2. Real keyboard, focus, screen-reader and JS form interactions; inspect mobile and print output. Static checks alone are **not acceptance**.
3. Original documentary source access check for the 1912 inquiry material, ordinary-browser resolution of blocked UK/NARA Catalog links, all outbound links, and item-level reuse qualifications.
4. Enforceable first-publish email/publicize suppression: prove **_jetpack_dont_email_post_to_subs=true** and **jetpack_publicize_feature_enabled=false** in a safe write/read mechanism. The present page connector does not expose those guaranteed fields. Do not trust newsletter-off defaults alone.
5. Final editorial navigation linking the nine pages in order, responsive design, source/rights dates, SEO title descriptions and corrections link. Update the published Library card/index **only after** the gates pass, without disrupting existing content.
6. Check current WordPress modified timestamps and coordination issues again before making any final changes. Related blockers: [shared QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589), [Research Sources data integrity #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788). This release did **not** take over either.

Potential Grok short-form concept after safe publication: "Missing log, missing crew name, and missing page: three different research questions." No Grok account edits, emails, subscriber blasts, social posts, purchases, or changes to Preparedness, Investigations, or homepage engineering were made.
