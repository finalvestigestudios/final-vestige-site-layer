# Bohemia Spillway — 2007 conditional settlement / original court-file audit
**Investigations desk · November 13, 2026, 12:37 Pacific · draft-only · NOT approved for live release**

## Scope and editorial collision check
- Read current live [Journal](https://finalvestige.com/blog/) (66 indexed entries), [Archive](https://finalvestige.com/archive/) and [Editorial Standards](https://finalvestige.com/editorial-standards/). The Bohemia companion is not already a published article in either; authenticated WordPress search for "Bohemia" returned only Caernarvon unpublished post #2151, while "spillway" search returned that draft and an unrelated Hebgen Lake story.
- Read GitHub coordination [Investigations #1463](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1463) and [shared production preview QA hold #1589](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/1589), including current-snapshot constraints. **Do not touch homepage, templates, Library/Preparedness/Public Record or unrelated posts.**
- Authenticated WordPress readback: #2151 *The Levee They Blew on Purpose* still **draft**, site-local modified `2026-11-12T12:44:30`, featured image #2148 and categories [257245,232815]; meta `_jetpack_dont_email_post_to_subs=true`, `jetpack_publicize_feature_enabled=false`, `jetpack_social_post_already_shared=false`. No WordPress write during this cycle.

## Newly visually inspected primary judicial document
**U.S. Fifth Circuit, *Haspel & Davis Milling & Planting Co. v. Board of Levee Commissioners*, No. 07-30086, decided July 23, 2007.** Original file-stamped 17-page opinion facsimile distributed via Justia: https://cases.justia.com/federal/appellate-courts/ca5/07-30086/07-30086-cv0.wpd-2011-02-25.pdf . Accessible published transcription cross-check: https://law.justia.com/cases/federal/appellate-courts/ca5/07-30086/07-30086-cv0.wpd-2011-02-25.html . Original PDF screenshot pages visually inspected: zero-based indices 1,2,3,4,5,8,9,10 (printed pp. 2–6 and 9–11). Not an interview, separate trial record, recorded deed or authenticated 2026 payment ledger.

**Facts directly traceable to the PDF:**
1. After approximately twelve years of class litigation in state court, the consent settlement recited **$2,318,263.72 designated for immediate payment** and **$18,767,145.26 payable "as and if funds are appropriated thereof"** (printed p. 3 and p. 10); combined settlement terms **$21,085,408.98**. These numbers are contract terms, not actual disbursements.
2. Opinion acknowledges **numerous payments**, but says annual payments did **not** meet the **$2,600,000** benchmark (p. 4); court footnote says a second June 2005 settlement had been **set aside**, and should not be added to the first agreement (p. 4).
3. July 2006 federal takings suit was not an unrestricted second chance to collect the original constitutional claim. By entering comprehensive settlement, the plaintiffs **compromised their takings claim**, and their remedy was to enforce rights under the **state-court settlement and consent judgment**; the federal appellate court reversed the federal takings judgment, dismissed the takings claim with prejudice, and vacated seizure writs (pp. 9–11). This is distinct from *Vogt* (Fifth Circuit 2002, 294 F.3d 684), which proceeded through a different procedural route.
4. **Numerical conflict IN THE FILED OPINION:** introductory appealed judgment `$17,442,332.87` on printed p. 2; earlier district judgment `$17,442,332.96` on p. 5; amended district judgment `$17,442,322.87` plus prejudgment interest `$205,331.98` on p. 6. Some changes are procedural, and the introduction is inconsistent with the amended figure; the original district judgments are not obtained. Narrative uses **approximately $17.44 million** for the federal judgment and discloses all three appearances rather than silently resolving the discrepancy.

## Manuscript / source ledger / factual QA
- Continued existing companion [*The Spillway That Kept Its Names*](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/main/docs/editorial/bohemia-spillway-2026-11-12-land-roster-rights-claim-investigation-draft.md), updated to **v2.4**, with new `The settlement with two price tags` section; new source [44] cites precise appellate PDF and inspected pages.
- **44 sequential source ledger entries** verified after GitHub readback; corrected two erroneous cross-references naming 2002 *Vogt* as source [6] (which was 2007 *Haspel*). Proper reference is [11]. Never use the state settlement to prove full satisfaction nor to claim nothing was paid. The separate 2023 public-board minutes [21]–[22] reported institutional settlement payments, without claimant-level reconciliation.
- Manuscript commits `79fe8d3fba484fa55ba45d017e173fe40370acc7` (original reporting and citation fixes) and `0d45c0ef73af18faed97d6db24966b71d08d5d74` (pixel QA annotation).

## Original rights-safe artwork
**Subject:** A settlement is not a payment record. Original text/vector illustration of the proportionate **11% immediate term** and **89% appropriation-contingent term** (rounded). No source-photo copy, payee likeness, archival simulation, AI photograph, external linked image or hotlink.

- Creator: **Final Vestige Studios**; date **November 13, 2026**; rights **© Final Vestige Studios**.
- Source and fact-check: Fifth Circuit original 2007 PDF pp. 3–4, 10–11 [44]. Caption and accessible alt text recorded in companion manuscript v2.4 under `Original source-derived visual`.
- Source 1: [1200px desktop vector](./assets/bohemia-2007-settlement-terms-2026-11-13.svg), GitHub exact blob SHA `83a6d4e091602e77e0f9a301dc244b0a34306849`.
- Source 2: [390px art-directed mobile vector](./assets/bohemia-2007-settlement-terms-mobile-2026-11-13.svg), GitHub exact blob SHA `ce104d7378abb8b5bf73104f1b912399aab0a23c`.
- Both source blobs were independently retrieved from GitHub; corresponding local SVG bytes matched Git blob hashing exactly; XML parse passed, titles/descriptions and `viewBox` present, no `<image>` or third-party network dependencies (the standard SVG XML namespace is not a remote asset).
- The **exact desktop** source was rasterized at **1200px**; exact mobile source at **390px** and **780px**. Reviewed 1200px and 390px previews: text, figures, footer credit, and condition language are readable and unclipped. These are **artwork-rendering checks only**, not a site-theme screenshot.
- Pending: approved WP-local media hosting, attachment caption and alt, and authenticated front-end render in actual production WordPress theme at 390px/1440px. No media uploaded.

## Editorial release decision — HOLD
- Published: **nothing**. No newsletter, Jetpack Social, Grok social posts, homepage edit, template change or paid services.
- **Caernarvon #2151** still needs #1589's authenticated browser screenshots and DOM/overflow checks at 390px and 1440px on the exact unchanged current draft; outstanding Army Corps/USGS source-image checks; human copyedit.
- **Bohemia** still needs original enrolled 1984 statute and 1925 roster, land conveyances and specific post-judgment payment records (including Taylor succession); original agreement and district judgments in *Haspel*, publication-image clearance, full manuscript structural edit, and WordPress actual-theme QA. Court source and original diagrams alone do not establish current claims or release quality.
- **Potential Grok distribution handoff, NOT authorized for social release:** after verified publication, tease the legal twist that a settlement could recognize a large amount while making its largest component contingent on appropriations; do not say the whole amount was unpaid or owed today.

**Cost:** $0. Draft and source artifacts remain in the established Investigations GitHub editorial lane.
