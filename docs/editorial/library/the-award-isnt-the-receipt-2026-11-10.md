# The Award Isn't the Receipt — FV Library evidence & release record

**Owner:** Final Vestige Library Resource Studio. **Reviewed:** November 10, 2026. **Status:** WordPress draft; NOT PUBLISHED. **WordPress:** draft [#2395](https://finalvestige.com/wp-admin/post.php?post=2395&action=edit), child of Library #77, slug `the-award-isnt-the-receipt`, `draft/noindex`.

## Reader problem and unique contribution
The research question: **Does a public federal grant 'award' mean a recipient actually received that amount?** This guide keeps three distinct tracks apart: award/obligation (commitment), outlay (actual disbursement in appropriate dataset), recipient single-audit expenditure/compliance (entity-year report). These cannot be numerically reconciled without matching identifiers, time windows, reporting populations and definitions. Not a new Public Record investigation. Complements the existing Research Sources directory rather than duplicating it.

**Produced in this session:** self-contained original responsive HTML guide with locally executed **Funding Witness Card** (JSON export, print and reset); four-page illustrated printable PDF (method, explanatory diagram, worksheet, 10 linked sources); CSV provenance and rights register; local QA evidence. Files were delivered as conversation attachments, not placed on any public page or WordPress media library. A substantive **static article** was saved to WordPress draft #2395 without script tags. The interactive local tool is *not* being represented as live WordPress functionality.

## Important sourced qualifications
1. The GAO's 2005 glossary distinguishes federal *obligations* from *outlays*. Award-transaction records alone do not establish when or how much cash a recipient received.
2. The FAC states its non-federal-entity Single Audit expenditure thresholds are **$750,000 for fiscal years beginning before 2024-10-01** and **$1,000,000 for fiscal years beginning on or after 2024-10-01**. This is not a per-grant award-value test; different periods/eligibility require checking governing rules.
3. FAC search guidance says its audit-year data go back to **2016**, and its migrated September 2023-and-earlier acceptance dates can appear **one day earlier** than submission.
4. GSA says a newly accepted audit PDF may require **up to 24 hours** to become downloadable. Some Tribal entity PDFs are not publicly downloadable even when the entity has a FAC record.
5. An intentionally fictional sample ($1.2m obligations, $300k outlays, $700k audited program expenditure) illustrates why subtracting unmatched figures cannot establish funds 'missing'. No real recipient or investigation is implied.

## Official source and rights ledger
Last checked **2026-11-10 UTC**: institution-owned pages were retrieved in indexed, readable form through web research, **not** an authenticated API session or every individual audit. Source labels are not redistribution licenses. Any substantive excerpt or reproduced figure from an individual auditor PDF demands its own permission/privacy review.

| Institution / source | Original source | Evidence supported |
|---|---|---|
| U.S. Treasury, USAspending — Advanced Search | [Official page](https://www.usaspending.gov/search) | Award/transaction/subaward finder, source taxonomy; dynamic site. |
| U.S. Treasury, USAspending — Analyst’s Guide | [Official page](https://www.usaspending.gov/federal-spending-guide) | Reporting definitions, filters and data quality. |
| GAO — Federal Budget Glossary (2005) | [Official page](https://www.gao.gov/products/gao-05-734sp) | Obligation/outlay terminology. |
| GSA Federal Audit Clearinghouse — Using FAC data | [Official page](https://www.fac.gov/data/) | Audit package = auditor report and Form SF-SAC; public data vs underlying report. |
| GSA Federal Audit Clearinghouse — Starting an audit | [Official page](https://www.fac.gov/audit-resources/submission-guide/starting/) | $750k threshold before Oct. 1 2024 fiscal-year starts; $1m on or after. |
| GSA Federal Audit Clearinghouse — Search filters | [Official page](https://www.fac.gov/search-resources/filters/) | UEI/EIN/ALN, audit-year coverage and whole-word matching. |
| GSA Federal Audit Clearinghouse — Search results guide | [Official page](https://www.fac.gov/search-resources/results-guide/) | Acceptance-date migration discrepancy and restricted Tribal audit PDFs. |
| GSA Federal Audit Clearinghouse — API resources | [Official page](https://www.fac.gov/api/) | Public API, free Data.gov key and terms. |
| GSA Federal Audit Clearinghouse — Submitted-but-not-yet-downloadable help (Jan. 2026) | [Official page](https://support.fac.gov/hc/en-us/articles/29043839561869-I-just-submitted-my-audit-report-Why-can-t-I-download-my-report-from-Search-Is-there-an-error-with-my-submission) | Up to 24h for report PDF to appear. |
| GSA Federal Audit Clearinghouse — Search resources | [Official page](https://www.fac.gov/search-resources/) | Search and interpretation guidance. |

**Media:** One original 2026 Final Vestige SVG diagram with built-in accessible title and description; one original printable form. No external photographs, document scans, maps, logos, seals, or auditor-authored exhibits downloaded/reproduced. Ownership of the institutional source pages remains with the listed agency. FAC's public-domain assertion applies to FAC **data**, not automatically to every attachment.

## Local standalone QA
- Browser Chromium `page.set_content` at **320, 390, 768 and 1440px**, each with JavaScript on and off: **8/8 PASS**. No document-wide horizontal overflow, no page errors; 10 source entries and original descriptive SVG present in both modes.
- Native browser Blob export, field retention, JSON schema fields and reset: **4/4 width checks PASS** in local Chromium. This is stronger than mock-backed functionality testing, but does not establish secure-origin behavior under WordPress.
- PDF 4 US Letter pages, visually inspected all four; embedded PDF hyperlink counts **0 / 6 / 0 / 16**. Printable record sheet has adequate write-in space.
- WordPress #2395 authenticated edit readback: **draft**, **noindex=true**, **parent #77**, **original SVG exists**, **20 external anchors**, no inline script. WordPress body 9,593 characters. No public Library card or new public URL.
- The tests do **not** certify a production-theme render, authenticated WordPress draft appearance or anonymous public visit. Container DNS prevents external Chromium navigation; WordPress screenshots return URLs rather than inspectable pixels.

## Release gate / coordination
**HOLD** until actual WordPress-theme mobile and desktop visual proof at 320/390/768/1440, keyboard focus/overlay/link checks, and independent anonymous readback are obtained. First-publish requests must suppress subscriber emails (`_jetpack_dont_email_post_to_subs=true`) and automatic Publicize (`jetpack_publicize_feature_enabled=false`), neither of which is exposed as a writable meta option by the current WordPress page-create/update connector. Do not publish without an approved mechanism that sets them on first publication. Do not create a live Library card before the guide has a verified public URL; keep drafts invisible in navigation.

Priority remains **Research Sources #1338**: controlled 90-card repair staged at #2354 and documented [#1788](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1788). Shared browser tooling blocker [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). No changes to Preparedness, Investigations, homepage, newsletters, other agents' pages, or socials.

**Potential Grok handoff after publication:** 'The federal database says $1.2 million awarded. Does that mean $1.2 million was paid?' Do not publish an accusation or any real-recipient illustration without record-level corroboration.
