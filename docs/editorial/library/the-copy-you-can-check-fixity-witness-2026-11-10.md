# The Copy You Can Check — digital-file fixity research and release record
**Library editorial asset** | November 10, 2026, 16:35–16:48 Pacific | **DRAFT / PUBLIC HOLD**

## What problem it solves
Researchers can download a PDF or digitized report, lose the download's precise provenance, and later encounter another file with the identical name. A SHA-256 checksum plus the institution's catalog ID, acquisition time, original URL and rights/access notes lets them verify agreement of *bytes*. It does **not** certify authenticity, custody before acquisition, historical truth, date of original production or copyright clearance.

**Distinct from existing FV assets:** [The Page That Changed](https://finalvestige.com/free-resources/the-page-that-changed/) reconstructs changes to online records and archived web versions; the draft *Scan Witness* (#1591) compares digitized image surrogates. This asset treats **local binary file fixity**, independent custody of the first digest, rechecks and retaining both versions if a discrepancy appears.

## WordPress
[Nonpublic draft #2393](https://finalvestige.com/wp-admin/post.php?post=2393&action=edit) — child of Library #77; slug `the-copy-you-can-check`. WordPress authenticated **edit readback**: status **draft**, `jetpack_seo_noindex=true`, last modified `2026-11-10T16:47:03`, body **9,756 characters**, **one original inline SVG**, ten source/related-article links, **zero scripts**. The WordPress draft intentionally describes but does not link to an unhosted downloadable tool. No public navigation/card, landing page, Preparedness or Investigations page changed.

## Locally completed release candidate (automation conversation attachments)
- **The_Copy_You_Can_Check.html**: self-contained responsive article and *Fixity Witness Desk*, Web Crypto SHA-256 for an acquired file plus optional comparison, 100 MB memory guardrail per file, institutional/context form, privacy-local processing and JSON export. Original vector diagram has accessible title and description. No external media or requests.
- **Fixity_Witness_Field_Card.pdf**: three printable pages including six-step method, fourteen-field blank ledger, limitations and seven clickable institutional references.
- **Fixity_Source_Rights_Ledger.csv**: seven official/institutional destinations, factual scope, rights/access caveats and November 10 review entries.
- **README_Release_Hold.md**, SHA-256 manifest and ZIP of finished files. No external images reproduced, no new spending.

## Institutional sources and boundaries (source review November 10, 2026)
1. LOC, [Data Integrity Management](https://www.loc.gov/programs/digital-collections-management/inventory-and-custody/data-integrity-management/) — establish and recheck fixity early; indexed text retrieved, direct automated open HTTP 403, **not** a broken-visitor-link finding.
2. NIST, [FIPS 180-4 Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) — SHA-256 technical digest standard; does not validate historical authorship.
3. LOC, [Keeping Personal Digital Records](https://digitalpreservation.gov/personalarchiving/records.html) — versions, naming, geographically separate copies and periodic readability checks.
4. NDSA, [Levels of Digital Preservation](https://www.ndsa.org/activities/levels-of-digital-preservation/) — **version 2.1**, announced **March 23, 2026**; official redirect and [announcement](https://www.ndsa.org/2026/03/23/announcing-version-2_1-of-the-ndsa-levels-of-digital-preservation.html) verified.
5. NARA, [Digital Preservation](https://www.archives.gov/preservation/digital-preservation) — framework and risk management.
6. LOC, [Digital Preservation](https://www.loc.gov/preservation/digital/) — formats, metadata and monitoring.
7. LOC, [Born-Digital Manuscript Access](https://guides.loc.gov/born-digital-access/placing-a-request) — Digital IDs and some on-site or copying restrictions; last updated September 22, 2026.

All third-party sources are **linked only**; archival photographs, reports, standards text and scans are not copied. Original FV illustration depicts a schematic process, not historical evidence. Rights to individual archive files must be assessed at the object level.

## QA — what actually passed
- Standalone Chromium `page.set_content` rendered at **320 / 390 / 768 / 1440 px** without detected page-wide horizontal overflow or browser JavaScript errors. A 390px screenshot was visually inspected; this is **local HTML**, not WordPress-theme inspection.
- Browser policy blocked `file://`, `localhost`, and routed external navigation. Web Crypto's `crypto.subtle` was not available in the insecure about:blank test context. A **clearly marked SHA-256 mock adapter backed by Python hashlib** verified the tool's file selection, matching/non-matching digest branches, known vector, JSON export and reset. Native secure-origin hashing must still be checked separately.
- Three-page PDF rendered and inspected; seven embedded institutional links present, no blank page. ZIP integrity check passed.
- WordPress **edit-context readback** confirmed draft metadata/content/one SVG; not a public render.

## Publication gates / next action
**HOLD.** Obtain actual current-theme inspectable screenshots of WordPress draft at 320/390/768/1440 and a keyboard/accessibility pass. Confirm native Web Crypto in secure HTTPS context and provide accessible safe hosting for offline HTML/PDF without unsupported file formats. Verify primary link/media health and public anonymous URLs. Explicitly establish first-publish email suppression (`_jetpack_dont_email_post_to_subs=true`) and social suppression (`jetpack_publicize_feature_enabled=false`) in the actual first publication operation — the current `wpcom_mcp_pages_create/update` schema cannot set those keys. Do not publish or add a card without these gates. Existing [Research Sources integrity issue #1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788) remains separately owned; shared browser QA escalation [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) remains open.

Grok promotion idea, **deferred until publication**: "The document has the same name. Is it the same document?" No social/account actions taken.
