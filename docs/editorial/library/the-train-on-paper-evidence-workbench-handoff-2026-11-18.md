# The Train on Paper — Evidence Workbench / Release Handoff

**Date:** 2026-11-18. **Status: HOLD (not published).** Library owner only. Companion to existing WordPress **draft #2924**, parent #77, noindex, and [PR #3071](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3071).

## New working reader asset

A standalone offline HTML evidence instrument was built and exercised in local Chromium. It is **not another field guide**: it gives researchers a precise way to record a published railway timetable and a second putative operating witness without turning scheduled service into an observed journey.

- Three claim scopes: *scheduled*, *specific train operated*, *named passenger traveled*. The final is never considered established by timetable/operating log alone.
- 21 form inputs/selects/text areas; original descriptive SVG; clear fictional worked example; user-affirmed exact date, service identity, independent source and image inspection; second-witness URLs must also be complete HTTPS URLs.
- Conservative classifications distinguish missing document identity, timetable-only claims, retrospective recollection, duplicated schedule, catalog description and independently reviewed second records.
- Qualified text receipt, locally downloaded UTF-8 CSV (formula-injection guard), copy and print. No cookies, accounts, analytics, CDN, tracking, external assets, API requests, form submission or automatic date/time conversion.
- **Current checked-in instrument:** [`the-train-on-paper-evidence-workbench-2026-11-18.html`](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/review/library-train-on-paper-20261118/docs/editorial/library/the-train-on-paper-evidence-workbench-2026-11-18.html). **SHA-256 (local hardened copy):** `8d80a52767b6d62607d232af300b6332ac825fe15cc00dc0cc11c3f27357269f`; **23,379 UTF-8 bytes**, 23,359 code points. Source file was committed in `2ceb36a` and safety changes in `b122597`; GitHub readback exactly matched the submitted Unicode source. No hosted version or live WordPress embed exists.

## Research register: inspected on November 18, 2026

| Record | Link | Evidence / rights | Limitation |
|---|---|---|---|
| Baltimore & Ohio Railroad Company, *Book of the Royal Blue*, 1897–1911, Library of Congress | https://www.loc.gov/item/05032208/ | LOC states books in collection public domain/free to reuse. Primary printed schedules require precise volume, issue, page. | Direct source open denied (403) in one retrieval client; no individual operating event proven. |
| B&O *Book of the Royal Blue*, Volume 14 (1910–1911), Library of Congress scan | https://www.loc.gov/resource/gdcmassbookdig.bookofroyalblue27balt/ | Official digital discovery record; no scans copied. | Individual schedule page pixels not verified; direct 403 in web tool. |
| LOC *Railroads: Sources for Historical Research — Maps, Time Tables & Images* | https://guides.loc.gov/railroads/maps-timetables | Authenticated institution guide describes timetable discovery and incomplete holdings. Link only. | Not a primary operating log. |
| Smithsonian NMAH, Amtrak Northeast Corridor Employee Timetable No.1 (1989) NMAH.AC.1327_ref101, Box 10, Folder 9 | https://americanhistory.si.edu/collections/archival-item/sova-nmah-ac-1327-ref101 | Catalog proves holding, appointment access; reproduction requires item-level rights review. No copy. | Original contents not inspected. |
| Smithsonian *On Time: Mechanizing Time* | https://americanhistory.si.edu/ontime/mechanizing/reliable.html | Institutional historic-clock context. Link only. | Does not prove clock standard for a specific issue. |
| FV *The Lost Itinerary*, *The Archive Trail* and Editorial Standards | https://finalvestige.com/the-lost-itinerary/ ; https://finalvestige.com/the-archive-trail/ ; https://finalvestige.com/editorial-standards/ | Public pages independently retrieved; clear related scopes, no content copied. | The website's production theme still needs exact instrument browser validation. |

**New source-level nuance from this run:** Text extraction from the LOC B&O 1910 volume exposes both an **eastward Royal Blue schedule effective May 29, 1910**, and a **different westward “to all points west and southwest” schedule effective September 4, 1910**. These govern distinct headings/services within the same bound volume, not necessarily an editorial contradiction. The page-image screenshot service refused the 56.7 MB PDF, so do not assert visually confirmed numbers. The guide/tool must never promote one heading’s effective date to the entire bound volume.\n\nThe workbench uses only an **original FV 2026 explanatory SVG**, described in text; no external historic images, publisher logos or facsimiles. Every sample train, station, schedule, number and claim is explicitly fictional. The LOC source link in the sample is a genuine **repository example, not support for the fictional train**.

## QA completed locally

Local Playwright/Chromium **rendered and executed the actual HTML with `page.set_content`** at 320, 390, 768, 1440px. Four viewport passes, page-wide horizontal overflow zero at all widths, JS exception count zero, sample/receipt/CSV/reset/passenger tests passed. Additional tests passed for incomplete IDs, a duplicated source, conditional second-witness classification, HTML input as inert text, spreadsheet formula prefix defense, keyboard Tab sequence, and print-only receipt visibility. Screenshots inspected at 390px.

**Not passed**: the browser is blocked by environment policy from navigation to `file://`, `127.0.0.1` or the live site. Thus `set_content` verifies locally authored layout and behavior, **not production-theme/browser/navigation acceptance**. Formal screen-reader testing also outstanding.

## Fail-closed publishing sequence

1. **GitHub source transfer complete.** Select approved static delivery on Final Vestige and test byte-parity, Content Security Policy and actual JavaScript execution. Do not paste scripts into public Gutenberg without confirming HTML sanitization and CSP.
2. Use signed-out production-theme browser to check mobile widths 320/390/768/1440, screenshot pixels, keyboard and assistive technologies, CSV download, print output, no console errors or unexpected network calls.
3. Inspect primary scan pixels before reporting exact B&O schedule transcriptions, and verify outbound links from a real visitor browser.
4. Confirm **effective** first-publication email and social suppression including `_jetpack_dont_email_post_to_subs=true`. Do not assume that a site setting alone guarantees it.
5. On verified acceptance, link from *Train on Paper* and add a single scoped Library card with accurate description, then independently verify WordPress readback, public URL, canonical/robots, links and media.

No live WordPress content, navigation, newsletter/social settings, Preparedness, Investigations, homepage engineering or Grok accounts were modified. No spending or subscriber blast.

**Potential Grok lane after release:** “The train was printed in the schedule. Did it run? The paper knows less than you think.” Demonstrate fictional data only; keep account handling with Grok's owner.


## November 18, 2026 — checked-in release-candidate hardening

- **New guard:** if the timetable and purported operating record have the identical source URL, the tool rejects the idea of two independent witnesses, even when the user checks the independence box. It asks for a distinct source record and identity.
- **New guard:** editing any of 21 fields after generating a receipt invalidates the stale classification and hides export/copy/print until the reader rebuilds the receipt. This prevents downloading notes that silently disagree with changed source details.
- **Local Chromium v2 QA:** all four widths (320/390/768/1440) passed again with no overflow or browser JS exceptions, sample CSV download, reset, person-claim rejection, print CSS, inert HTML input and CSV-formula guard; added explicit same-URL and input/select/checkbox stale-receipt regression cases. This remains **local HTML `set_content`**, not hosted production QA.
- **Independent WordPress checks:** public Library, Research Sources and Editorial Standards canonical pages returned status 200; visitor read of page #2924 returned 404; authenticated WP confirmed `draft`, parent 77, `jetpack_seo_noindex=true`. The still-live 60/90 static text discrepancy is already assigned to separate Library issue #1788; no out-of-scope edits.
- **Archival corroboration caution:** the B&O Railroad Museum's John Geist 2007 index describes the periodical publication history and links back to LOC, but is a *finding aid*, not a new independent operating witness. https://www.borail.org/wp-content/uploads/2025/01/Index_TheBookoftheRoyalBlue.pdf . Museum PDF first page visually inspected. The LOC's 56,676,169-byte 1910–11 source PDF was too large for direct page screenshot; exact schedule headings remain unverified at scan-pixel level.
- **No new external images:** the included SVG is original FV explanatory artwork; linked historic source pages are not embedded/copied. Rights of the original LOC book collection were identified as public domain in the institution record; rights of unrelated images at other institutions are not assumed.
- **Release still HOLD:** missing production signed-out screenshots at four widths, screen-reader/print/browser acceptance, scan-pixel verification for any exact historical timetable transcription and enforceable Jetpack first-publish email/social suppression. No live WordPress publication, email, Grok/social activity or spending.
