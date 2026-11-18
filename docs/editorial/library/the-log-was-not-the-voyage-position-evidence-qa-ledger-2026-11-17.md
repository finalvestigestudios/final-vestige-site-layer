# FV Library | Position Evidence Desk — Source, Rights, QA and Release Record

**As-of:** November 17, 2026, 19:38 Pacific  
**Owner/scope:** FV Library Resource Studio. Existing WordPress Library draft #2870 (*The Log Was Not the Voyage*), parent #77. Existing GitHub draft PR #2922.  
**Resource:** [The position was not the track](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/review/library-log-was-not-voyage-20261117/docs/editorial/library/the-log-was-not-the-voyage-position-not-track-2026-11-17.html).  
**Decision:** **HOLD public release**. This is source-controlled draft work, not a published page or an authorized navigation product.

## This session's work

- Added a distinct, about 1,990-word position-evidence instrument to an already-running maritime archival guide instead of creating another overlapping Library page.
- One new top-level `core/html` Gutenberg block appended at position 5, taking the existing page from 5 to 6 blocks. The previous five block hashes were retained unchanged.
- New block: **24,155 characters** of serialized Gutenberg HTML, including responsive and print styles, an original inline explanatory SVG, one four-row evidence matrix, eight-step research method, an explicit fictional example, and a ten-field local-only Position Evidence Receipt (build/copy/print plus print/no-JS alternative).
- WordPress authenticated readback after final fixes: page **draft**, **noindex=true**, **parent=77**; site-local modified `2026-11-17T19:38:58`; total raw content **129,610 characters**. **Exactly one occurrence** of new annex; entire final 24,155-character source-controlled block occurs verbatim in WordPress raw content.
- GitHub latest change to annex: `7e62f37fd6f689e686e578667c2050d113ff3f86`; fixed editorial contact destination and removed unverified blanket third-party reuse grant. All WordPress block edits were optimistic-locked and returned zero content warnings.

## Evidence trail and critical qualifications

Official/institutional reference URLs directly examined or linked during the November 17 research cycle. These support general method and record characteristics, **not** any particular historical voyage inferred from the fictional diagram.

| Source | Supports / limits | Checked |
| --- | --- | --- |
| [NARA, NOAA and Coast & Geodetic Survey vessel logbooks](https://www.archives.gov/research/military/logbooks/noaa-vessels.html) | Positions, weather and operations may appear in some archival series; formats vary, so each original log/page must be inspected. | Nov 17, 2026 |
| [NARA, Navy deck logs available online](https://www.archives.gov/research/military/logbooks/navy-online) | Discovery and selected day-by-day ship events. A directory entry is not a surveyed track. | Nov 17, 2026 |
| [NARA, Digitized Deck Logs](https://www.archives.gov/research/military/logbooks/digitized-logs) | Incomplete digitization / limits on access; a failed search is not proof of a missing or empty log. | Nov 17, 2026 |
| [NARA, Information Not Included in Deck Logs](https://www.archives.gov/research/military/logbooks/navy-info-not-in-deck-logs) | Many details are outside deck-log purpose. A silent page is not proof an event did not happen. | Nov 17, 2026 |
| [NOAA Office of Coast Survey, How Accurate Are Nautical Charts?](https://nauticalcharts.noaa.gov/updates/how-accurate-are-nautical-charts/) | Survey ages and compilation methods vary; a modern overlay is not an automatic validation of older coordinates. | Nov 17, 2026 |
| [NOAA NGS, Datums FAQ](https://www.ngs.noaa.gov/datums/faq.shtml) | Horizontal datum meanings/relationships; do not assume a historical reference frame from a modern coordinate display. | Nov 17, 2026 |
| [NOAA NGS, NCAT](https://www.ngs.noaa.gov/NCAT/) | Transformation/conversion service when the actual input frame is established; does not infer missing historical metadata. | Nov 17, 2026 |
| [NOAA Historical Map & Chart Collection](https://historicalcharts.noaa.gov/) | Discovery of historical editions; chart edition, original survey dates and reproduction terms require object-level review. Portal/interactive route requires ordinary-browser confirmation. | Nov 17, 2026 |

**Interpretation rule:** A literal position is not independently proof of its accuracy, method, modern reference frame or the vessel's intermediate path. Do not silently infer a line, a datum, an hour-zone or a ship movement from a pair of numbers.

**Cross-links:** Existing FV archive-method and historical-clock resources, plus source-specific NARA/NOAA links; the /the-last-fix/ cross-link received a transient automated 429 and remains an external-access acceptance item rather than a confirmed working page. **No unrelated editor sections modified.**

## Visuals, authorship and rights

- One original SVG vector: *Two documented positions do not establish an intervening ship track*. Authored for Final Vestige Studios, Nov 17, 2026; rights holder FV. Original, fictional explanatory graphic, neither a voyage reconstruction nor historic documentary image. Inline accessible `title`, `desc`, `aria-labelledby`, descriptive caption and provenance.
- **No third-party photo, chart tile, archive scan, logbook facsimile, video, institution mark or map dataset was copied.** Links to institutional source pages are citations, not automatic permission to republish those institutions' assets.
- Do **not** infer an open reuse license for the FV original art. The block states to follow studio permissions for external reuse.
- A future documentary-media enhancement requires object-level creator/institution/date/original URL/rights statement, accurate caption and alt text before inclusion.

## QA performed and remaining

| Test | Result |
| --- | --- |
| GitHub fetch after final commit | PASS — content returned and compared |
| Authenticated WordPress raw readback / block parity | PASS — exact 24,155-character substring, exactly one annex |
| Prior five Gutenberg block hashes unchanged | PASS |
| WordPress draft, parent #77, noindex | PASS |
| New source block has unique IDs / semantic form labels / inline SVG title and description | PASS structural |
| Responsive rules, 320/390 mobile CSS, tablet/desktop, print and no-JS fallback present | PASS structural only; **NOT** actual browser acceptance |
| No external JS libraries, fetch/XHR, client storage or send endpoint in new block | PASS static |
| Public Library and Research Sources | 200 and canonical URL confirmed on independent signed-out WordPress render readback |
| Draft anonymous URL | 404 (unpublished, expected) |
| Real production-theme 320/390/768/1440 visual and overflow checks | **NOT TESTED — HOLD** |
| Real tab/keyboard/copy/print interaction and screen-reader acceptance in the WP theme | **NOT TESTED — HOLD** |
| All outbound links and external portal destinations in an ordinary browser | **PARTIAL — HOLD** |
| Enforceable first-publish subscriber email/social suppression | **NOT VERIFIED — HOLD**. Do not publish until per-operation `_jetpack_dont_email_post_to_subs=true` and automatic publicize suppression can be guaranteed and read back. |

No public Library card/nav or existing public content changed. No notifications to subscribers, no social posting, no paid calls or spending. Preparedness, Investigations, homepage engineering and Grok accounts not touched.

**Next release step:** Obtain actual themed and assistive-technology acceptance for current revision, fix any issues in this annex only, verify the final link and rights inventory, demonstrate no first-publication subscriber/social distribution, then publish with a carefully scoped WordPress write and independently check public URL/SEO/media/link integrity. Coordinate the potential Grok educational-video angle only in an editorial comment, without accessing distribution accounts.
