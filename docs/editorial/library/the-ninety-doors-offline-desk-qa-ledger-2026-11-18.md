# The Ninety Doors — Offline Research Desk · Source, Rights & QA Ledger

**Editor:** Final Vestige Studios Library · **Checked:** November 18, 2026 (America/Los_Angeles)  
**State:** Draft PR / release HOLD. No WordPress publication, navigation, email, social or spending.  
**Artifact:** [Standalone offline research desk](./the-ninety-doors-offline-research-desk-2026-11-18.html) · [90-source CSV](./research-sources-90-portable-index-2026-11-18.csv)

## Reader problem

Find and compare existing institutional gateways, build a research shortlist, and preserve the identity of what was actually inspected. A gateway is not the original document, two links are not necessarily two witnesses, and an institutional download is not a universal reproduction license. The HTML works as a fully readable list without JavaScript; with JavaScript it adds local search, category filters, shortlist-to-CSV export and a printable eight-field source receipt. No accounts, tracking or externally hosted assets.

## Provenance & source checks

| Source | Record type / what it supports | Checked | Rights/access condition |
| --- | --- | --- | --- |
| [FV Research Sources](https://finalvestige.com/free-resources/research-sources/) | Live WordPress #1338; last edit 2026-11-03 22:12:43 site-local; 90 source cards | 2026-11-18 authenticated raw and signed-out readback | Original FV editorial descriptions; linked third-party collections are not reproduced |
| [FV Editorial Standards](https://finalvestige.com/editorial-standards/) | Primary-source and image-reconstruction policy | 2026-11-18 readable | Cross-link only |
| [The Archive Trail](https://finalvestige.com/the-archive-trail/) | Related FV source-tracing method | 2026-11-18 readable | Cross-link only |
| [NARA Copyright and Permissions](https://www.archives.gov/research/still-pictures/permissions) | Not all NARA holdings are public domain; item rights differ | 2026-11-18 readable | Reference link only |
| [LOC Rights and Access](https://www.loc.gov/collections/meeting-of-frontiers/about-this-collection/rights-and-access/) | Access does not waive third-party copyright or privacy rights | 2026-11-18 readable | Reference link only |
| [NARA JFK 2025 release](https://www.archives.gov/research/jfk/release-2025) | Sample directory destination; NARA warns of living-person PII | 2026-11-18 readable | No files/PII copied |
| [FRUS Iran volume](https://history.state.gov/historicaldocuments/frus1951-54IranEd2) | Sample official documentary index and edition | 2026-11-18 readable | No scans or text republished |
| [GAO High-Risk Series 2025](https://www.gao.gov/products/gao-25-107743) | Sample oversight report destination | 2026-11-18 readable | Link-only |

**Important limitation:** These sample checks do not establish health or reuse rights for all 90 institutional destinations. CSV and viewer rows preserve URLs, not verified accession identifiers or rights clearances.

## Media credit & rights

The CSS bar chart, original reading workflow, document layout, and printable receipt are **original Final Vestige Studios explanatory graphics and editorial work** (November 18, 2026). Chart caption: 90 FV editorial gateway cards split into 12 declassified, 24 accountability, 21 engineering, 25 archives, 8 navigation; not reliability, completeness or source quality. Accessible alternative: the same five categories and exact numbers are present in adjacent text. FV owns the visual; no public reuse license is granted. No historical photograph, map, archival scan, private collection item, outside video, icon font, CDN image or unlicensed media was included.

## Independent static readback: PASS

- WordPress edit-context #1338: 90 cards; GitHub HTML readback: 90 cards, 90 distinct HTTPS source URLs; exact title/category/URL **in identical order**.
- Gutenberg original: 12 declassified, 24 accountability, 21 engineering, 25 archives, 8 navigation. HTML embedded JSON: 90 records.
- Candidate: 179,402 characters; GitHub source blob SHA-1 8ab0cbbced610920a30161f1826e818a8c198bea.
- 116 unique HTML ID values, no duplicates, no missing internal anchor targets, 8 labeled worksheet fields.
- JavaScript syntax compiled in V8; external script and media URL checks clean; no inline handler attributes.
- All 90 external links open with noopener/noreferrer. Draft has noindex, print and reduced-motion rules.
- No passwords, user-specific submissions, file uploads, remote network requests or analytics.

## Runtime and release QA: HOLD (not run)

**Static inspection is not visual/browser acceptance.** Browser acceptance for this exact artifact, local CSV download, keyboard/screen reader, 320/390/768/1440 widths, zoom, overflow, print-PDF and browser CSP have NOT run. Local Chromium cannot reach the network because DNS is blocked. WordPress screenshot capture URLs were returned at all four widths for the *published directory*, but the images were not independently inspected. These are not a pass.

Before release: (1) run real-browser QA on HTML with search finding supplemental records and exported CSV opened successfully; test XSS/CSV formula cases, (2) check real production theme and navigation access, (3) confirm item-level rights and sensitive-data hazards for promoted media, (4) upload only a tested stable free artifact, verify logged-in and anonymous public readback/canonical/meta/links, (5) ensure first-publication Jetpack subscriber email/social suppression if creating a new page, (6) correct the live #1338 static 60 labels and false 23/26 counters only under scoped optimistic-locked edits after genuine live QA.

## Separate live issue (unchanged)

[Issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788): live source cards total 90 but some first-render labels still say 60. Supplemental JavaScript uses accountability=23 and archives=26 rather than measured 24 and 25. The public SEO description already says Ninety. This work does **not** update public WordPress, #1340 draft, homepage, Investigations, Preparedness, subscribers or Grok accounts.

## Coordination

Existing [draft PR #3047](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3047). Grok promotion idea *after* real publication: "Ninety links are not ninety original documents" with a live source-receipt demonstration. Idea only, no account access or social post.

**Decision: HOLD draft; no public URL yet.**
