# Final Vestige Investigations — FY2007 Bohemia reserve classification and claims audit
**Run date:** 2026-11-13 (America/Los_Angeles) · **Draft:** *The Spillway That Kept Its Names* v2.8 · **Release:** HOLD

## Coordination and live checks
- Read current [FV Editorial Standards](https://finalvestige.com/editorial-standards/), [live Journal](https://finalvestige.com/blog/) and homepage's investigation section. No same-topic live Bohemia article appeared in the latest published WordPress post list (66 published posts, most recently dated November 2, 2026).
- Authenticated WordPress post queue: Caernarvon #2151 still **draft**, last modified November 12, 2026 at 12:44:30 site-local. Meta read: `_jetpack_dont_email_post_to_subs=true`; `jetpack_publicize_feature_enabled=false`. No edits made to it, homepage, shared templates, subscribers or social platforms.
- Continued the existing Bohemia companion in `docs/editorial/bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md`, owned under [coordination issue #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463). Existing [production theme QA blocker #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589) is unchanged.

## New official primary record actually inspected
**Orleans Levee District / Postlethwaite & Netterville, *Basic Financial Statements and Independent Auditor's Reports, June 30, 2007*.**
Source hosted by Louisiana Legislative Auditor:
https://app.lla.state.la.us/PublicReports.nsf/3ABF8A4700B075598625737600782977/$FILE/00001769.pdf

Original page images personally inspected via document viewer:
- Printed **p. 46**, PDF index 49: Note 11, restricted governmental assets: **$292,522 set aside for legal settlements** (General Fund), separate from **$5,001,136 debt service**.
- Printed **p. 53**, PDF index 56: Note 15 reserve schedule labels **$292,522 “Legal Settlements”**, not “Bohemia Spillway Escrow.”
- Printed **p. 57**, PDF index 60: begins Note 19, lawsuit history and statutory background.
- Printed **p. 58**, PDF index 61: **164 of 220 tracts** with DNR-certified claimant interests **before 1997/1999 amendments**; accounting statement that claims certified by **October 1, 2002** were returned, claims certified as of **June 30, 2005** conveyed; **16 suits as of June 30, 2007**; **$19 million set aside pending appeal**, **July 23, 2007** federal reversal; **August 3** rehearing motion.
- Printed **p. 59**, PDF index 62: legal contingencies combine different matters. Avoid mislabeling all as Bohemia.
- FY2005 [45] and FY2006 [46] **specifically** label reserves “Bohemia Spillway Escrow” ($456,190 and $339,407). FY2007 [47] uses broader “Legal Settlements”; the **difference of $46,885 does not prove a Bohemia payment, transfer or loss** because categories could differ. The **2005-to-2006** $116,783 difference remains unreconciled.
- FY2007 reporting of **$19m set aside pending appeal** is not a beneficiary payment. The appellate holding is controlled by source [44], not by the district's judgment-amount wording.
- The year-end report includes July/August 2007 subsequent-event material; never imply all narrative events predate June 30.

## Manuscript and art
- **v2.8 article amendment:** “The reserve that lost its name” (678 new section words), placed after “The cash on the books.” Source [47] added, continuing numeric ledger [1]–[47].
- Manuscript commit `a284963267021e6849c234381f2588e58b06233c`.
- New original evidence SVG:
  `docs/editorial/assets/bohemia-reserve-label-transition-2026-11-13.svg`, asset commit `9913bbd3f38bb02d3b1051486ea3e532ed4b99aa`, git blob SHA `8c9cac0fa1a89c147a68c6f6a01abbb73fe9e307`.
- Original creator: **Final Vestige Studios**, date **2026-11-13**, rights: **FV original artwork**, independent third-party image permissions not needed; SVG includes no external assets and does not claim to reproduce a historic object.
- Caption: “Orleans Levee District reserve classifications, 2005–2007: two Bohemia-specific entries followed by a broader legal-settlements balance. Neither the 2007 amount nor changes between reporting categories demonstrate landowner payments.”
- Alt: “Bohemia Spillway Escrow was $456,190 in June 2005 and $339,407 in June 2006; in June 2007 the district reported $292,522 under the broader Legal Settlements classification. These categories cannot be assumed equivalent.”
- The exact committed asset SHA **matches** the locally rasterized SVG's `git hash-object`; valid SVG XML, no external assets. Preview render and human visual inspection completed at **390 px and 780 px**, no visible clipping. This is **local artwork QA only**; production-theme render not inspected.
- Source URLs: FY2007 above; prior FY2005/FY2006 URLs in source ledger [45]–[46]. Visual is a documented accounting interpretation, **not** an AI historical reconstruction, direct photograph, original financial-record facsimile or actual payment ledger.

## Remaining release gates and next evidence
1. Obtain signed settlement and registry/escrow statements, official tract-level certification and deeds, plus named payee distributions. Investigate what happened between the specifically labeled Bohemia reserves in 2006 and broader legal-settlement reserve in 2007; request general-ledger transfer/journal details rather than assuming continuity.
2. Verify the legal status and aftermath of the August 3, 2007 rehearing request from actual appellate docket; earlier 2007 opinion [44] is authoritative only for its disposition.
3. Resolve the previously documented Taylor succession fee/principal inconsistency with trial docket and beneficiary/cleared-payments evidence; preserve it as unresolved.
4. Complete documentary-image pixel rights review, site production-theme preview QA at 390/1440, final source/footnote and legal editorial proofread. Do not edit #2151 or first-publish until release gates are met.
5. Newsworthy post-release social note for separate Grok lane: accounting category shift and 164/220 historical certified-tract count; **no social posting authorized**.

**Publish decision:** NONE; WordPress unchanged. **Paid spend:** $0.
