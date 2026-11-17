# Final Vestige Library · The Two Timelines · Accessible HTML companion

**Revision:** 2026-11-17 · **Disposition:** RELEASE HOLD; offline review asset, not publicly published · **Owner:** Library Resource Studio · **Source artifact:** `FV_The_Two_Timelines_Accessible_Casebook.html`.

## Why this exists

The existing six-page fillable PDF casebook is useful for print/form completion but is **not** certified as a tagged accessible PDF. This new original, portable HTML casebook provides semantically labeled fields, figure text description, navigational links, an independently usable scriptless worksheet and optional local Markdown receipt export. It extends rather than duplicates WordPress draft #2860 (*The Two Timelines*) and the earlier PDF. It makes **no** claims of automated historical-clock conversion, record authentication, or source independence.

## Sources and provenance: last opened 2026-11-17

| Source | Institution / creator / record | Publisher date or note | Original URL | Access / rights / qualification |
|---|---|---|---|---|
| Apollo 204 preliminary memorandum | NASA History Office; Robert C. Seamans, Jr., memorandum to James E. Webb | 1967-02-03; transcribed from Review Board source | https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/seamans.html | Public NASA-hosted transcription, link-only; preliminary account. The source warns recording stations might not be synchronized within 1–2 seconds. Presence on NASA site does **not** clear every embedded element for republication. |
| Apollo 204 Review Board chronology | NASA History Office; Apollo 204 Review Board | 1967; NASA Historical Reference Collection | https://www.nasa.gov/history/Apollo204/tragedy.html | Public institutional transcript, link-only; later account. Do not infer timestamp differences diagnose the cause of the fire. |
| Production Date | US National Archives, Lifecycle Data Requirements Guide | Page reviewed 2024-09-26 | https://www.archives.gov/research/catalog/lcdrg/elements/production-date | Public institutional reference, link-only. Defines **creation/production date**, not event timestamp. |
| Universal Time | US Naval Observatory, Astronomical Applications Department | Undated institutional reference, accessed 2026-11-17 | https://aa.usno.navy.mil/faq/UT | Public reference, link-only. Different Universal Time designations matter at finer precision; certain almanac practices cannot be generalized to unrelated records. |
| Daylight Saving Time Rules | US National Institute of Standards and Technology | Institutional reference, accessed 2026-11-17 | https://www.nist.gov/pml/time-and-frequency-division/popular-links/daylight-saving-time-dst | Public reference, link-only. Modern time transitions do not prove historical clock practice. |
| Editorial Standards | Final Vestige Studios | Site says last reviewed 2026-08-23 | https://finalvestige.com/editorial-standards/ | FV editorial policy for disagreement, sources, AI, images and corrections. |

Original NASA times retained as *reported* times: preliminary rupture **about 6:31:17 p.m. EST**; later chronology rupture **23:31:19.4 GMT** (6:31:19.4 p.m. EST); difference approximately **2.4 seconds**. The preliminary detection event and later spoken-report event are not necessarily the same occurrence. Neither establishes exact ignition. Shared institutional publication does not establish independent station evidence.

## Media / rights ledger

- **Original explanatory SVG:** *Two records, four separate acts*, drawn expressly for Final Vestige Studios on 2026-11-17 within the HTML document. Author/owner: Final Vestige Studios. Source: this original HTML. Rights: original FV work; available as part of this free publication subject to FV's rights. Caption and `<title>`/`<desc>` included. Not historical imagery, NASA data or AI reconstruction.
- **Original editorial prose, layout, form fields and JavaScript:** Final Vestige Studios, 2026-11-17. Original FV work. No external photographs, archival scans, videos, documents, logos or third-party images embedded or redistributed. Linked sources remain subject to item-level conditions; free access is not a reuse grant.
- **No external runtime dependencies:** no CDNs, webfonts, analytics, forms submission, storage, cookies, ads or network requests from the standalone HTML.

## QA (offline, actual Chromium engine via `page.set_content`, not WordPress theme)

- 8/8 responsive configurations passed: 320, 390, 768 and 1440 pixel widths with JavaScript **on and off**. Chromium at `/usr/bin/chromium` used; local `file://` direct navigation was blocked by the environment, so the HTML was loaded as source via `page.set_content` into a browser document. Eight inspectable screenshots accompany this package.
- No horizontal overflow at tested widths, no JavaScript runtime errors, and no outgoing network requests on this offline resource in those runs.
- Both witness fieldsets (16 explicitly labeled evidence fields), four mutually exclusive verdict choices and five institutional source links retained.
- Markdown export tested under Chromium with sample inputs (including `<test>` and `&`), verified saved output and HTML entity neutralization. **The exported transcript summarizes user entries; it does not verify them.**
- Core form and sources remain readable at all widths with JS disabled. No keyboard-only screen-reader manual assessment or actual hardware assistive technology acceptance completed; HTML labels, headings and figure description are structural checks only.
- Pages tested offline, not rendered through the real WordPress theme. Live production-theme QA at 320/390/768/1440 remains outstanding.

## Live site / coordination

- Live Library page: https://finalvestige.com/free-resources/ · WordPress #77. Verified 2026-11-17 signed-out HTTP 200, canonical matches, 0 missing image-alt entries or blank links in WordPress server-rendered checker.
- Live Research Sources: https://finalvestige.com/free-resources/research-sources/ · WordPress #1338. Signed-out HTTP 200, canonical matches; published text continues to label the directory as *60* even though separately audited markup has *90* source cards. Correction tracked in GitHub #1788 and staging #2354.
- Two Timelines WordPress draft #2860: remains draft/noindex under Library #77, anonymously HTTP 404; existing PR #2878 and coordination issue #2879. This asset did not write to WordPress.
- Newsletter setting `email_new_posts_by_default=false` verified 2026-11-17, but this **does not prove** enforceable email/social suppression for a first public release. Do not publish until stronger controls are verified.
- A potential short educational video could illustrate detection → report → log → publication using the original schematic. **Coordinate with Grok only; do not modify its social accounts.**

## Open release gates

1. Inspect actual **WordPress-theme** rendering, keyboard operation, screen-reader semantics, Markdown export and print at 320/390/768/1440. A local fixture alone does not meet production approval.
2. Establish and test reliable no-email, no-social first-publish suppression (including explicit `_jetpack_dont_email_post_to_subs=true` wherever supported). Current supported WordPress pages meta does not expose that flag.
3. Obtain full live URL review, item-level rights signoff for any *future* archival media additions, and editor approval of final page card/link placement.
4. Only then promote this companion and/or draft #2860, preserving old pages, and independently read back rendered content, canonicals, media/links and notification outcomes.

**Publication result this run:** HOLD. No paid calls, public edits, subscriber emails, notifications, social changes, or changes to Preparedness, Investigations, homepage engineering or Grok accounts.