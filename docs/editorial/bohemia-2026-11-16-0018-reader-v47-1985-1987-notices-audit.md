# Bohemia Spillway — Reader v47 primary-record comparison and guarded draft QA
**Cycle:** November 16, 2026, shortly after 00:18 America/Los_Angeles. **Release:** HOLD. **Post:** WordPress Investigations draft #2488, *The Spillway That Kept Its Names*.

## Editorial coordination
Read live [Final Vestige editorial standards](https://finalvestige.com/editorial-standards/) (last reviewed Aug. 23, 2026), live homepage/Journal context, authenticated WordPress posts and drafts queue, and GitHub issues [#1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). Existing #2488 was resumed rather than creating a duplicate. The Caernarvon draft #2151, other posts, homepage and shared themes/templates were untouched.

## New historically consequential documentary distinction
* [*Haspel & Davis Milling & Planting Co. v. Board of Levee Commissioners*, Louisiana Fourth Circuit, 680 So. 2d 159, September 4, 1996, ¶18](https://openjurist.org/680/so2d/159/haspel-davis-v-bd-of-levee-com-rs), cross-checked against [an independent opinion-text reproduction](https://hallapproved.com/la/cases/appeals/1996/1634298/). Both texts identify the court's summary of Natural Resources Secretary Raymond Stephens's May 16, 1988 affidavit:
  * Application forms made available February 1985.
  * Levee-board restraining-order litigation interrupted implementation in March 1985.
  * Department newspaper notice in *The Times-Picayune* dated February 3, 1987.
  * Department applications became available March 8, 1987.
  * Bohemia claim-evaluation regulations promulgated October 20, 1987.
* The [Rod Lincoln Collection finding aid](https://www.southeastern.edu/acad_research/programs/csls/historical_collections/archival_collections/l_m/lincoln_rod/) separately catalogs a February 21, 1987 newspaper notice. DO NOT equate it with the February 3 advertisement: original clippings not examined.
* **Verification class:** source is an appellate opinion reproduced in two text collections; the referenced affidavit, original newspaper notices, March 1985 restraint, and 1987 Register pages were not inspected. A court's description of an affidavit cannot establish that every individual claimant received notice or a fee demand, secured a deed or was paid. No claim of original access, interviews, archives visit, or resolved payment accounts.

## Controlled writing / source work
* Canonical [Reader Edition v47](./bohemia-spillway-reader-edition-2026-11-14.md) now links source **#56**, notes **56 selected reader sources**, and cites master ledger **85**; [Evidence 85](./bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md) contains the source trail, caveat, discrepancy and follow-up records.
* WordPress #2488 received four optimistic-locking Gutenberg operations: remove redundant pre-archive university-catalogue paragraph, insert the 1985–87 judicial-affidavit timeline before the 1990 postmark passage, append source #56 in the original ordered bibliography block, update source-count paragraph. No full-post overwrite. All writes confirmed against modification and content hashes.
* **Authenticated readback** at site-local `2026-11-16T00:18:04`: post remains `draft`, content hash **`15bd2c56b8bb4b7c9366407936b23bf7e95d809e`**, **226** top-level Gutenberg blocks, **56** bibliography IDs numbered 1–56, **214** same-post citation links, zero missing, duplicate or unreferenced source anchors. Category IDs `9369` and `232815`, featured image **#2484** preserved.
* Safeguards explicitly verified: `jetpack_seo_noindex=true`, `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`. No live publication or newsletter/social action.
* Existing locally hosted documentary images **#2484** (2023 NASA/USGS Landsat, 1280×1280) and **#2485** (2007 USDA/NAIP via NASA, 1125×1280) are still in the first two image blocks with meaningful alt/caption/source metadata. Source attribution and local media-library metadata checked; **public bytes not verified**: independent container requests to both public URLs returned `curl: (6) Could not resolve host: finalvestige.com`. This is not evidence of broken public images.
* Existing original FV evidence diagrams and archival-provenance caveats preserved. No new stock, third-party image hotlinks, unsupported reconstructions or fee-bearing assets. Neither the original March 1990 PDF page nor the signed 2014 settlement/accounting files newly inspected this cycle.

## Publication gate / release held
1. Actually render the **current** authenticated production-theme draft at 390px mobile and 1440px desktop; save inspectable screenshot and DOM checks for full width, title, signup overlays, table overflow, source links and current article art. Prior mshots “ready” URLs are not evidence.
2. Independently fetch public JPEG bytes and inspect in-post caption, copyright/agency credits, loading and alt at both widths.
3. Obtain signed FY2014 settlement and case-level financial entry support, treasury/registry and individual claimant-payment evidence; avoid attributing financial changes to later authorizations without support.
4. Final independent legal/editorial review. The 1987 affidavit, notices, and rule images would support further historical precision but are NOT represented as obtained.

**Decision:** draft held. No homepage, template, other-agent posts, site-wide edits, subscriber mailing, social distribution or paid calls. Grok distribution lane should receive the validated evidence summary only following editorial release clearance; it should not post this held investigation.
