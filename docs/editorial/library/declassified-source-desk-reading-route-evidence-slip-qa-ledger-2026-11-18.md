# Final Vestige Library — Declassified Source Desk reading route / Evidence Slip
**Checked:** 2026-11-18 12:42 Pacific. **Status:** WordPress DRAFT, not released. **Owner:** Library editorial only.

## Scope and reader problem
The existing *Declassified Source Desk* in WordPress draft **#2917** had five substantive Gutenberg blocks totaling about 96,804 serialized characters. Each was researched, but the five modules lacked an immediately usable choice of reading routes. The new original **11,646-character introductory Gutenberg HTML block** gives readers a no-JavaScript map to the twelve-source directory and four case studies, plus a six-cell printable **Evidence Slip** (five research prompts and one access/rights receipt). It does not add another guide or duplicate an existing Library URL.

**Source:** [reading route and original CSS/worksheet](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/review/library-declassified-source-desk-20261118/docs/editorial/library/declassified-source-desk-reading-route-and-evidence-slip-2026-11-18.html)

## WordPress write and independent readback
- Target: site `finalvestige.com`, page `2917`, parent `77`, slug `declassified-source-desk`.
- Scoped mutation: `page_sections_insert` at index 0; page remained **draft**, with `jetpack_seo_noindex=true`.
- Optimistic lock used exact preceding `modified=2026-11-18T11:37:55` and content hash `17284c4e4f627878a75153ad12eef5171e70952d`.
- Readback: `modified=2026-11-18T12:41:37`; serialized content **108,450 characters**; **6 blocks**. New first block matches the GitHub file byte for byte, and **all five earlier block hashes are unchanged**.
- Old hashes preserved, in order: `f80728c674aef2ef307bdc8e2b094109f3fc1d68`, `61e79bcae2129d556e1f9400894f6a00441da038`, `7e97d83e67f8b6795396e99698fd0be50d809905`, `0665e3702fc06684ee92676c9c91645ca07b4a59`, `b5f1f10f3d513c98c76fa14227ff7ad75ea958e9`.
- Source checks on complete draft: **no duplicate HTML IDs** and **no missing internal fragment targets** (17 fragment references checked). New route contains five distinct in-page destinations, all verified against the existing stored blocks; no external scripts, iframes, photographs or third-party scans.
- WordPress write returned **no content warnings**.

## Source and rights ledger (links checked 2026-11-18)
1. [U.S. Department of State, FRUS Iran, Editorial Note 225](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/d225). Official textual editorial note: later memoir claim about a June 25 meeting; editors say no official record found and cite separate chronology. **NOT** an inspection of the claimed meeting's original minutes or the original memoir.
2. [U.S. Department of State, FRUS Iran, Editorial Note 251](https://history.state.gov/historicaldocuments/frus1951-54IranEd2/d251). Official editorial note reproducing/referencing one July 24, 1953 memorandum printed previously as FRUS Volume X Document 335. Two publication locations, **one documentary witness**. **NOT** inspection of the underlying physical memorandum.
3. [U.S. National Archives, Using the Catalog](https://www.archives.gov/research/catalog/help/using). Official public guide explaining catalog descriptions and digitized object access. The existence of a catalog entry does not establish that an original scan was inspected.
4. [FV Editorial Standards](https://finalvestige.com/editorial-standards/) and [FV Research Sources](https://finalvestige.com/free-resources/research-sources/): institutional and internal crosslinks; public URLs were independently checked.

**Visuals and licensing:** Original FV CSS process diagram and printable text field sheet only. Author/creator Final Vestige Studios, created November 18, 2026; explanatory artwork, not historical material. No external scans, photos, maps, seals, videos or facsimiles copied. Linking to government publications does not imply unrestricted rights for items inside those archives; permissions remain object-specific.

## Public readback and unchanged pages
Independently checked through WordPress signed-out rendered-page inspection:
- `https://finalvestige.com/free-resources/` — HTTP 200 and expected canonical.
- `https://finalvestige.com/free-resources/research-sources/` — HTTP 200 and expected canonical; its **90-card/stale-60-copy discrepancy remains unresolved** under issue #1788.
- `https://finalvestige.com/editorial-standards/` — HTTP 200 and expected canonical.
- `https://finalvestige.com/free-resources/declassified-source-desk/` — HTTP 404 signed out, correct for an unpublished draft.

## Unpassed release gates — HOLD
Actual **production-theme** screenshots and live viewport inspections at **320 / 390 / 768 / 1440px**, real keyboard and screen-reader pass, and print acceptance have **not** been completed. CSS breakpoints and raw markup checks cannot substitute for these. Publishing requires a verified first-publish route with `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false`, neither exposed by the current page-update connector; default newsletter OFF is not a sufficient explicit safeguard. Do not publish, add a public Library card or send promotion until those gates pass.

No public WordPress page, Library index or other team-owned section was changed. No email, Jetpack publicize, Grok account change, paid call, or upload of third-party images occurred.

**Grok-only handoff concept (post-publication):** “Five official links. One underlying witness. Find the document before you count the citations.” No promotion requested or initiated.
