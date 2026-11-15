# The City Seen From Nowhere — Library companion and release HOLD

**Last checked:** November 15, 2026 (Pacific). **Owner:** Final Vestige Studios Library Resource Studio. **Proposed home:** companion to [The Lost Landscape](https://finalvestige.com/free-resources/the-lost-landscape/), not a replacement. **Publication status:** offline release candidate / HOLD. Existing WordPress content unchanged.

## Reader problem
Late-nineteenth-century bird's-eye city views are *drawn perspectives*, not necessarily surveyed maps or aerial photographs. An apparent street or named building can provide a historical lead, but image prominence is not physical scale, a published date is not necessarily an observation date, and invisible features are not proved absent.

## Original deliverables produced
- Self-contained original 19 KB accessible HTML field guide **The City Seen From Nowhere**, with original fictional perspective-vs-plan SVG (clearly labeled schematic, not documentary).
- Six-pass method: locate exact copy; read margins/artist/viewpoint; classify image claims; independently corroborate; separate document dates; state narrow finding.
- Browser-local **Perspective Witness Desk**: nine fields, private text preview, JSON and TXT downloads, reset; no network/storage/subscription calls.
- Three-page printable PDF: method, usable lined worksheet and clickable institutional source shelf.
- Nine-entry dated source-access and rights ledger; release-hold report and 8 responsive QA screenshots.

## Primary evidence, checked Nov 15
- [LOC California local history guide: maps](https://guides.loc.gov/california-local-history-genealogy/digital-collections) — fully readable institution-authored source; defines panoramic maps as nonphotographic oblique city depictions, generally not drawn to scale.
- [LOC San José 1875 panorama / LCCN 75693108](https://www.loc.gov/item/75693108/) — first-party indexed catalog fields state the work shows a view from an elevation of 500 ft looking north, **not drawn to scale**. Direct page open returned HTTP **403** in this research environment: **scan not inspected**.
- [LOC Santa Rosa 1876 panorama / LCCN 76693083](https://www.loc.gov/item/76693083/) — first-party indexed catalog fields: looking NW from SE, indexed points of interest, **not drawn to scale**. Direct page open returned **403**: **scan not inspected**.
- [LOC cartographic search guidance](https://guides.loc.gov/cataloging-cartographic-materials/using-the-map-collections) and [LOC copyright guidance](https://www.loc.gov/legal/security-copyright-and-privacy/understanding-copyright/) — institution source guidance; no historic map copied.
- Companion cross-link: [The Lost Landscape](https://finalvestige.com/free-resources/the-lost-landscape/).

## Rights
All text, CSS, JS, SVG concept drawings and worksheet are new original FV material; **no archival map scans, photos or government seals copied**. LOC holds originals but generally does not grant third-party copyright rights. Confirm each archival map's item-specific rights advisory before any scan reproduction. The displayed graphic is an explicitly invented conceptual town, not a reconstruction of San José/Santa Rosa.

## QA
Chromium local **page.set_content**: 320 / 390 / 768 / 1440 px, JS enabled and disabled: **8/8 PASS**; one H1, accessible SVG name+description, source links visible with JS off, no page-wide horizontal overflow or JS errors. Four JS-enabled runs passed preview, JSON/TXT download, reset and malicious-input plain-text handling. Three PDF pages rendered and visually inspected; source-page links embedded on PDF page three. **This does not constitute production WordPress-theme QA or PDF/UA tagging.**

## Release hold / exact outstanding evidence
1. Ordinary-browser open and inspect each LOC catalog record, *actual* historical map and item-level reuse statement (two item pages returned 403 automatically).
2. Production WordPress-theme 320/390/768/1440 visual, keyboard, source and no-JS QA. No theme-level proof yet; share cross-cutting issue #1589.
3. For first-publication WordPress work, prove `_jetpack_dont_email_post_to_subs=true` on publish. Current connector does not expose this key; keep as offline/draft. No media or email/sending controls changed.
4. Anonymous public HTTP byte readback for hosted HTML/PDF if ever attached, plus preserved parent/paths and minimal single Library card/cross-link edit.

Avoid conflict with existing The Map That Slipped (#2511), The Scale in the Copy draft (#2300), The North in the Margin draft (#2298), and existing Lost Landscape. No new WordPress draft created. No public edits, Grok activity or spending.
