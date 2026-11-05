# R143 — Exact PR #157 rebase-custody and conversion HOLD

Scope: **Preparedness Archive #136 only**. Coordinating issue **#820** and charter **#818**. R143 parent is R142 draft PR #1083 exact commit \`4662ecd45d7ad4ccf55e40fced76fb909f838542\`. This is a **read-only review gate**. No existing article, source register, citation, route, taxonomy, CMS, navigation, homepage, analytics, email, merchant, affiliate, social, or publishing artifact changed.

## Newly verified — do not wholesale apply old PR #157

Actual GitHub file bodies were independently read at frozen 35-article RC \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\` and independent QA PR #157 \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`; exact Git blob identities are pinned by the companion JSON and by Python constants.

| Article | Frozen RC | QA #157 | Replacement risk |
| --- | --- | --- | --- |
| \`household-emergency-plan\` | ~3,420 approximate whitespace words; **57 citations** | ~3,151 words; **57 citations** | ~269-word loss despite unchanged citation total. Both already state **do not turn off the main breaker**; RC specifically preserves refrigeration, alarms, sump pumps, security and critical equipment. The PR is **not an incremental necessary fix** to the current RC. |
| \`three-day-kit\` | ~3,761 approximate words; **79 citations** | ~2,848 words; **68 citations** | ~913-word and **11-citation** loss if replaced. The QA medicine caution merits qualified review, but wholesale substitution would remove 3 entire source identities: \`start-fema-power-sheet\` (5), \`start-fsis-emergency-food\` (1), \`start-cdc-power-outage\` (1); it also drops four other citation occurrences. |

**Key distinction:** The current RC already contains an outage-specific FEMA medicine quotation and two CDC prescription citations in an editorial instruction to consult a pharmacist about **interim-use and replacement**. QA #157 has different, more explicit "do not stop essential treatment or discard" advice. A qualified reviewer should consider the **one bounded passage-level editorial clarification** while preserving the richer RC's evidence, qualifiers, and citations. No automatic merge, unreviewed medical advice approval, or source equivalence is allowed.

The prior #157 patch also changes Red Cross source kind and taxonomy formatting, but this R143 gate intentionally audits just the two article-body risks. Those other changes require their own existing QA/source-custody lanes.

## Engineering and invocation

- New \`preparedness/tools/r143_qa157_regression_gate.py\`: exact article **and metadata Git object** integrity preflight. Compares all literal source IDs and occurrence counts, validates the two R143 high-consequence context anchors, freezes author-specific \`source_use\` binding, and emits a deterministic reviewer docket.
- New 2-row manifest: \`preparedness/docs/r143/qa157_frozen_pair_manifest.json\`. It identifies **both** original article paths and current RC metadata; all approval fields remain unreviewed.
- New isolated Python tests: \`preparedness/tests/test_r143_qa157_regression_gate.py\`. 65 actual unittest cases, including 48 independent tampering mutants and false approval/draft/source absence checks.
- Given independently checked-out trees, use:

\`\`\`bash
python -I -m unittest discover -s preparedness/tests -p 'test_r143*.py'
python -I preparedness/tools/r143_qa157_regression_gate.py \
 --manifest preparedness/docs/r143/qa157_frozen_pair_manifest.json \
 --rc-root /read-only/exact-rc-checkout \
 --qa-root /read-only/exact-qa157-checkout \
 --report /local/private/r143_qa157_review.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests
\`\`\`

The audit exits **2** with explicit HOLD when an expected source tree or SHA-pinned file is absent; even a successful exact-pair check **does not issue QD/safety/release approval**. Local 65 tests are synthetic; native execution against the authenticated 35-article tree, complete build, browser review and independent QD remain **NOT TESTED** if the checkout is unavailable. R143 does not alter or erase earlier R133–R142 custody facts.

## Coordination and release constraints

- All seven Claude contributor branch refs rechecked Nov 5 against R140 pins: Start \`2122d856fce9f64887c16df3d52e64be9f59a55b\`; Shelter \`5daeaf2dd5ab71806a6b73c91edfb1d8df5da976\`; Food \`f911ff7a655de8d81535ea86ec3d65a49ee76648\`; Health \`d5ef5bafd68361434dd1cc9209915b8e8a4eaf17\`; Hist Food \`67e116e536c7410bed30f8f3b1bb8c166f3c223d\`; Hist Home \`7504a5f099594d635e3dd7332a33a2e1346c43a2\`; Hist Field \`4e5caf812727953aa45e3bda2d382f2c67b6a09c\`. All **IDENTICAL** (0 ahead/0 behind). Historical Food jerky-ID scope and 32 source groups remain human review HOLD; no automatic source normalization.
- Fixture isolation PR #169 \`e9cd7766dac59d47ab467d8945269b9146c2aef5\` leaves one test writing into shared sources. Stacked PR #973 \`4d40996a559b0124d74a9bb3bdcd481ad1992aa8\` repairs that remaining fixture in a temporary copy; neither changed here.
- Homepage PR #49 \`10495883299d53596992c26a8987f629b2904670\` and draft #604 \`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176\` remain independent. Claude owns production engineering. No public publish or QD PASS.

## Conversion-first Preparedness acceptance check (ONE audience; NO invented SKU)

**Proposed audience:** parents/caregivers planning out-of-area contacts, school pickup, and family reunification, subject to validation in Grok/Praxxis TASK-008. The already authentic, source-backed **draft** \`household-emergency-plan\` is the proposed free guide. The existing **draft** \`family-reunification-card\` is a separate optional practical printable (its metadata still shows safety \`pending\`, publish \`draft\`; verify mobile, privacy and print). Neither is announced or released by this proposal. Keep all essential safety instructions free with no email/paywall gate.

**Proposed on-site copy for editorial review ONLY:** “Make a family contact plan. Read the free evidence-linked guide first. Optional: create a wallet-size reunification card you can print and keep privately.” This is not a deployed CTA or a guarantee of safety.

**Paid upsell:** **NONE AUTHENTICATED** for this Preparedness buyer. Do not display a purchase button or claim that a new toolkit is sellable without real rights clearance, exact owned product SKU, actual merchant URL/price, a successful staged checkout/delivery/refund audit and founder approval. Do not resurrect the retired water freebie or make emergency knowledge conditional on buying.

**Required acceptance gates:** actual creator \`asset_id\` + published post URL + allowed link placement + canonical approved guide URL + working 360/390/768/1440px keyboard/mobile page; accessibility; privacy of printed contacts (never capture PII in URLs or analytics); native signup only if explicitly opted in and independently confirmed; merchant-reported paid order and fees/refunds if a suitable product is verified. Count unique qualified human landing sessions, article-to-printable CTA taps, confirmed leads, paid orders and revenue as **different events**. No duplication of tracking scripts. For 7- and 30-day cohorts, \`net_revenue_per_1000_qualified_sessions = 1000 * (merchant_paid_gross - fees - refunds) / qualified_human_sessions\` only when both numerator and denominator exist; otherwise **NOT COMPUTABLE**, with small samples called out.

**Offer → step → blocker → proposed owner action → evidence:** (1) owned Preparedness pack → purchase → no independently validated purchasable matching SKU → Growth/Claude verify listing, rights, merchant delivery and refunds → HOLD; (2) free household guide → human reader → qualified safety/source/QD pending → Preparedness QA review & native validation → DRAFT; (3) published Grok post → guide → no authenticated Preparedness asset ID or approved landing URL in TASK-008 → Grok/Praxxis reconcile without changing content queue → UNKNOWN; (4) guide → optional wallet card → mobile/privacy/print checks missing → Site QA test staged page → NOT TESTED; (5) order → net revenue → no reconciled qualified sessions or paid order evidence → Commerce reconcile 7/30-day cohorts → NOT COMPUTABLE.

**Release stays DRAFT/HOLD; this document is not authorization to publish, sell, email, track, or make medical/fire-safety assurances.**
