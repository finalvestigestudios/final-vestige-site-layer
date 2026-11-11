# R301 — Preparedness body custody and independent reader-fidelity gate
Date: 2026-11-11 (PT). Owners: Preparedness Integration, Issue #136. Commercial dependency: #820 / #818.
**DRAFT / HARD HOLD / NO PUBLICATION / NO QD PASS.**

## Grounded Git provenance
Base: R300 PR #2099 `a4654d61d6cae73cf6378279a705cdde2c938453`.
Frozen R200 custody blob: `5822f9dfde21d1f3bdfc26658769d852c639438c`.
Pinned previous gate R300 blob: `ae83f747491ee1665d0bf5fb5272a8dd2a4d492e`.
Exact R300 Git tree contained 35 article .body.html and 35 .meta.json files; R301 pins **all 35 currently integrated article body Git blobs**. 21 match authentic frozen R200; 14 are explicit integrated overrides, **not adjudicated or declared safe**.
The 14 divergent bodies: household-emergency-plan; three-day-kit; outage-heat-cold-generators; home-fire-escape-plan; shelter-or-evacuate; family-communication-plan; go-bags; preparedness-real-households; pioneer-travel-rations; pemmican-and-dried-meats; root-cellars-cool-storage; navigation-before-gps; sanitation-before-germ-theory; pioneer-supply-chains-failed.

## New independent gate and limits
1. Reject any missing, symlinked, extra, or byte-changed article body; pin each full original HTML body with exact Git-blob hashing.
2. Parse source raw HTML independently of native builder and extract ordered text nodes and citation token occurrences; compare to the exported `pa-body#pa-main` reader text, citation occurrence order, anchor numbers, and visible marker labels. Detect paragraph/phrase deletion or insertion even if native build and report consistently omit it. Never equate this with browser CSS visibility or qualified accuracy.
3. Preserve all 14 source lineage differences as unresolved. Re-use the pinned R300 source+metadata+CSS+41-export checks; fail closed on missing upstream evidence. A mechanically valid artifact returns `DRAFT_HARD_HOLD`, never an approval.
4. No source manuscripts, metadata, source registers, taxonomy, CSS, exporter, navigation, WordPress, CMS, social publishing, merchant, tracking or email functionality modified.

## Executed local evidence
99 new adversarial Python tests PASS, including 35 deliberately dropped-text cases and 35 deliberate original-body mutations; 473 total inherited R295–R300 plus R301 offline tests PASS; Python compilation PASS. Git blob identities of committed implementation and tests must match these exact locally executed copies. This is **synthetic mechanical testing**, not full source/WordPress QA.
Incomplete checkout: `INVALID_HARD_HOLD` with nonzero exit as intended. Full authenticated checkout and native build/41-real-export comparison **NOT RUN**, because local `git ls-remote` cannot resolve github.com (DNS). GitHub connector metadata/tree reads DO work; they are not a substitute for executing the full local build.
Earlier R300 14 body and 12 metadata lineage differences remain unadjudicated. The seven Claude cluster branches compare `identical` to the correct frozen R200 commits, with zero ahead/behind and zero file differences.
PR #157 remains draft, #169 remains draft and includes another actual-source-directory temporary fixture mutation in test_register_fragments_cannot_duplicate_ids; independent QA owns that repair. Homepage lead #1689 is unchanged, draft.

## Safety and commerce dependencies
Article #7 hazardous-water guidance; Article #15/Tool #104 emergency-call language, privacy, no-JS, print and accessibility; 32 shared-source groups, 15 source-ID duplicates and source conflicts require independent scope-specific qualified review. Nothing here asserts medical safety.
**Single audience:** households preparing emergency family contact and reunification plans. **Free destination:** existing official-resource page /preparedness/; candidate Tool #104 remains under independent QA hold. One optional paid pack can be mapped only after Founder/Commerce verifies existing SKU ownership/licence, genuine availability, checkout, disclosure, downloadable delivery, refunds and audience fit. Legacy Triage remains unapproved: Vested Wisdom merchant identity not authenticated as FV ownership. No paid CTA.
Grok/Praxxis TASK-008 must supply a previously posted, relevant asset_id and valid mobile destination. No new Grok tasks or posting.
**Measurement contract:** unique qualified-human session by asset_id/UTM → valid landing → relevant CTA → consented confirmed lead if applicable → actual settled merchant-paid order (not checkout start or outbound click) → fees/refunds → net realized revenue. 7/30-day cohorts; tiny samples flagged. Net revenue per 1,000 qualified-human sessions: NOT COMPUTABLE (no verified numerator/denominator).

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
1. Free preparedness guide → trustworthy reading: potential dropped body and citations → R301 complete-body pin and independent main-body comparison → 473 synthetic PASS; 41 authentic unverified → Preparedness Integration / independent QA.
2. Free guide → practical Tool #104: dispatch/privacy/printing/no-JS issues → qualified review and mobile/browser tests → HARD HOLD → Preparedness QA.
3. Free guide → optional paid product: no verified rights-cleared audience-fit FV Preparedness SKU → verify seller rights, merchant order and fulfillment → NOT APPROVED → Founder/Commerce.
4. Published Grok social asset → guide: published family-contact asset and working mobile journey unverified → match existing TASK-008 ID and site link → NOT VERIFIED → Grok/Praxxis.
5. Confirmed paid transaction → realized net revenue: merchant settlement and attribution missing → 7/30-day reconciliation → NOT COMPUTABLE → Commerce/Claude analytics.

**Release decision: remain DRAFT / HARD HOLD.** Do not merge, publish, claim qualified source safety, attribute revenue, or invent a QD PASS.
