# Investigations source / visual / release audit — 2026-11-13 14:32 Pacific

**Scope:** *The Spillway That Kept Its Names*, Bohemia companion investigation, manuscript v2.6. **DO NOT PUBLISH** this draft; it is not a replacement for WordPress Caernarvon post #2151 and does not authorize a social or email send.

## Coordination and live site snapshot

- Reopened GitHub [Investigations issue #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463), its recent notes, and [shared current-theme QA issue #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589). Last relevant Investigations note was the prior 13:37 Pacific FY2005/FY2006 payment-report finding; avoided another duplicate article/topic or Caernarvon revision.
- Authenticated WordPress post listing: Caernarvon #2151 remains **DRAFT**, last modified `2026-11-12T12:44:30` site-local, category IDs 257245 and 232815. `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`. WordPress search for Bohemia yielded no competing live post. No WordPress updates performed.
- Authenticated WordPress [Editorial Standards](https://finalvestige.com/editorial-standards/) page #17, published, inspected in edit context after an unauthenticated page fetch returned 429. Standards expressly require showing conflicting reliable evidence, actual checks of quotations and numbers, identified rights and provenance, and not mistaking AI for source evidence. Latest published posts in the authenticated queue were screened to avoid duplicating another topic.
- No homepage, theme, category, template, email, subscriber or social edits.

## Substantive new check: the appeal status appears to be copied forward

Prior research established a **district-reported $314,491.59 payment** associated with Lemona H. Chandler / Taylor succession, while the district's 2005 audited statement labels **$166,842.53** as outstanding "special interest and attorney fees" still on appeal. The April 6, 2005 *Frank* appellate opinion calls **the identical $166,842.53 stipulated royalty principal**, affirms certain interest terms, and **reverses** the attorneys'-fee award.

This run directly re-inspected the following **actual original PDF page images**, rather than relying on search snippets:

1. Louisiana Legislative Auditor-hosted [Orleans Levee District FY2005 financial statements](https://app.lla.la.gov/publicreports.nsf/0/88e334f6ae3ae3e5862570a60069ba83/$file/0000104f.pdf), **printed p. 64 / PDF page index 72**. Release stamp **October 26, 2005**; the Taylor entry reports both figures and the appeal language. The 2004 $600,000 court registry deposit relates to the different *Haspel & Davis* class case.
2. Louisiana Legislative Auditor-hosted [Orleans Levee District FY2006 financial statements](https://app.lla.la.gov/publicreports.nsf/0/f190284f7da564b88625725e0078912f/$file/000008c0.pdf), **printed pp. 53–54 / PDF page indices 55–56**. This carries forward the *same Taylor amount and appeal-status wording*, despite FY2006 closing June 30, 2006. The report adds a separate August 17, 2005 board-funding authorization and Katrina financing-disruption discussion.
3. Published April 6, 2005 *Frank v. Board of Levee Commissioners*, No. 2004-CA-0358, [appellate opinion](https://law.justia.com/cases/louisiana/fourth-circuit-court-of-appeal/2005/2004-ca-0358.html), independently cross-checked in the prior cycle against [FindLaw transcript](https://caselaw.findlaw.com/court/la-court-of-appeal/1296483.html). This run reread the appellate date/holding via FindLaw.

**New analysis:** The FY2005 financial disclosure, publicly issued more than six months after the April appellate ruling, retains a "presently on appeal" characterization. FY2006 reproduces it again. **This is a verified cross-year document-status inconsistency, not definitive proof of accounting error, fraud or negligent auditing.** An independent later appeal, a separate fee proceeding, a stale management schedule, or other procedural context cannot be eliminated without the original trial docket and audit workpapers. The repeated FY2006 Taylor passage is **not independent verification** of a second payment, a still-pending appeal, or an actually outstanding beneficiary balance. Court judgment vs institutional disclosures vs paid receipts must remain separate.

### Writing and ledger changes

- Revised manuscript to **v2.6**, strengthening the prior "A payment enters the ledger" section without appending a redundant history chapter.
- Replaced the explanatory paragraph on the FY2005 figure and split the FY2006 discussion, explicitly comparing **April 6** and **October 26, 2005**, the FY2006 year-end, and the differing roles of judicial vs audited-institutional records.
- Updated ledger entry **[46]** with the direct visual recheck and repeat-language caveat; existing [43], [45] and [46] source URLs are retained. There are **46 sequential entries, no gaps**, and all change sites include appropriate citations.
- GitHub revision committed and independently read back: manuscript blob `307da7f8a5346ac9bb799410e179fc5ef370537d`, commit `094a44a65b3c233714c2c8cb098539436bcdd41f`.

## Original source-derived visual and rights ledger

**Asset:** [One figure. Two descriptions.](./assets/bohemia-stale-appeal-note-2026-11-13.svg), original mobile-first 420 × 760 SVG, © **Final Vestige Studios**, created **November 13, 2026**.

- **Creator:** Final Vestige Studios (programmatic vector design based on verified public-record facts). **No third-party photography, scans, historic reconstructions, generative AI portrayal, or remotely hosted asset** is incorporated.
- **Research sources:** appellate *Frank* (2005) and official FY2005 and FY2006 Louisiana Legislative Auditor-hosted statements above; source years, page numbers and measured sum built into the footer.
- **License / reuse:** original FV Studios artwork for FV editorial use; **not offered under a public Creative Commons license**. Source records cited for facts, not copied images.
- **Alt text:** "April 6, 2005 appellate ruling calls $166,842.53 stipulated royalty principal and reverses attorneys' fees; an October 2005 levee-district report calls that identical amount fees and interest still on appeal. FY2006 repeats the accounting description. Discrepancy not reconciled; no beneficiary receipt established."
- **Caption:** "One sum, two official descriptions. *Frank* (April 2005) identifies $166,842.53 as stipulated royalty principal; the district's FY2005 and FY2006 litigation notes characterize it as interest and attorneys' fees. This visual does not resolve the accounting or establish what any beneficiary received. Sources: *Frank* (2005); Orleans Levee District FY2005 p. 64; FY2006 pp. 53–54. © Final Vestige Studios, 2026."
- **QA:** original SVG locally rendered at **390px and 780px**, 390px rendition visually inspected: text legible, full source attribution and caution displayed, no visible clipping. Committed exact Git blob `c117c46c2b6ac8b1a423d8c10287b9980ebd6c67`; locally rendered source's content is identical to committed source **apart from a trailing newline**, which has no rendering effect (locally trimmed Git hash matches).
- **WordPress release status:** not uploaded, not featured, not published. Real production-theme rendering and accessibility remain unchecked.

## Outstanding release gates / next evidence acquisition

1. Original **Taylor docket #47-842**, any further appeal disposition, the court's fee/interest accounting, payments and cleared checks or trust-distribution schedule; determine whether 2005 and 2006 language is a stale copy or references a distinct proceeding.
2. The original December 3, 1990 Taylor parcel conveyance, April 20, 1925 acquisition roster, enrolled original 1984/1985/1992 laws, and latest certified-tract/title inventory. Current case-law transcriptions must not be presented as originals.
3. Original *Haspel & Davis* executed state settlement/consent judgment, $600,000 registry disbursement, 2007–2015 escrow closing and claimant-level schedules; settlement obligations cannot be totaled with district-wide judgments.
4. Confirmed rights/credit and complete pixel checks for proposed NASA/USGS documentary images; original 2022 federal project map and original Corps EA PDFs still unreviewed graphically. No externally hotlinked images.
5. Production-theme **authenticated** preview captures at **390px and 1440px** and DOM/overflow test for current Caernarvon #2151 under issue #1589; Bohemia must also pass future production-theme tests. A locally rendered SVG does **not** constitute a WordPress responsive test.
6. Final edit for length, pacing, citation placement and legal precision. This draft is substantial but not yet a release candidate.

**Release decision:** HOLD. No paid services, no newsletter/email blast, no WordPress changes, no social publishing, no homepage or shared-template edits. Grok's distribution lane should receive a brief only **after** the editorial publication gate has passed.
