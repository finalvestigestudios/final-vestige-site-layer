# R279 — Actual 96-file Preparedness tree parity gate (DRAFT / HARD HOLD)

**Scope:** #136 Preparedness integration and source/citation custody only. Commercial coordination #820 / charter #818. Based on R278 exact commit `9829bb9f2707a82a276a3d62bead8e25193d3735`. **NO MERGE, NO CMS/PUBLICATION/COMMERCE ACTIONS, NO INDEPENDENT QD PASS.**

## Why this change matters

R278 independently cross-checks four historical JSON ledgers. Those records may all remain internally consistent even when an actual checked-out manuscript, citation register, HTML resource, metadata record or export validator differs from its historical R275 bytes. R279 introduces a separate **current filesystem custody gate**:

- Authenticates the R276 96-file snapshot manifest by exact Git blob `b8c7c6df0dca62b04b01abc5671b7083ad9cb61e`, frozen at integrated commit `df96120007ceb33290764392a5900e356e04deac`.
- Checks the exact 35 article body/metadata pairs (70 files), six tool pairs (12 files), Start Here hub, eight source origins, consolidated source crosswalk, unresolved review docket, and R220/R272/R273 gate source files.
- Fails on missing/added body/metadata files, byte edits (even when text length is unchanged), duplicate normalized paths, nonregular/symlinked files, malformed/duplicate-key metadata, mismatched slugs, non-draft publish states, invalid role/path pairings, changed counts, altered source review holds or unapproved release flags. Also checks all 96 paths and Git blob hashes against disk bytes.
- Returns `DRAFT_HARD_HOLD` for **perfect mechanical parity** and `INVALID_HARD_HOLD` for any mismatch. Both are hold states. CLI exits nonzero intentionally. This is **not** an editor/medical/privacy/accessibility verdict.
- Standalone pre-export read-only review command: `python -I preparedness/tools/r279_live_slate_gate.py --root preparedness` (expected exit code 2 and hold report when all source bytes match). This is **not wired into the unchanged R220 exporter**; integration of a new enforcement point would modify an already pinned protected file and require deliberate baseline reauthorization.

## Executed verification (2026-11-10/11 UTC)

- **68/68 isolated synthetic Python regression tests PASS**, after correcting two test-case assumptions during development (well-formed but altered SHAs are rejected by file-tree verification, not manifest syntax alone; swapped role fixture must actually swap role).
- Python `compileall`: PASS. The locally executed implementation/test file byte identities match their GitHub branch blobs: implementation `3f07367951720a35c5cbc49fd2a25b05029f5f98`, tests `1d306a174110cba56e832ea1f2ab77f5076619b0`.
- Independent connected GitHub REST **exact blob+size comparison of ALL 96 frozen paths against the R278 repository tree: 96/96 matches, 0 mismatches**. This is remote Git tree-object verification, **not execution of full `audit(root)` on a checked-out tree**.
- All seven current Claude contributor branch refs inspected against the correct R200 freeze: **7/7 identical**. R276's five-new-drift claim was corrected in R277; do not assign unnecessary merges.
- Independent QA draft PR #157 and synthetic-fixture draft PR #169 inspected again. **#169 still directly writes/removes `sources/fragments/_dup_test.json` in the active checkout** inside `test_register_fragments_cannot_duplicate_ids`; preserve its owner and request tempdir isolation, never edit that branch here.
- Home lead draft PR #1689 inspected and left unchanged.

## NOT EXECUTED / hard blocks

Full authenticated checkout / native `python -I preparedness/tools/validate.py`, `build.py`, full inherited suite and all 41 intended WordPress draft exports: **NOT RUN** because local container cannot resolve github.com. The standalone R279 real-checkout audit is also **NOT EXECUTED**. GitHub REST tree parity does not substitute for Python invocation. No verified independent medical, citation, accessibility or QD approval.

Historical R200-to-integrated differences still require substantive human review: **17 articles (14 bodies, 12 metadata), six shorter in bytes**. All **32 shared URL groups, 15 duplicate ID groups and three disputed CDC/Ready.gov citation uses** remain unresolved. Article #7 chemical contamination and Article #15/Tool #104 children's data, print readability and accessibility require qualified review. No material was deleted or editorially rewritten in R279.

## Conversion-first acceptance (no new offer activation)

Single audience hypothesis: **households seeking family emergency communication and reunification guidance**. Existing public free archive is the only permissible draft campaign destination: `https://finalvestige.com/preparedness/`. Require Grok/Praxxis TASK-008 to substantiate *already published* platform asset ID, rights, publication date, native mobile destination and consent-aware URL attribution; until then: **NO VERIFIED MATCH**. Never route to held Article #15, held Tool #104 or retired water freebies.

**Legacy Triage** is the **only provisional existing paid-product candidate**, not yet verified purchasable, rights-cleared, suitable or approved for Preparedness. No product CTA/affiliate link/checkout is live or authorized by this work.

| Offer → step | Blocker | Change / experiment (draft only) | Evidence status | Owner |
| --- | --- | --- | --- | --- |
| Existing free archive → matched social landing | No authenticated Grok asset/link | Require source-linked TASK-008 asset ID and 360/390px signed-out mobile click path | NO VERIFIED MATCH | Grok/Praxxis |
| Free guide → optional practical resource | Household/child privacy, printing, medical/editorial review open | Keep resource withheld; independent safety/accessibility and physical print acceptance | HARD HOLD | Preparedness/independent QA |
| Free guide → Legacy Triage | Product rights/content relevance, real purchase/download status unverified | Audit full owned PDF and offer terms; seek founder permission for clearly labeled optional offer | NOT APPROVED | Founder/Commerce |
| Optional paid pack → completed order | Checkout, refund and fulfillment not demonstrated | Authorized merchant test including delivery, taxes/fees/refunds and privacy disclosures | NOT TESTED | Commerce |
| Qualified-human sessions → net revenue | Purchase/affiliate settlement and attribution absent | Use unique asset_id + UTM, verified leads, confirmed paid orders minus fees/refunds for 7/30 day cohorts | NOT COMPUTABLE | Analytics/Commerce |

Draft public-safe CTA for future independent review only: **“Start with free household emergency planning resources.”** No unapproved tools, products, scarcity or health claims. No actual CTA placed.

**Priority metric:** realized net revenue / 1,000 qualified human sessions; **NOT COMPUTABLE**, not zero. No session, click, lead or order has been claimed without evidence. Founder owns release/spend/merchant approvals; Grok owns creator production, Praxxis verification; Claude owns main website/analytics engineering.

## Review order

1. Execute the R279 current-tree gate and R278 historical-ledger gate on the **same authenticated checkout**; confirm both remain HOLD.
2. Run native validate/build/inherited tests and verify all 41 *draft-only* exports, without writes to WordPress.
3. Obtain independent reviewer adjudication for 17 changes/32+15 source groups/three disputed uses and Article #7/#15 child-health risks; never mark QD PASS by code alone.
4. Only then assess whether a legally purchasable Legacy Triage pack aligns with the verified free guide and independently verified creator campaign.
