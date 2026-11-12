# Caernarvon 1927 — claim-page documentary QA handoff
**2026-11-12, 10:34–11:00 Pacific | Investigations #1463 | shared release gate #1589 | DO NOT PUBLISH**

## Scope, revision, and coordination

Continue the existing original WordPress investigation **draft #2151**, *The Levee They Blew on Purpose*. Last authenticated readback in this cycle: status **draft**, modified `2026-11-12T07:43:20` Pacific (site-local), 81 serialized Gutenberg blocks, 42 bibliography entries, featured-media ID 2148. The established source-edit fingerprint **`e89879d2b34a53de75d04f2a92bbab832de5aaf3`** remains the handoff reference from the earlier verified revision; this run did **not** recompute it or edit WordPress. Registered `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false`; the post was never published. Preserve homepage, theme and other agents' pages.

## Concrete QA tooling defect and correction

The [anonymous source inspector](tools/inspect_anonymous_pdf_sources_2151.py) formerly rasterized **only the first and last page** of any successfully fetched primary PDF. That can make an image capture misleadingly reassuring: the Bonnet Carré caption and the Arkansas City peak-flow methodological caveats are on **interior pages**. A cover and back page cannot demonstrate that those actual claims appear correctly in the cited document.

In [commit 49559aa5](https://github.com/finalvestigestudios/final-vestige-site-layer/commit/49559aa5d4464fea9e0408aae453c9d595f8e00f), the existing script was amended to:
1. Compare *page-by-page extracted text* against claim-oriented terms per USACE/USGS source, normalizing whitespace and case.
2. Rank matching pages by number of located terms and choose up to **two** top claim-bearing pages, in addition to first/last reference pages (up to four rendered pages per document).
3. Report candidate **one-based PDF page numbers**, matched phrases, selected raster page numbers, and an explicit no-text-match warning for scanned/unsupported PDFs.
4. Preserve independent ordinary-browser PDF-viewer screenshot attempts, the no-credential behavior, and `source_release_gate=NOT_PASSED` until **human visual inspection**. Neither extracted text nor a screenshot filename is a visual PASS.

The replacement's two-keyword/one-keyword ranking order was checked in a deterministic local algorithm test; the updated GitHub file was independently fetched and its new logic and release-hold behavior confirmed. The full script has **NOT** been run successfully against the government documents in a graphical internet-enabled Chromium environment this cycle, and rendered pixels have **NOT** been examined. No browser availability claims are made.

## Claim-level sources to inspect next

| Document | Direct narrative dependency | Page-level test |
| --- | --- | --- |
| USACE New Orleans District, earlier Bonnet Carré brochure | Existing draft quotes `With MRC approval` in its discussion of the distinction between non-objection and formal authorization | Find exact original caption *in that edition*, not just a secondary transcription. Do not presume that the 2018 and earlier brochures are independent historical witnesses. |
| [USACE, *Bonnet Carré Spillway* (Dec. 2018)](https://www.mvn.usace.army.mil/Portals/56/docs/Recreation/BCS/Brochures/BC%20spillway%20booklet%20Dec%202018%20.pdf) | Retrospective `saved the city` claim; same caption includes `With MRC approval` | Locate and inspect the actual caption page; treat `saved` as an institutional retrospective, not a measured no-cut counterfactual. |
| [USGS 2008, Appendix A: Mississippi River](https://pubs.usgs.gov/sir/2008/5164/pdf/sir20085164_MississippiRiver.pdf) | Arkansas City hypothetical peak about 2.47 million cfs vs April 20 Chicot reported measurement 1,712,000 cfs | Locate the Arkansas City discussion on printed pp. 231–232; visually inspect the 2,470,000 vs 2,472,000 sources and the caution about unavailable raw measurement/calculation. |
| [USGS 1994, OFR 94-275](https://pubs.usgs.gov/of/1994/0275/report.pdf) | Supplementary bibliography item; *not* an article-body sole-source dependency | Validate bibliographic identity / reader accessibility or document the exact substitute or necessity of retention. |

**Important limitations:** direct automated official-PDF fetches and online screenshot operations have previously returned HTTP 403 or payload-size errors. That does **not** prove ordinary-browser unavailability. The indexed official USGS 2008 Appendix A text and USACE 2018 text support careful *text-level* quotation checks, not actual anonymous PDF-viewer legibility. This run's web screenshot attempt on the large 1928 Congressional Record document also failed because of source size; no screenshot was fabricated.

## Existing visual evidence, production gate

Four FV-local documentary photographs (NOAA media #2148; LOC #2255, #2202, #2149) were re-read via authenticated WordPress media metadata: all four retain local image URLs, credits, meaningful alt text and positive pixel dimensions. Two original evidence visualizations are already embedded in the draft. These are **metadata checks, not current-theme rendering checks**.

The independent Site QA lane must still obtain **actual authenticated frontend draft preview pixels and DOM checks at 390px and 1440px**, confirm image loading, readable diagrams, bibliography and links, and inspect the ordinary-reader official-source pages. Do not expose preview URL, cookies, authentication storage or screenshots in public GitHub. Until both gates pass, leave WordPress #2151 **draft** and do not trigger email/social/Grok distribution.

## Run accounting

- Research: live Editorial Standards, Journal/latest posts, both open GitHub issues, current draft, official source references and existing ledgers inspected.
- Written: this claim-page release-evidence note and targeted update to the public-document reader inspector.
- Visuals: existing 4 archival photo records inspected; no new assets imported or AI images generated; no documentary-page screenshots verified.
- Published: none. Additional paid services: none. Homepage, shared template, WordPress content and social channels unchanged.
