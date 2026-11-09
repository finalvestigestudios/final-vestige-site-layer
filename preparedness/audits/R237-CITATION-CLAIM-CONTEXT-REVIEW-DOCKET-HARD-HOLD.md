# Preparedness R237 — citation-by-citation claim-context review HOLD (2026-11-09 PT)

**Issues:** #136 (integration/source safety), #820 (conversion), charter #818. **DRAFT_HARD_HOLD / unmerged / not published.** This is an independent, deterministic *review docket*, not source validation, medical advice certification, QD PASS, WordPress deployment, or proof of attributable sales.

## Problem and bounded change
R235 reconciled 244 raw source records and 32 shared source-scope groups. R236 verified that all 35 manuscripts contain original author-authored source-use notes for every cited source ID, while three original occurrences remain editorially UNREVIEWED. Neither operation independently creates a review item for **each occurrence and adjacent claim context**. Editors must not treat a source-level note as a claim-level verification. R237 generates one stable ordinal, source ID, original offset, bounded human-reading context excerpt, excerpt SHA-256, author-note SHA-256, and nonbinding *review-priority term hits* for every original citation. The receipt is bound to the 35 frozen article slugs and draft metadata; three original citation HOLD occurrences remain frozen.

A separate fail-closed input check rejects source citations placed in nonreader HTML comments, template/script/style/noscript/textarea payloads, or tag attributes, and malformed tokens. Context drift changes a deterministic article and aggregate SHA-256 receipt. Risk-term matches are **triage only**, not proof of danger or safety.

## Authentic current-source reconnaissance
All 35 authentic body manuscripts were read via the linked GitHub connector at the R236 frozen branch. Each body had the same count of raw `{{cite:` tokens and recognized citation syntax; the preflight found no citations placed inside HTML tag attributes and no missing prose prelude within 300 characters. The actual source-use parity census is **2,000 citation occurrences in 35 manuscripts**. The two distinct UNREVIEWED source groups still cover three original citation occurrences: article #7 `cdc-find-clean-water` twice, and article #20 `start-ready-plan` once. This does NOT adjudicate source support or medical/environmental safety. R237's Python code was **NOT** run against the full authentic checkout; its per-occurrence receipt hashes for real content remain unexecuted.

Original contributor branches observed unchanged via same-ref GitHub compare:
- start `2122d856fce9f64887c16df3d52e64be9f59a55b`
- shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- food `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`

Independent QA PR #157 draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and synthetic fixture PR #169 draft HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` inspected; neither merged or altered. Current homepage lead #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0` is out of lane and untouched.

## Verification
- Exact R237 module Git blob: `30379a441948ed264871a4b2280a154b5a5167e0`.
- Exact R237 synthetic tests Git blob: `86d625dbc267042de652204b13ed404c5909d9ca`.
- **112/112 isolated Python unittest regressions PASS**, and Python compilation PASS, from locally executed files whose Git blobs match the committed module/test files. Coverage: 35 concealed template placements, 35 attribute placements, 35 claim-context fingerprint mutations, plus seven baseline/negative controls.
- R220 source validator now binds R237 module to the exact Git blob and expects 35 articles, 2,000 cited occurrences, three original HELD citations, all release/QD/safety flags false. The complete native checkout and inherited suites are unavailable due to local GitHub DNS resolution. **Full `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and `python -I -m unittest discover -s preparedness/tests -v` NOT EXECUTED.** No real WordPress-ready output or 82-file claim of QA PASS.
- Existing R220–R236 citation, browser, tokenizer, publisher, route, source, hub and full-export integrity guards preserved, not bypassed.

## Mandatory editorial and engineering blockers
1. On a trusted complete checkout, execute original validate/build/full suite; run `python -I preparedness/tools/r220_full_slate_draft_custody.py --root preparedness --originals-only` and verify the new receipt; check full 35-article/6-tool preview and WP exports with the legacy 82+ landing/hub files. Recheck exact Git heads before run.
2. Independently adjudicate all **32 shared-source scope groups**, the two original unreviewed claim-source groups/three occurrences, and qualified water/medical/food/device caution language. Author notes and R237 risk-priority terms are not verification.
3. Independent reviewer to compare individual R237 claim snippets with full primary official pages at proper reading depth; require reviewer signature, date, context fingerprint and explicit citations before any source status can change. No automatic approvals.
4. Preserve the 35 original manuscripts' reading depth, six tools, canonical URLs, original citation records, safety labels and seven contributor branches; retain DRAFT_HARD_HOLD.

## Conversion-only coordination — no new offer activated
**Audience/topic hypothesis:** family emergency contact and essential-document planning; existing public free official-resource Preparedness index `https://finalvestige.com/preparedness/`. An actual published Grok video asset ID, platform URL, rights, UTM, mobile landing and campaign linkage are NOT independently verified. The sole existing provisional optional commercial candidate remains Legacy Triage, publicly advertised at $19 but currently **not cleared** for this funnel: seller authorization, full PDF, audience fit, privacy/security, disclosures, checkout, fulfillment, refunds and independently confirmed orders all need verification. It is primarily an estate/incapacity product; do not pretend it is an evacuation toolkit. No new product, retired water freebie, campaign link, paid CTA, email, social post or merchant action.

Proposed *draft only* CTA: “Make a plan your household can find when it matters. Start with our free emergency planning references.” Optional secondary card only after founder/commercial validation: “Organize essential records — learn what Legacy Triage includes” with an accurate scope statement and clear `Paid digital download` label. Never gate essential safety directions behind purchase.

**Offer → funnel → blocker → acceptance → evidence → owner:**
1. Existing free official-resource index → Grok asset landing → actual `asset_id`/destination missing → verify TASK-008 published asset, mobile URL and permitted attribution → UNVERIFIED → Grok/Praxxis.
2. Free index → original long-form draft guides → native tests + human source/safety approval absent → execute exact native validation, claim dockets and qualified review → HARD_HOLD → Preparedness + QA.
3. Free official guide → optional Legacy Triage → fit/rights/privacy unclear → complete PDF and merchant rights/fit audit → NOT APPROVED → Founder/Commerce.
4. Optional paid offer → purchase → checkout, delivery/refunds untested → authorized end-to-end order/fulfillment verification → NOT TESTED → Commerce.
5. Confirmed purchases → realized net revenue per 1,000 qualified human sessions → no reconciled orders, fees, refunds or trustworthy 7/30-day source attribution → verify merchant exports and consented analytics → NOT COMPUTABLE → Analytics/Commerce.

**No changes outside `preparedness/`, no CMS/public/analytics/creator queue/navigation/merchant/email/spend writes.** See #136 and #820.
