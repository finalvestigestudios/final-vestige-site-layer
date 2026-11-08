# R204 — original Preparedness citation adjudication workorders (DRAFT / HARD HOLD)

**Governance:** Preparedness #136 only; revenue/attribution coordination #820 and charter #818. Isolated atop R203 PR #1494 at immutable parent SHA 088b8a2b61ca7a6be078322edbdb0d4f6f14091a. Zero changes to original article bodies, metadata, source registers, WordPress, homepage, navigation, CMS, analytics, email, affiliate, merchant, social or spending. No merge or publishing permission.

## Distinct engineering advance

R203 correctly fails on the FIRST absent source-use description, clears the citation ledger and returns INVALID_HARD_HOLD. R204 generates a complete deterministic, individually actionable human-review docket without auto-fixing records, so the two known gaps / three citation occurrences can be adjudicated together. The source body is pinned to its original Git blob and owner-branch commit; R202 custody and a pinned R203 parser are prerequisites. Unexpected missing citations, changed branch scopes, foreign-only sources, duplicate IDs, rewritten bodies, missing registers, changed human-review flags or unsupported approvals fail closed. Every valid workorder is UNREVIEWED_HARD_HOLD and successful structural execution remains DRAFT_HARD_HOLD / exit 2, never QD PASS or medical safety approval. Missing original repo returns INVALID_HARD_HOLD / exit 3.

## Authenticated source findings, November 7, 2026

- Article #7 homemade-water-filters, immutable body SHA 67aa44e9a332f57fb70298a3867410d8f66c8c15 and metadata SHA 33789d3db0ec06007deb50d0293361f07cea27ae: two body citations to cdc-find-clean-water, without matching article-level source-use explanation. Global CDC source register object b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77 points to https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html and has human_link_check=false. First claim concerns household alternative water such as heater tank/melted ice; second concerns creek fuel/chemical contamination. Official CDC source dated June 25, 2025 differentiates the tap water heater from heating-system water and permits melted ice only if made with uncontaminated water; reviewer must check whether original wording requires stronger qualifications. CDC says suspected chemical/fuel-contaminated water cannot be made safe by simple treatment. These observations DO NOT constitute medical or editorial signoff.
- Article #20 preparedness-real-households, immutable body SHA 70d03c366e10db623929f118501becfa26c48bab and metadata SHA a0c3a09143a825560b5a5ed79d857b7402bfa295: one body citation to start-ready-plan without matching article-level source-use explanation. Original Start fragment object 29574c328cbab0548e6e5d4a026694857d56b6b4 points to https://www.ready.gov/plan with human_link_check=false. Claim concerns spoken household languages; public Ready.gov direct fetch returned HTTP 403 this run. Source fit/human check NOT VERIFIED.
- Both bodies and both metadata identities matched their original Start contributor at commit 2122d856fce9f64887c16df3d52e64be9f59a55b. The two original source-record identities and three citation positions are real, not synthetic fixtures.

**Required human adjudication:** (1) Author/versioned claim-specific source-use explanations for both CDC citation positions; examine water heater and uncontaminated ice caveats plus water safety. (2) Independently inspect Ready.gov plan in an accessible authoritative source and document the exact language-support claim, review date and author. (3) Independently review water and other relevant public-safety advice; maintain original/revised evidence separately and rerun R203/R204. Do NOT silently amend original source records or mark linked records human-reviewed by inference.

## Code and executable evidence

Tool Git blob 68ef1635c0f5470af8a15cd84b434607ff4b7cb2 and regression suite Git blob b228b3c116edc76bead5bcca948d2753c3fb88a4 matched the locally executed exact code with git hash-object. **82/82 local synthetic Python unittest tests PASS**, including 70 frozen body and owner-branch mutation cases. Python compilation PASS. Missing original checkout CLI exit 3 / INVALID_HARD_HOLD tested. Authenticated original full-repository R202/R203/R204 native CLI, validate.py, build.py, full repository unittest discovery, inspection of all 41 WordPress exports, browser QA, human source review and independent safety/QD remain **NOT EXECUTED**; local GitHub DNS resolution still blocks trusted full checkout. Native commands after obtaining original checkout:

    python -I preparedness/tools/r204_citation_adjudication_workorders.py --repo . --report /tmp/fv-r204-workorders.json
    python -I preparedness/tools/r203_full_slate_citation_body_gate.py --repo . --report /tmp/fv-r203-gate.json
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

R203 is expected to fail on current original inputs and should NOT be bypassed.

## Coordination — exact current refs

Fresh GitHub original branch refs: Start 2122d856fce9f64887c16df3d52e64be9f59a55b; Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; Food f911ff7a655de8d81535ea86ec3d65a49ee76648; Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c; Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2. All 7/7 frozen heads unchanged. Independent QA PR #157 at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa corrects power-drill and refrigerated-medication guidance, but remains separate/unmerged. Synthetic fixture PR #169 at e9cd7766dac59d47ab467d8945269b9146c2aef5 and follow-up PR #973 at 4d40996a559b0124d74a9bb3bdcd481ad1992aa8 remain separate drafts. Their overlapping test_preparedness.py requires conflict-aware reconciliation. Homepage lead PR #1500 at 51b7b0591481d32424ddaa76c962d13bd61c795e left untouched.

## Conversion-first bounded plan: OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer / funnel step | Blocker | Draft-only change/acceptance | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Free household preparedness gateway → original Household Emergency Plan | Three citation positions unadjudicated, full QD and safety incomplete | Original-vs-amended diff, qualified source review, native build, then phone/keyboard checks; free guidance must remain ungated | FAIL / HOLD | Preparedness + independent QA |
| Grok household-records content → existing gateway | No authenticated matching published Preparedness asset_id, platform link or approved destination | Reconcile actual immutable asset IDs and platform click path in existing Drive TASK-008; do not seize Grok production | NOT VERIFIED | Grok + Praxxis |
| Guide → optional free Reunification Card | Original card unpublished, child/contact privacy and printing acceptance pending | Synthetic-only mobile, print and keyboard checks; no data transmission, hidden collection or forced opt-in | HARD HOLD | Site QA |
| Legacy Triage → paid practical pack | Rights, actual active Payhip listing, price, merchant checkout/delivery/refunds unverified | Commerce/founder authenticates product and completes authorized delivery and refund acceptance before showing any paid link | HARD HOLD | Founder / Commerce |
| Qualified human sessions → paid net revenue | No verified attributed orders, fees, refunds or cohort sessions | Existing measurements only: asset_id + utm_campaign to qualified visits to CTA, consented confirmed leads, merchant-confirmed orders, refunds/fees to realized net revenue; compare 7/30 day cohorts | NOT COMPUTABLE | Commerce / Analytics |

**Potential free-guide CTA text, NOT FOR RELEASE:** Read the free household emergency planning guide — official sources and practical steps, no signup required. No unapproved paid CTA is proposed. Existing Focus Fieldbook remains the sole site-wide opt-in magnet; no retired water freebie. The only currently public provisional destination is https://finalvestige.com/preparedness/ where original detailed guides remain unpublished. Verified net revenue per 1,000 qualified human sessions cannot be computed, and pageviews/clicks/affiliate outbounds are NOT purchases.

**FINAL: DRAFT / HARD HOLD. No source equivalences approved, especially the disputed jerky source aliases; no commercial or editorial release.**
