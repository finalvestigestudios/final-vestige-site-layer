# R415 — original citation-context replay defense (Issue #136)

**2026-11-16 · REVIEW ONLY · DRAFT / HARD HOLD.** This review is additive to R414 and does not select an article or Shelter fork, mutate the seven original Claude branches, edit source registers/WordPress, or authorize any publication.

## Reproduced structural false positive
R414 checked nine original words to either side of an inline citation, but did not bind that pair to a globally consistent original manuscript position. In a disposable 35-article fixture, remove the exact citation anchor from its original location, append a copy of its original preceding and following passages to the same draft and put the unchanged citation in that new copy. The source ID, URL, label, citation total, original SHA, warning/heading text, and both paired exports all remain consistent. **R414 integrity = true; R415 integrity = false.** This is a synthetic source-binding problem, not a medical recommendation or claim that any published FV article has this manipulation.

## Engineering
- Adds a deterministic bounded original-to-rendered word alignment (12,000-token input ceiling; conservative fail-closed on ambiguity), for **both** WordPress-ready and private-preview outputs independently.
- Source-bound citations require nearby original words to map to the same monotone span in the rendered draft. Replaying the correct 18-word context elsewhere no longer repairs source-position integrity.
- Counts repeated exact source-adjacent witnesses to surface ambiguous copy/paste evidence; preserves multiple original candidate Git pins without selecting any.
- Uses only read-only source/manuscript/export inputs, carries forward R409–R414 safety restrictions, and returns `DRAFT_HARD_HOLD` with CLI exit code 2 even for structural success. No private manuscript excerpts in receipts.
- Conservative limitation: heavily restructured valid editorial prose can trigger review; a structural PASS cannot establish what a citation actually supports, source applicability, qualified food/emergency/child-privacy safety or independent QD.

## Exact offline execution
- New R415 synthetic: **64/64 PASS**; whole assembled R409–R415 suite: **486/486 PASS** (R409–R414 inherited 422).
- `python -m compileall -q preparedness/tools preparedness/tests` **PASS**.
- `python -m unittest discover -s preparedness/tests -p 'test_r4*.py' -q` **PASS**, 486 cases in 19.879 seconds.
- Committed R415 source Git blob `276847c902d65363ca7e8e68883766aa79eb4d3e`, test Git blob `7dba6a6c01cabf5566351e152047527db42eea24`; both matched the **exact local files executed**. Existing artifacts in the local test assembly derive from R412–R414 previous packages.
- The genuine 35-article repository checkout, real original private manuscript bytes, real 35 pairs of WordPress/preview exports, native validate/build, mobile/accessibility/browser regression, and qualified human citations/safety/QD **NOT TESTED**. Local `git ls-remote` failed with `Could not resolve host: github.com`. Local synthetic success must never be described as native full-build or hosted CI PASS.

## Explicit preservation ledger
R397 original escrow blob `86d22a1d504c93db7689b914e2202a7845b648e2`: 35 original articles, 77 original paths, 203 source IDs, 280 source occurrences, 17 shared-exact-URL groups, 5 unadjudicated source-scope conflicts, 9 unselected Shelter forks. All nine original contributor refs re-compared against their recorded SHA pins: **identical (0 ahead/0 behind)**.

Independent QD PR #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and fixture PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` inspected without editing. PR #169 still has a second canonical-source-directory temporary fixture; dependent #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a` remains a separate draft. Home lead #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0` unchanged. Do not merge or alter their ownership.

## Conversion-first acceptance / source-of-truth #820 and charter #818

| OFFER | FUNNEL STEP | BLOCKER | PROPOSED CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| **One existing FV-owned, rights-cleared Preparedness paid pack — NOT VERIFIED** | Optional checkout/paid order after free guide | Payable SKU, ownership, rights, fulfillment, terms, refund/fees unknown | Founder/Commerce independently authenticate one actual SKU, test buyer receipt + delivery; only then draft an intent-matched paid CTA | HOLD; no verified merchant order; never create speculative offer | Founder / Commerce |
| Existing free official-source `/preparedness/` archive | Published, on-topic social asset → landing → relevant resource CTA | No independently matched already-published family-contact/reunification Grok `asset_id`, hook, rights, UTM or working 360/390px route | Praxxis independently verify exactly one existing asset; no new task/post. Draft-only CTA: **Start With Trusted Preparedness Resources** | UNVERIFIED; CTA not published | Grok / Praxxis |
| Optional downloadable Tool #104 (NOT PUBLIC) | Guide → practical optional tool | Emergency and child-privacy claims, printing and accessibility unresolved | Source, privacy, QD and accessible-print review first; keep core emergency steps ungated | HARD HOLD; no promise of safety | Preparedness / QD |
| Authentic qualified sessions → confirmed leads → merchant paid orders → net revenue | Measurement and 7/30-day cohorts | No verified merchant confirmation/refunds/fees, qualified-human denominator or genuine asset attribution | Claude evaluate native first-party events and consent, no duplicate scripts; score net revenue per 1,000 qualified sessions only from observed numbers | NOT COMPUTABLE; clicks/checkouts/leads are not paid orders | Claude / Commerce |

**Release invariant:** no public CMS/navigation, publication, social post, creator queue edit, affiliate/merchant activation, email, analytics script, spending or QD PASS. Historical evidence is not modern safe-practice approval. Cross-reference #136 and #820.