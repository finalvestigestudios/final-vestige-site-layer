# R378 — Authoritative Registry Fallback, Claim/Citation Safety and Commerce Custody

**Status: DRAFT / HARD HOLD; review artifact only. Issue #136; commercial issue #820; charter #818.** Observed 2026-11-14 PT; stacked exactly on R377 commit a95afe75fd842e2a0743ae589ec2c04583a30b2c. No manuscript, editorial status, public route, WordPress, CMS, navigation, sales offer, analytics or social queue changes.

## New authentic resolution (important correction to R377)
R377 identified three IDs absent from **the nine contributor-fragment crosswalk**, not necessarily absent from the complete build. Readback of the **original authoritative preparedness/sources/register.json Git blob b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77** proves all three occur in the BASE register:

| Article 11 ID | Base destination / function | Human link check | Disposition |
| --- | --- | --- | --- |
| cdc-botulism-prevention | https://www.cdc.gov/botulism/prevention/index.html — CDC general botulism prevention, not a jerky processing formula | false | PATH PRESENT / safety HOLD |
| fsis-home-cure-qa | https://ask.fsis.usda.gov/article/How-do-I-safely-cure-meats-at-home-to-avoid-botulism — USDA FSIS introductory curing discussion, not a tested jerky formula | false | PATH PRESENT / direct retrieval timed out / HOLD |
| nchfp-cure-smoke | https://nchfp.uga.edu/how/cure-smoke — topic/index overview, not a specific tested procedure | false | PATH PRESENT / safety HOLD |

All three have author-specific nonempty meta.source_use descriptions; each base row records verified_on=2026-10-29, **machine-checked only**, with human_link_check=false. The food fragment lacks these three identifiers. Original build.Library.source_for selects a Food-owned variant when present and otherwise falls back to the BASE row; sources/crosswalk.json maps safe-jerky-dehydration to origin food. Consequently the prior three **fragment** gaps do not justify inventing new source IDs or falsely alleging three globally missing citations. This is a **static source-path reconciliation**, not a complete native Python build pass.

Special caution: original nchfp-jerky is an unverified BASE placeholder upgraded by the Food contributor at the same URL. That Food-specific reading scope is not interchangeable with Historical Food's reading scope or a generic website URL. The R375 five source-record collisions, R376 Shelter forks, and R377 disputed wild-game/jerky claims remain unresolved.

## Source and safety verification
- Direct independent public page read on 2026-11-14 PT: CDC botulism prevention page (dated **Feb. 26, 2026**) and NCHFP Curing & Smoking index reachable. USDA Ask FSIS article timed out; no human-link approval is granted.
- CDC Trichinellosis prevention (dated **March 12, 2024**) explicitly warns that freezing wild game may fail against freeze-resistant species: https://www.cdc.gov/trichinellosis/prevention/index.html . This materially contradicts Article 11's general wild-game freezing framing; manuscript remains unchanged and nonpublic.
- No unsupported “medically safe,” “safety approved,” “human link checked,” “QD PASS” or “ready to publish” status is assigned.

## New deterministic read-only gate
tools/r378_authoritative_registry_claim_gate.py pins eight original Git blob identities and checks: source-origin selection, exact original 71 citation occurrences and 11 citation IDs, complete nonblank article-specific source_use, BASE-only three-ID fallback, no synthetic Food shadowing, nchfp-jerky upgrade semantics, URL HTTPS/date/reading-scope integrity, draft/pending states, R377 custody, and preservation of two disputed-claim review anchors. It reports source_path_resolved separately from human-link or emergency-safety approval and **always exits 2**. It writes nothing.

tests/test_r378_authoritative_registry_claim_gate.py contains **81 isolated synthetic tests** for missing/duplicate/corrupt citations, wrong origins, changed review flags, false publishing states, altered source uses, bad URLs, and mutation attempts. These test the committed Python logic on synthetic fixtures, not authentic full-site compilation. Exact original 35-article build, 50 WordPress drafts plus 50 preview pairs, real browser/print QA, independent safety and source review remain **NOT EXECUTED/NOT APPROVED** in this environment.

## Upstream and independent QA (no branch modifications)
All seven Claude contributor heads and both Shelter continuation heads matched their nine original R374 branch pins on this run (see #136). Independent draft QA PR #157 exact head 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; synthetic fixture PR #169 e9cd7766dac59d47ab467d8945269b9146c2aef5; dependent corrective #2205 bbcf1859768624c611df4abadc564c18247cf32a; homepage lead #1689 f55c36b6598eec558dd8bb24e4c8988becc51be0. Review untouched; #169's second canonical fixture-write risk is addressed in separate dependent #2205 and still requires native verification. Do not merge or overwrite any of them.

## Conversion-first acceptance (OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER)

1. **One existing rights-cleared FV Preparedness paid pack → payable checkout → CONFIRM PRODUCT FIRST.** No verifiable FV-owned/licensed, accepted, deliverable and refundable Preparedness SKU was authenticated. Verify product ID, title, price, seller status, delivery/rights, checkout acceptance, fee/refund treatment *before* permitting any paid CTA. **HOLD; Founder/Commerce.**
2. **Published Grok family-emergency-contact asset → existing free official-source Archive → verify asset ID/hook/rights/mobile destination and consented UTM against TASK-008.** No verified matching published asset ID has been supplied. Do not substitute unrelated history videos or touch Grok's creator queue. **UNVERIFIED; Grok/Praxxis.**
3. **Free family household plan → optional Tool #104 card → physical trim/printing, no-JS, child privacy, emergency-source and accessibility reviews.** Prior R368–R373 are synthetic/review dockets only; Tool #104 remains private. **HARD HOLD; Preparedness/qualified reviewers.**
4. **Qualified human sessions → relevant CTA → confirmed lead → merchant-confirmed paid order → refunds/fees → realized net revenue per 1,000 qualified sessions.** Existing approved Claude analytics only; no duplicate tracking script, no invented order value, no claim affiliate clicks are sales. Compare 7-/30-day cohorts with small-sample flags. **NOT COMPUTABLE; Claude/Commerce.**

Proposed **unposted free-only CTA**: “Start With Trusted Preparedness Resources” → https://finalvestige.com/preparedness/ . Not an approved downloadable pack or product upsell. No retired water freebie or change to existing offer status.

**Release governance:** Keep **DRAFT / HARD HOLD** until genuine native build/export verification and independent qualified human claim/source checks plus founder authorization. No CMS write, public publishing, navigation, social post, email, merchant/affiliate change, tracking deployment, merge, or spending.
