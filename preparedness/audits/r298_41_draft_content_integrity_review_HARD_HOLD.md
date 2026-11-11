# R298 — Authentic build semantics + 41-draft custody and passage-preservation gate

**Date:** 2026-11-11 PT. **Issue:** #136. **Conversion coordination:** #820 / charter #818. **State:** DRAFT_HARD_HOLD, never approval. **No merge, WordPress or public changes.**

## Critical build reconciliation

Exact source `preparedness/tools/build.py` (base R297) shows `Library.__init__` registers **content/articles AND content/tools** into the *same* `lib.articles` collection (around lines 96–118); `main()` loops `for slug in lib.articles` and writes a WordPress draft and preview for each. Therefore **the intended 41 export entries are 35 article entries PLUS six tool entries in build-report.json**, not two unrelated build reports. An early local R298 prototype assumed the report had 35; this was corrected before completing the draft PR. The new gate demands 41 unique entries, 35 R200 article slugs and exactly six distinct actual tool slugs.

The new executable `preparedness/tools/r298_export_content_integrity_hold.py` validates R200 custody blob `5822f9dfde21d1f3bdfc26658769d852c639438c`; article numbering 1–35, canonical URL routes, immutable body Git OIDs/byte minima, the builder's release-evidence fields, WordPress HTML draft wrappers, explicit unapproved review language, 9-word narrative window continuity, and article introduction/conclusion anchors. For the six tool entries, a separate *review-only* custody receipt must provide slug, original tool body/meta Git blob IDs and generated draft SHA-256; actual bytes must match, and tools must remain draft.

The gate **only** reports DRAFT_HARD_HOLD for mechanically consistent synthetic inputs and INVALID_HARD_HOLD for missing/changed inputs. It cannot grant QD, factual/medical/privacy/rights approval, verified purchases or publication. Any source rewriting, source-ID alias substitution, extra duplicate canonical, missing tool, truncated narrative or missing review warning is an error.

## Executed verification (local, bounded)

- 84/84 new R298 adversarial synthetic tests PASS.
- 166/166 inherited exact-source R295/R296/R297 synthetic tests PASS.
- **250/250 combined local Python tests PASS**, exit 0. Python compilation PASS.
- Exact R298 committed and locally executed Git blobs: validator `d96d552655c5915f5dc6c1d92078e373208c3f7d`; tests `15e6b3dfb8725a818c230261cce5c354006b4e7a`.
- Negative control against incomplete local repository returns exit 1 / `INVALID_HARD_HOLD` / `R200_CUSTODY_BLOB_INVALID`.
- **No native authenticated full-repository validate.py/build.py execution**, no actual 41 export run, no original 41-body comparison, no browser/print/privacy examination. This is NOT an independent QD pass. Local GitHub DNS remains blocked; authenticated Github connector reads are available.

## Current upstream and safety custody

- Seven Claude contributor heads each compare **identical** (0 ahead, 0 behind, 0 changed paths) with authentic frozen R200 SHA, NOT older pre-R200 ancestors: start 2122d856; shelter 5daeaf2d; food f911ff7a; health d5ef5baf; historical field 4e5caf81; historical food 67e116e5; historical home 7504a5f0.
- Independent QD PR #157: DRAFT `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Food test PR #169: DRAFT `e9cd7766dac59d47ab467d8945269b9146c2aef5`; one remaining `test_register_fragments_cannot_duplicate_ids` uses `ROOT / "sources" / "fragments" / "_dup_test.json"`, so fixture isolation remains independent-QA HOLD.
- Homepage lead PR #1689: DRAFT `f55c36b6598eec558dd8bb24e4c8988becc51be0`; no changes made.
- Existing 21 historical lineage differences, 32 shared URL groups, 15 duplicate source-ID groups, disputed agency citations, Article #7 hazardous-water claims, and Article #15 / Tool #104 emergency-dispatch, child privacy, printing, accessibility and no-JS issues are **not cleared by this PR**.

## Conversion-first handoff — OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer / funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Existing FREE Preparedness Archive / official FEMA household-plan resource → family communication visitor | Original Tool #104 advice and disclosures are unreviewed | Preserve free official source; draft contextual CTA only; qualified independent editorial emergency/child privacy + print review | LIVE free archive; original tools HOLD | Preparedness QA |
| Optional authentic Tool #104 paper card → useful delivery | No-JS, filled-card print, minimum-disclosure and storage assertions unverified | Browser print/no-JS/accessibility/security QA; do not deploy | R296/R297 source-level claim witnesses, no browser PASS | Preparedness QA |
| Free guide → ONE paid suitable FV toolkit | No authenticated FV-owned/rights-cleared purchasable Preparedness pack or proven fit | Audit actual SKU rights, merchant checkout, fulfillment; do not recommend Legacy Triage until Vested Wisdom relationship proven | No qualified payable SKU verified | Founder / Commerce |
| Grok high-intent family contact content → archive | No validated already-published matching asset_id / landing URL | Cross-check existing TASK-008, preserve Grok production queue | NO VERIFIED MATCH | Grok / Praxxis |
| Qualified sessions → CTA → confirmed lead → paid fulfilled order → fees/refunds → net revenue | Sessions/orders/payment attribution unavailable | Consent-aware 7- and 30-day reconciliation; no extra script | Realized net revenue/1,000 qualified human sessions NOT COMPUTABLE | Claude Analytics / Commerce |

No paid CTA, new offer, retired water freebie, CMS/nav write, social posting, outbound email, analytics script, affiliate activation or spending.

## Next bounded acceptance

On authenticated complete checkout, execute `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`, then run R298 with an actual six-tool checksum receipt. Independently adjudicate any article-body OID differences against R200 history rather than silently overwriting them. Do **not** claim 41 verified without independently inspecting their content and safety states. Keep all releases under founder/independent QD control.
