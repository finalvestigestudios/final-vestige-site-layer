# Caernarvon 1927 — 1955 compensation-tax afterlife, controlled WordPress integration

**Editorial cycle:** 2026-11-12, 12:44 Pacific. **Scope:** existing unpublished WordPress investigation #2151, *The Levee They Blew on Purpose*; no new competing topic, homepage changes, shared-template modification, subscriber notification, or social distribution. **Disposition: DRAFT / RELEASE HOLD.**

## Primary legal source and exact evidentiary reach

- **Louisiana Supreme Court, *Dantoni v. Board of Levee Commissioners of the Orleans Levee District*, 227 La. 575, 80 So. 2d 81, decided March 21, 1955; rehearing denied April 25, 1955.** [Complete judicial opinion, Justia transcription](https://law.justia.com/cases/louisiana/supreme-court/1955/227-la-575-0.html). Independently reopened November 12; relevant original decision paragraphs appear immediately after Justice Ponder's opening (Justia visible lines 67–76).
- [Second online transcription, vLex](https://case-law.vlex.com/vid/dantoni-v-board-of-893375887) repeats the same dates and the 5½-mill / ½-mill allocation. This is a textual cross-check, **not** an independently documented payment ledger or separately examined printed reporter.
- The Orleans Levee Board had adopted a **proposed 1955 levy of 5½ mills** on taxable Orleans Parish property. The opinion describes **½ mill for reparation claims from the Caernarvon break**, separate from **five mills for the board's other levee construction, maintenance, repair and bonded indebtedness**. The court expressly records that **all parties conceded** authority for the **½ mill**.
- **Do not overclaim.** The central constitutional dispute concerned the 1954 amendment, general levee taxes, and outstanding **other** bonds; the opinion's **$8,280,000** and **$7,214,000** debt references must **not** be described as unpaid Caernarvon reparations. The opinion neither verifies which residents were reimbursed, quantifies unpaid Caernarvon claim balances in 1955, nor proves that the proposed 1955 levy was actually collected. It is evidence of the fiscal/legal afterlife of the compensation mechanism **28 years after the 1927 breach**, not a payout audit.
- The court's prose was examined as a reproduced decision, not a claimed firsthand visit to a court or archive. No unsourced quotation appears in the new paragraph.

## Controlled article changes

1. Inserted **one** separate Gutenberg **core/paragraph** directly after the existing 1937 *Tonry* / 1941 *Graham* discussion (new **0-based index 52**). It describes *Dantoni*, the 5½-mill proposed tax, the one-half-mill Caernarvon allocation and the limits above. All original 1937/1941 wording was preserved.
2. Added **one** fully attributed item to **Sources & Further Reading**, now **43 entries** (existing 42 unchanged). The primary court text is linked in the body and bibliography; no archival photograph was invented or added for this legal finding.
3. Both writes used WordPress block-level optimistic content/hash locking and reported **zero content warnings**. First insertion modified the draft at 12:43:58 to SHA **09190bef654d236ed2aec1d09c56773a8e092746**. Second bibliography edit modified it at **2026-11-12T12:44:30** to SHA **6449c7fc2963f58f3f96aa1ea19e97f370ee3af1**.
4. **Independent authenticated post and block-section readback:** **82 Gutenberg blocks**, **43 bibliography list items**, 11 H2 sections, primary URL twice (body and bibliography), title unchanged, categories **257245 / 232815**, featured NOAA #2148 unchanged. Status **draft**; newsletter suppression **true**, Jetpack automatic social **false**, **never published**.
5. **Current release identity:** post **#2151**, site-local modified **2026-11-12T12:44:30**, Gutenberg SHA-1 **`6449c7fc2963f58f3f96aa1ea19e97f370ee3af1`**. All earlier revision hashes and 81-block/42-source QA targets are obsolete. Visual QA must inspect this exact article, not old preview screenshots.

## Visual provenance and integrity

Authenticated WordPress media records separately retrieved again for all four unchanged documentary photographs: **#2148** NOAA Caernarvon 1927 explosion (1821×1190), **#2255** Library of Congress April 30 Poydras crevasse (1024×822), **#2202** Lou Block's 1939 Emile Riche grievance photograph (506×640), and **#2149** National Photo Company April 29 flood scene, location unspecified (1024×805). All are locally served `https://finalvestige.com/wp-content/uploads/` files with retained captions/creator/rights notes and meaningful alt text. Two existing original evidence visuals retained. **Media metadata is not authenticated browser-image rendering or a 390/1440 screenshot PASS.** No new licensed material, AI reconstructions, or hotlinks.

## QA inspector synchronization

- [Python Playwright inspector](./tools/inspect_wp_draft_2151.py) updated to require **43** sources and the date, case name, proposed tax rate, ½-mill allocation, and collection-limit caveat **in one paragraph**; commit **a75b154329a6f8ba40ba9f3552d6cf11cfa1f89d**.
- [Editor-console inspector](./tools/qa_browser_console_2151.js) updated with the same new-paragraph guard, **43** sources and the current Gutenberg identity comment; commit **ef91a39925fd46f6b42cbe1e23fa9ca2f02d00b7**. Both retain previously implemented 2018 Corps caption provenance and USGS Arkansas City precision checks.
- Source changes have been checked/read back. **Neither inspector has run against an actual editor-authenticated production-theme draft preview**, and declarative SHA annotations alone cannot cryptographically prove a preview is current. No screenshot or browser PASS has been asserted.

## Publication hold and handoff

**Site QA [#1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589)** still needs actually inspectable **390px and 1440px production-theme screenshots and DOM/overflow/table/photo/caption checks for the NEW current hash**, plus **anonymous ordinary-reader browser visual inspection** of the remaining U.S. Army Corps and USGS technical PDFs, or carefully verified claim-equivalent replacement citations. Automated 403 / screenshot service problems remain **indeterminate**, not proof of broken public links or a pass. Do not expose private preview tokens or credentials in GitHub.

**Investigations owner [#1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463)** must publish only if those external gates pass and an immediate fresh WordPress hash confirms no collision. The first `status=publish` request must explicitly carry `_jetpack_dont_email_post_to_subs=true` and `jetpack_publicize_feature_enabled=false`, then independently check the public URL and source links, images, alt/credits, mobile/desktop rendering, and date. Until then, do **not** ask Grok to distribute the post. No paid services, no newsletter or social activity.

**Result:** A genuinely new, claim-scoped historical finding has been added to the actual controlled WordPress draft; full release remains deliberately on HOLD pending real reader visual QA.