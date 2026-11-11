# R287 — Preparedness Inline Citation / Frozen Source Crosswalk (UNAPPROVED)

**2026-11-11 PT | Preparedness Issue #136 | Conversion #820 | Business charter #818**

**DRAFT / HARD HOLD.** This is a read-only, fail-closed engineering proposal. No merge, publication, navigation, CMS, merchant, analytics, email, social or spending changes. No independent QD, safety, privacy or commerce approval.

## New mechanical gate
R285/R286 authenticate all 41 metadata documents and 244 registered source records, but did not pair the exact 35 article HTML bodies and six tool HTML bodies with those metadata `source_use` lists. R287 adds a deterministic source lineage gate:

1. Load the exact Git-blob-pinned R286 bridge `1b3d4ca5056871ede00101eb5902dfdfa1b20867`; require it to return DRAFT_HARD_HOLD with all approval flags False. No path-based Python cache loading.
2. Read the frozen 96-row integration manifest; require 35 article body/meta pairs and six tool body/meta pairs, with each body and meta authenticated by its original Git blob SHA.
3. Enumerate literal `{{cite:source-id}}` body occurrences; reject malformed markers, inline IDs absent from paired metadata, IDs absent from the frozen registers, missing bodies, duplicate paths and role changes.
4. Produce a reviewer-only per-body evidence crosswalk: every source ID, occurrence count, authenticated origin/candidate URL and historical verification/human-check status. **Never choose a winner for duplicate source IDs or infer truth from ID existence.**
5. Preserve uncited bodies and metadata-only sources as review warnings, not automatic deletions or editorial approvals. All success states are still DRAFT_HARD_HOLD; errors are INVALID_HARD_HOLD.

## Verification scope
Local R287 prototype: **71/71 synthetic Python regression tests PASS**, compiled. Local R286 inherited 22 tests + R287 prototype: **93/93 PASS**. The inherited source file's Git blob matches the authentic committed R286 bridge SHA. The smaller, separately committed R287 regression file is **not yet executed in a complete authenticated checkout**; do not equate prototype test receipts with exact committed current-head CI.

Authentic connected-GitHub spot checks (read-only; **not all 41**): emergency hygiene 62 inline markers/7 unique IDs; family communication 69/20; historical fire-making 67/11; family reunification card 16/11; fire escape worksheet 11/7. All five samples had no inline source ID missing from their corresponding original metadata. A successful mechanical crosswalk would **not** certify any claim as medically safe or verify its source reading scope.

**Local checkout blocker:** `github.com` and `api.github.com` DNS resolution fail in the local container; full native Python `validate.py`, `build.py`, all-current-head tests and genuine 41 WordPress draft exports are NOT EXECUTED. Previous R286 CI failure cause remains unverified.

## Exact SHA coordination
Seven Claude cluster branches freshly compared against their correct frozen R200 SHA: **7/7 identical**, ahead 0 / behind 0.
- Start `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Historical field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- Historical food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical home `7504a5f099594d635e3dd7332a33a2e1346c43a2`

Independent QA PR #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` inspected, remains separate. Fixture PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` inspected; one secondary fixture still writes into live source fragment directory. Homepage lead PR #1689 last reported HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`; no homepage changes. R286 parent #2021 `a0b26804470b6db081a91d916bb6b117c8168d94`.

## Immutable holds
**21** historic three-way article lineage differences; **32** shared-URL groups; **15** duplicated source IDs; **three** disputed CDC/Ready.gov citations; Article #7 chemical-water hazard; Article #15/Tool #104 child privacy, print and accessibility; historic metadata `approved` labels for #6/#21 not independent QD/safety approval. No original manuscripts, URLs, source registers, citations or exporters changed.

## Conversion-first decision (OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER)
- Provisional **Legacy Triage** → potential purchase: not independently verified purchasable, rights-cleared, audience-relevant or deliverable → founder/commerce audit of real file, merchant acceptance/refunds and privacy. **NOT APPROVED / NOT TESTED**. Owner: Founder/Commerce.
- Existing free Preparedness Archive → optional practical resource: child-data privacy, safety, accessible print and source scope unresolved → independent human review and mobile/print tests. **HARD HOLD**. Owner: Preparedness QA.
- Grok social asset → free guide: no authenticated matching `asset_id`, destination/mobile proof or rights in existing TASK-008 → request read-only verification from Grok/Praxxis, never change their production queue. **NO VERIFIED MATCH**. Owner: Grok/Praxxis.
- Approved pack → checkout → paid order: no verified offer to test → authorized mobile checkout, disclosure, delivery/refund QA **after** founder approval. **NOT TESTED**. Owner: Commerce/Claude.
- Confirmed paid orders → realized net revenue / 1,000 qualified human sessions: orders, qualified-session attribution, fees and refunds unavailable → seven-/thirty-day settlement reconciliation. **NOT COMPUTABLE**, not zero. Owner: Analytics/Commerce.

Next: authenticated full repository checkout; current-head native build and all 41 offline WP draft exports; human adjudication of source scope/medical/privacy; verify one actually purchasable, relevant digital pack before any CTA. No public publishing without explicit release approval.
