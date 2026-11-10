# Research Sources — static-first release evidence and rights register
**Final Vestige Studios · Library editorial · November 10, 2026 (Pacific)**

> **HOLD: staging is not public.** This is an editorial-release record, not authorization to publish. The final 90-card HTML must be applied **in place** to published WordPress page **#1338**, **never** by publishing draft #2354 as a second directory. No plugin/theme/homepage/Preparedness/Investigations changes.

## What readers will gain
The current public directory's copy promises 60 sources, although 90 cards exist in its saved markup; 30 depend on client-side placement code. The replacement keeps **90 source cards directly in HTML**, so a browser without JavaScript still exposes every link. Site search and filters remain optional enhancements. A no-script notice is now included.

## Version-pinned WordPress evidence
- **Public** #1338, `publish`, modified `2026-11-03T22:12:43` Pacific; saved content contains 90 card articles but displays 60-source copy and runs 2 scripts. **No public edits made.**
- **Staging** #2354, `draft`, `jetpack_seo_noindex=true`, modified `2026-11-10T09:36:11` Pacific; one main source HTML block, one filter script, 90 statically embedded cards, no-JS explanation, reader safety note about NARA's JFK records. Authenticated readback matched saved content exactly; no content warnings.
- Same 90 titles retained; 90 distinct CTA destinations in staging; categories **12 / 24 / 21 / 25 / 8** (declassified/accountability/engineering/archives/navigation); no source deleted or added.
- **42 source-card contents differ** from public (one includes a new November 10 JFK privacy qualification); additional structural labels/counts and client-side logic repaired. Older reports of "42 corrections" are sequential editorial-work counters, not proof that 42 unique independent institutional corrections were checked again today.
- Three primary CTA destinations differ from public:
  - **Congressional Hearings Collection:** old `https://www.govinfo.gov/help/chrg` → staged `https://www.govinfo.gov/app/collection/chrg`
  - **NTSB CAROL — Case Analysis and Reporting Online:** old `https://www.ntsb.gov/Pages/carol.aspx` → staged `https://carol.ntsb.gov/`
  - **National Archives Donated Collection Explorer:** old `https://www.archives.gov/findingaid/donated-collection-explorer/1000` → staged `https://www.archives.gov/findingaid/donated-collection-explorer`

## Source verification sample (2026-11-10 UTC)
Of 90 primary destinations, **10** were observed through institutional search/readback in this session; this is a **sample, not 90 independently checked live links**. The remaining 80 must receive ordinary visitor sampling at release. `403` below means automated access blocked; **do not** label as broken without manual review.

| Institution / resource | Automated result | Note |
|---|---|---|
| National Archives · 2025 JFK files | Institution page retrieved | NARA explicitly warns of living-person personal information in released files. Avoid replicating PII. |
| State Department · FRUS Iran second edition | Institution page retrieved | 375 documents; original source volume is 2018 second edition. |
| GAO · High-Risk 2025 | Institution page retrieved | Report is **dated February 25, 2025**, not an automatically updated score. |
| NASA · Columbia Board | Institution page retrieved | NTRS volume-one citation/record available. |
| NOAA/NHC · Data archive | Automated **403** | Restriction to automated client, ordinary-browser accessibility not proven. |
| CDC Stacks | Institution page retrieved | Repository page and rights-help link available. |
| Library of Congress · Sanborn overview | Automated **403** | Item-level rights and correction dates must be checked manually. |
| National Park Service · Preservation Briefs | Institution page retrieved | Page has online materials; certain printed copies are sold (not all formats universally free). |
| FAA · AIM | Institution page retrieved | Change 3 effective July 9, 2026. |
| CIA · Kennedy–Johnson PDB booklet | Institution page retrieved | A **40-page explanatory booklet**, *not* a direct listing of 2,500 briefing files; the card identifies that boundary. |

**Institutional sources:** National Archives https://www.archives.gov/research/jfk/release-2025 ; State https://history.state.gov/historicaldocuments/frus1951-54IranEd2 ; GAO https://www.gao.gov/products/gao-25-107743 ; NASA https://ntrs.nasa.gov/citations/20030093634 ; NOAA https://www.nhc.noaa.gov/data/ ; CDC https://stacks.cdc.gov/ ; LOC https://www.loc.gov/collections/sanborn-maps/about-this-collection/ ; NPS https://www.nps.gov/orgs/1739/preservation-briefs.htm ; FAA https://www.faa.gov/air_traffic/publications/atpubs/aim_html/ ; CIA https://www.cia.gov/resources/publications/presidents-daily-brief-delivering-intelligence-to-kennedy-and-johnson/ .

## Rights and media provenance
The card’s access designation is a navigation aid, not a legal rights determination. Nothing in the ledger grants reproduction permission. Source images/scans were not downloaded or copied into this release. No third-party media included in this record. The companion CSV has all 90 titles, destinations, accompanying source qualifications, current card labels, and supporting links (distinct from each card's final primary **CTA**). Do not count the first in-card link as the primary source destination: some cards contain a qualifying citation before their actual CTA.

## Actual release gates — still red
1. Independent *actual front-end* screenshots/DOM evidence for WordPress staging at **320, 390, 768, 1440px**, JavaScript **on and off**. Verify 90 static links without JS, five filter counts, searching a formerly supplemental item, keyboard focus, no overflow, overlay/nav/footer and console.
2. Ordinary anonymous user tests of the three changed CTAs, 10 sampled sources above (particularly NHC/LOC anti-bot), local related-reading links and content metadata. Test media health; directory itself embeds no third-party archival media.
3. Verify publication will **not** send email to existing subscribers or trigger automatic social/Jetpack Publicize. The WordPress update schema does *not* expose the requested `_jetpack_dont_email_post_to_subs=true` key; do not assume it is set. Existing public page is being **edited**, not first-published, but still verify.
4. Re-fetch public #1338 and draft #2354 immediately before editing. Abort if changed; take a source backup/rollback snapshot. Apply only the vetted draft to #1338; preserve URL, parent, IDs and other blocks. **Do not** publish staging #2354.
5. After save: independent authenticated WP readback and anonymous public URL DOM + actual screenshot at all four widths; title, description, noindex **false** on #1338; 90 distinct card CTAs and five category counts; document source links and rights. Then correct the Library landing page #77's static “Sixty” / “60 curated” copy as a separate exact scoped edit.
6. Grok may later produce a public-facing research clip; do not post before publication, or alter its accounts.

## Coordination
Release owner: [Library #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788). QA browser blocker: [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). Never infer a production visual pass from WordPress's mshots `status=ready`: the screenshot pixels could not be fetched in this environment.

**Editorial standard:** https://finalvestige.com/editorial-standards/ (authenticated WordPress content inspected on November 10, 2026).

**No subscriber email, publication, social activity, paid calls, or visitor-data collection.**
