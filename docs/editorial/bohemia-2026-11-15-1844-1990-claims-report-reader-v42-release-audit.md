# Final Vestige Investigations — Bohemia Reader v42 research, staging and release audit

**November 15, 2026, 18:44 Pacific.** **RELEASE HOLD / unpublished.** Investigations post #2488 *The Spillway That Kept Its Names*.

## Scope and collision prevention

Read the live [editorial standards](https://finalvestige.com/editorial-standards/) and the current WordPress publishing queue. Reviewed [Investigations editorial coordination #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463), [site-wide production QA #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) and their current comment histories. Continued the existing **Bohemia** investigation in **WordPress draft #2488**. No new duplicate post, no write to the distinct Caernarvon 1927 draft **#2151**, published journalism, homepage, shared template, navigation, social accounts or site-wide settings.

## Previously unincorporated official primary record

**Reader citation #55 / master dossier Evidence 84:** Louisiana Department of Natural Resources and Office of the State Register, [*Louisiana Register*, Vol. 16, No. 3, March 20, 1990](https://www.doa.la.gov/media/uuhfce1r/march.pdf), *Notice of Intent, Return of Bohemia Spillway Lands*, fiscal and economic impact statement, **printed pp. 266–267**.

**Verification:** Original government-hosted PDF *searchable text* read, including the fiscal impact paragraph, and compared with the [September 20, 1988 prior official DNR proposal](https://doa.louisiana.gov/media/td3k1ksv/september.pdf), Reader #54 / master Evidence 83. Original **March 1990 PDF page-image screenshot attempts failed due 16.9 MB document limit**; no actual original-page image or typography was visually inspected. Site authority, title, printed pages and searchable text are evidenced; photo/page-image verification has **not** passed.

The earlier **1988 official fiscal statement estimated** 26,000 future Bohemia applications and 12,000 persons paying a $175 deposit. The **March 1990 fiscal statement reports the department had received 26,000 claims**, a meaningful evidentiary change in tense. This is **an agency-reported aggregate filing count**, not an audited unique claimants list, certified approvals, recorded titles, timely filings, processed deposits or restitution delivered.

The March 1990 notice additionally **estimated**, not documented as collected or spent, a **$450,000 advance-deposit shortfall**; $150,000 expected later recovery; **$300,000 projected net state implementation cost**; and indigence potentially applying to 30% of claims, described as **as many as 8,000** (30% of 26,000 = 7,800, rounded). It proposed an indigence questionnaire, three affidavits and deadlines with appeal mechanisms; **a notice of intent is not evidence of final adoption**. It references court-ordered procedural requirements, but the underlying order was not verified. Do not call the deposit shortfall missing royalties, or the projected 8,000 verified pauper determinations.

## Original graphic and rights ledger

[Original vector SVG: “The same 26,000. Two different claims.”](./assets/bohemia-1988-1990-claims-filing-v42.svg)

- **Creator:** Final Vestige Studios.
- **Date:** November 15, 2026.
- **Rights:** Copyright © 2026 Final Vestige Studios, all rights reserved; wholly original studio artwork, no imported documentary photography, historical maps, archive scans, paid images, remote web fonts or external image dependencies.
- **Sources:** the 1988 official DNR notice, printed pp. 648–649; the 1990 official DNR notice, printed pp. 266–267.
- **Alt:** “1988 Louisiana agency forecast of 26,000 Bohemia applications compared with March 1990 agency report of 26,000 claims received; neither counts approved claims or payments.”
- **Caption:** “Same 26,000, different evidence. The 1988 fiscal statement forecast applications; the 1990 state statement reported filings. © Final Vestige Studios; Louisiana Register, 1988 and 1990. Not a claimant registry or payment receipt.”
- **QA:** independently fetched and inspected Git blob, self-contained <svg>, accessible title/description, embedded provenance and a 780×940 viewBox. **Standalone pixel rendering and actual WordPress current-theme visual screenshots have not passed**. The WordPress post uses a separate first-party HTML rendering with accessible caption, self-contained styles and linked SVG source. No remote visual hotlinks.

**Preexisting documentary photography:** WordPress-local media IDs **2484** (NASA/USGS Landsat 8 acquired February 13, 2023) and **2485** (USDA/NAIP aerial acquired September 20, 2007). Independent authenticated media-library reads confirmed JPEG MIME types, dimensions, nonempty alt and source-dated captions. **External anonymous image-byte loading/production-theme render not independently verified.** No new third-party image used this run.

## Writing and guarded WordPress staging

- [Reader edition v42](./bohemia-spillway-reader-edition-2026-11-14.md): 3 substantive analytical paragraphs under the new subsection **“When an estimate became an agency count”**, original figure, reader source #55; commit `e40ef56300d6e7400a8ec6a6094c8109327444cd`, independently fetched blob SHA `18dd7077c6f68e7fd99e9f974dad2bc4970ada2a`.
- [Master evidence dossier Evidence 84](./bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md): filing-count category, fiscal forecasts, proposed-rule status, exact source and further required records; commit `1c59bcaf432ec66cd84f5f583f29f16cba7c39ce`, independently fetched blob `fd7ebb61bdacbeca7056a97b43ea44afd1a8fa90`.
- Original [SVG](./assets/bohemia-1988-1990-claims-filing-v42.svg) commit `9f462dbb32f6ab9ae967fba8ca6a74038cc7d04a`, independently fetched blob `2f0d55462acdbd314b64b37f0aef00a252c9f9ef`.
- WordPress targeted **optimistic-lock single-block** edits to post #2488 **only**, inserting one h3, three source-linked paragraphs, one `core/html` original diagram before “The accounting was already required”; targeted replacements of existing bibliography intro and ordered source list. **No whole-post rewrite**, no category/media/SEO/global settings changes.

**Definitive independent authenticated WordPress post and section readback after all edits:**

- Modified **2026-11-15T18:44:24** (site-local), serialized Gutenberg SHA-1 **`8b35fb2a323ba3d7af62ecc0b6072e88795dcd66`**.
- **249** top-level Gutenberg sections.
- **55** unique consecutive numbered bibliography target IDs **1–55**; **231** same-post citation links; **zero** missing target IDs, duplicate target IDs or orphan citation links.
- Correct bibliography-intro totals **55 reader sources, 84 dossier evidence entries**, source #55 and original figure present; five inserted sections at indices **58–62**.
- **DRAFT**, `jetpack_post_was_ever_published=false`, **_jetpack_dont_email_post_to_subs=true**, **jetpack_publicize_feature_enabled=false**, **jetpack_seo_noindex=true**; categories **[9369,232815]**, featured media **#2484** unchanged.

## Publication decision — HOLD

**Do not publish yet.** Material release blockers: (1) authenticated editor WordPress current-theme actual screenshots and responsive/overflow/link checks at **390px and 1440px for this exact hash**, including new infographic, two documentary photos and 55-source bibliography; (2) independent anonymous successful loading of media IDs #2484/#2485; (3) **original-page visual QA for the March 1990 official PDF**, underlying referenced court order and reconciliation with final May 1990 promulgation; (4) signed fiscal-2014 settlement terms, FY2014 case-level audit/journal bridge, registry release and claimant payment records sufficient to distinguish an accounting reduction from beneficiary disbursement; (5) qualified independent legal and structural editorial review. Current reader manuscript is now over 26,000 words and may require significant deduplication and narrative tightening rather than further accumulations of sidebars before public release.

**No release, subscriber mailing, Grok or other social-platform publication, homepage/template edits or new paid service. Additional spending: $0.** 
