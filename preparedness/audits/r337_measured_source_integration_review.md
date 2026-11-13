# R337 — measured source-depth and citation-token custody (Issue #136)

**Release state: DRAFT / HARD HOLD / NOT APPROVED.** This is a source identity and deterministic lexical inventory, not a source-support, Qualified Domain, emergency/medical, historical accuracy, accessibility, merchant, WordPress export or production signoff.

## Source provenance and measurement

- Exact integration baseline: `05fa47e24f5d7bb17ce40a3737242983706e57c7` (R336 draft HEAD).
- Prior frozen witness blob: `ff714125b0e785248819acc1358f912b470f4a69`; its `source_ref` is the prior R335 source snapshot, as recorded in that file.
- Read the original 41 Git body blobs by their frozen blob IDs, preserving all 35 article and six tool identities and draft statuses. No canonical source files were edited.
- New five-part lexical witness: 41/41 entries, 41 distinct previously proposed canonical routes, **117,431 ASCII-oriented word units**, **2,173 literal citation-token occurrences**, and **223 distinct cited source IDs**. These are lexical inventory measurements, not editorial word-count estimates or proofs of the citations' truth/relevance.
- For each entry record the exact body/meta blob pins, original route, source-byte minimum, word units, citation-ID frequencies, internal-link-ID frequencies and heading IDs. The tokenizer strips tags, literal citation/link tokens and encoded HTML entities, then counts ASCII-oriented words. This intentionally avoids an unreviewed interpretation of reading time, human comprehension or claim support.
- Independently fetched 41 metadata Git blobs and confirmed every observed citation ID exists in its entry's `source_use` declarations (41/41) and that all 41 publish states remain `draft`. **Source-use declaration is not external verification.**
- R337's read-only gate rejects missing parts, changed source blobs, word/depth drift, modified citation occurrences, heading/link drift, missing source-use membership, unsafe paths, altered route identities and false publish states. Even when syntax/identity checks pass it returns **DRAFT_HARD_HOLD**, never a green safety or release approval.

## Local execution and evidence boundary

- A disposable synthetic 41-entry suite: **98 new R337 tests PASS**, with 41 simulated body-depth removals, 41 citation removals and 16 other safety/integrity controls.
- Combined reconstructed archived R331–R336 suite with R337: **643/643 local Python unittest PASS**; Python compilation PASS. Exact committed R337 implementation and test blobs were independently fetched and matched byte-identical local Git hashes.
- **Not executed**: authentic complete checkout's `validate.py`, `build.py`, native 36+ tests, WordPress export parity for 50 WP + 50 private preview files, browser/no-JS/print QA, independent qualified QD review, production CI. Local GitHub DNS resolution still blocks a complete authenticated clone. GitHub-source reads and synthetic tests must not be labeled native-build PASS.
- Source-claim support is not automatically established from 2,173 citation markers. All 15 legacy source-adjudication conflicts, 14 differently defined raw Git-object divergences and 17 Article #15 / Tool #104 qualified claim reviews remain held. E327-05 phone-versus-missing-child numbering collision remains unresolved; E331 semantic editorial handoff is review-only.
- Independent QA PRs #157 and #169 are open drafts; PR #169 still has an unsafe canonical-source duplicate-test fixture addressed only by dependent unmerged draft #2205. Do not merge either by inference. Homepage lead #1689 remains outside this lane.
- All seven original Claude source heads and both Shelter descendant heads were compared to their frozen identities this run: 9/9 identical, ahead=behind=0.

## Commerce and creator acquisition, #820 / #818

**ONE audience hypothesis:** existing published Grok content about family contact/reunification, if and only if independently authenticated by Praxxis. **Only proposed free destination:** the already public official-agency source Archive `https://finalvestige.com/preparedness/`. Article #15 and optional Tool #104 remain held and must not be linked as available. Do not revive the retired water guide or present the Tool #102 plan builder as the Tool #104 wallet card.

| Offer → funnel step | Actual blocker → required safe experiment | Pass/fail evidence → owner |
|---|---|---|
| Existing FV-owned purchasable Preparedness digital pack → paid order | No authenticated approved rights-cleared, payable, delivered and refundable SKU. Validate existing merchant product identity, current checkout, fulfillment, receipts and refund terms before offering paid CTA. | HOLD, NOT VERIFIED → Founder / Commerce |
| Existing free Archive → held original family guide and optional print card | 17 unresolved claim/privacy/dispatch safety issues, five compiled source custody parts not native-export tested. Conduct independent qualified source and private-browser/print/no-JS review. | HOLD, NOT QD PASS → Preparedness / QD |
| Grok published asset `asset_id` → permitted free route | No independently verified family-contact published asset/URL/mobile matching. Have Praxxis check the existing TASK-008 inventory; do not create/post a new video or change Grok's queue. | NOT VERIFIED → Grok / Praxxis |
| Qualified human 7-/30-day cohort → CTA → confirmed lead (where applicable) → merchant-confirmed paid order → fees/refunds → realized net revenue / 1,000 sessions | Existing attribution and merchant settlement not reconciled. Preserve consent and separate outbound click, email intent, checkout start and verified purchase. | NOT COMPUTABLE → Claude / Commerce |

**No public release, navigation, CMS, mail, socials, analytics, affiliate/merchant activation, spending or homepage changes.** Founder retains release and spending decisions. This PR contains only additive Preparedness audits/tools/tests/review documentation.
