# R423 — Campaign privacy / merchant endpoint preflight · HARD HOLD

**Scope:** Preparedness Archive integration and source/citation safety gates only; Issue #136, conversion coordination #820, charter #818. **DRAFT / HARD HOLD / NOT WORDPRESS-PUBLISHED.** This is a developer review receipt, not approval of editorial advice, merchant rights, a campaign, or financial outcomes.

## Independent current source-branch identity (2026-11-16)
Nine head refs checked via GitHub same-ref compare (ahead/behind 0/0):
- `claude/prep-start-bbfeb8` `2122d856fce9f64887c16df3d52e64be9f59a55b`
- `claude/prep-food-ccdc55` `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- `claude/prep-health-837444` `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- `claude/prep-hist-field-9db767` `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- `claude/prep-hist-food-b81f19` `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- `claude/prep-hist-home-0e0e38` `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- `claude/prep-shelter-5e1e0e` `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- `claude/prep-shelter-continuation` `ac8625faf30dd5538fadc31e06cb5a2cea1defae`
- `claude/prep-shelter-followup-evidence` `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`

Independently checked draft PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, dependent fixture #2205 `bbcf1859768624c611df4abadc564c18247cf32a`, homepage #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`; these are separate, untouched. Parent R422 #2799 `631a76c77129db58e07d869453fea8d1dd28a720`.

Original Git-pinned R397 source/fork graph `86d22a1d504c93db7689b914e2202a7845b648e2` remains intact in parent; its inherited inventory is **35 articles, 203 distinct source IDs, 280 records, 17 exact duplicate-URL groups, five unresolved source disputes, nine unresolved forks**. The graph is not a certified source-to-claim assessment; no variant selected.

## Demonstrated synthetic R422 gap → R423 change
R422 accepted (a) arbitrary first-party-aligned personal `utm_campaign` strings, (b) a syntactically plausible YouTube video URL with a supplemental `email` query, and (c) a `REVIEW_CANDIDATE` with `seller=Final Vestige Studios` and an unrelated merchant checkout domain. Each passed R422 structural checking, **without** meaning the claims were true.

R423 rejects those cases with exact codes: `R423_UNBOUNDED_OR_PERSONALIZED_CAMPAIGN_ID`, `R423_SOCIAL_QUERY_PRIVACY_OR_CONTEXT_DRIFT`, `R423_MERCHANT_ENDPOINT_NOT_APPROVED_REVIEW_SHAPE`. It constrains tentative pilot names, publisher post query keys, mobile query keys, and **review-only** Payhip-style checkout paths/terms URLs (same host, no arbitrary redirect or query). This is a *conservative review policy* for this one candidate pilot, not an affirmation of Payhip seller ownership or a promise that any URL works. Other real merchants or future pilots need separate proof/approved scope amendment; do not infer a permanent merchant ban.

R423 synthetic 90/90 tests PASS, including parent-before/new-after reproductions, harmless URL controls, malformed evidence and privacy field mutations, merchant lookalikes, release locks and CLI fail-closed exit 2. Source/test blob identities are logged in Issue #136. Other R409–R422 module runs independently passed; combined total **1,108 local tests across 15 separate module processes** (NOT a single full-suite invocation). Python compilation PASS. The native full 35-article build and paired actual WordPress/private-preview exports were **NOT EXECUTED**; authentic files unavailable in this workspace. All safety/QD approvals remain outstanding. Hosted CI must be checked independently; local PASS is not hosted CI PASS.

## Original editorial safety and citation release holds
Do not infer that historical preservation processes are medically or food-safe; do not publish water treatment/food preparation/medical emergency steps pending qualified source applicability and safety adjudication. Do not collapse shared URL source IDs, invent missing cite contexts, remove warnings, or silently select nine manuscript forks. Article #15 and printable Tool #104 remain private/unapproved; Tool #102 separate. No WordPress-ready content emitted as public work.

## One intent-aligned conversion trial — OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
1. **Existing FV Preparedness paid toolkit** → merchant-confirmed purchase/delivery → FV seller rights, actual SKU, payable checkout, fulfillment and refunds unverified → independent founder/commerce verification of **one real** currently sold product, test on staging only after consent → **NO VERIFIED SKU/ORDER** → Founder/Commerce (HOLD). No invented SKU, no paid CTA.
2. **Existing family-contact/reunification social post** → verified human landing at **already-free** `https://finalvestige.com/preparedness/` → no independently authenticated existing Grok `asset_id`, post URL/hook/rights or platform-supported clickable mobile destination → Praxxis independently crosswalk one already-published on-topic asset in TASK-008 and retain immutable ID/permitted UTM → **UNMATCHED** → Praxxis/Grok (Grok production ownership unchanged).
3. **Free source-backed guide** → optional practical printable Tool #104 → emergency applicability, child privacy and accessible print not independently approved → separate qualified review and print/keyboard checks; **DO NOT EXPOSE TOOL** → **QD HARD HOLD** → Preparedness/QD.
4. **Qualified 7/30-day sessions** → CTA click → confirmed lead (if applicable) → independently confirmed paid order → fees/refunds → realized net revenue per 1,000 qualified humans → genuine first-party and merchant evidence missing → use Claude's existing measurement spec; do not add scripts; preserve consent → **KPI NOT COMPUTABLE** → Claude/Commerce.

**Unpublished draft free CTA:** “Start With Trusted Preparedness Resources” (to the existing free Archive only after authentic media-topic match). Check matching intent, no promises of safety, readable 320/360/390px mobile layout, working permitted mobile link, appropriate disclosures, keyboard access, clear tool-versus-free distinction, no premature checkout. Do not resurrect retired water freebies.

No public post, WordPress/CMS/nav/analytics writes, emails, merchant or affiliate activation, spend, merge, safety PASS or commercial verification. Grok creator/posts; Praxxis social QA; Claude site/analytics; founder release/commerce/spending.
