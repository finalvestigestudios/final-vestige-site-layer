# R303 — Inline semantic, ARIA and claim-context fidelity (Issue #136)

**2026-11-11 — DRAFT / HARD HOLD. No publication or QD PASS.**

## Scope and engineering rationale

The R302 reader-structure parser covers headings, blocks, lists, tables and citation-to-claim placement, but its semantic whitelist excludes `strong`, `em`, `span` and several other inline semantic elements. That permits a narrower standalone comparison to overlook erased warning emphasis or `role`, `lang`, `aria-label`, `hidden` and class changes while preserving flat text and the same structural-block events. The predecessor's exact-source/native exporter chain remains a separate control; this is NOT a demonstrated real-world release bypass.

R303 adds `preparedness/tools/r303_inline_semantic_aria_hold.py`, which **pins the R302 validator by exact Git blob SHA** (`2fa1a9d8818cceac546557ff303f7e9776de5ea7`) and the R200 custody (`5822f9dfde21d1f3bdfc26658769d852c639438c`) and requires the predecessor's full `DRAFT_HARD_HOLD` 35-article result. It compares authored inline tags, their complete attributes, order and textual/citation scope against WordPress draft `#pa-main` while preserving the R302 block/citation comparison. The tracked inline tags include `strong`, `em`, `span`, `abbr`, `time`, `mark`, `sup`, `sub`, `bdi`/`bdo` and others. Generated `sup.pa-cite` remains handled by R302 as an actual citation; generated link-token anchors are deliberately excluded from the inline matcher and remain subject to the prior byte-reproduction/source-link custody gates.

The validator rejects missing, symlinked, duplicate-slug or altered evidence; it never returns public-release authorization. It does not replace accessibility testing in rendered browsers, qualified safety review or human adjudication of source disagreements. No manuscript, metadata, URL, tool, taxonomy, source fragment, CMS or production code was edited.

## Run evidence

- Authentic seven contributor branches compared against the seven exact R200 custody SHAs on 2026-11-11: **7/7 identical**, zero ahead/behind, no changes. A live branch lookup was used rather than confusing an older pre-R200 snapshot with the canonical baseline.
- Independent QA PR #157 remains OPEN/DRAFT at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic-fixture PR #169 OPEN/DRAFT at `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Patch inspection shows #169 isolates the `_upgrade_test.json` fixture, but `_dup_test.json` still writes under `ROOT/sources/fragments`: keep that with independent QA, do not modify its branch. Homepage lead PR #1689 OPEN/DRAFT at `f55c36b6598eec558dd8bb24e4c8988becc51be0a0`, untouched.
- R303: **125/125** new local synthetic Python tests pass; inherited R295–R302 **582/582**, total **707/707**. `python -m compileall` passed. Mutation cases cover omitted emphasis, hidden labels, aria/role/lang changes, inline scope movement, malformed authored markup, source citation adjacency, symlinks and incomplete inventory. The incomplete-root negative control returns `INVALID_HARD_HOLD` with process exit code 1, as required.
- **Not executed:** authenticated complete native `validate.py`/`build.py` with all 35 article and six tool source files; 41 real WordPress draft outputs; browser/print/no-JS tests; qualified source/safety/QD review. Local direct `git ls-remote` still fails with `Could not resolve host: github.com`. Connector-accessed exact SHAs do not give the container a complete native checkout. The synthetic tests are not release approval.

## Existing editorial and safety holds

1. Original 35-body custody is pinned, but **14 integrated bodies** and **12 metadata records** differ from frozen R200; these are lineage questions, not automatically regressions or improvements.
2. Historical source identity (`hist-food-nchfp-jerky` versus `nchfp-jerky`) and outstanding agency/food preservation disagreements remain for qualified source adjudication; no automatic source renaming.
3. Article #7 hazardous-water guidance and Article #15 / Tool #104 emergency-dispatch scope, minor/child privacy, print and no-JavaScript promises require independent specialist review. Neither this validator nor R302 certifies medical/911 safety.
4. Nothing may publish, merge to production, update nav, write CMS, enable a paid CTA or report QD PASS under this draft. Founder approval and existing dedicated release ownership still apply.

## Conversion-first handoff — exactly one audience

**Audience:** households organizing emergency family contact/reunification. **Authentic free destination candidate:** existing `/preparedness/` official-source archive only; its unpublished original long-form guidance and Tool #104 remain gated. **Optional practical resource:** Tool #104 is a review-only, not-approved printable; an existing paper-only alternative is owned by its editorial lane. **Paid offer:** no FV-owned/licensed, genuinely purchasable, audience-fit Preparedness SKU/checkout/delivery has been verified; do not advertise Legacy Triage as FV or create a speculative product.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing free agency-resource archive → matched social visit | No verified already-published family-contact Grok `asset_id`, rights/allowed mobile destination | Read-only TASK-008 mapping of exact asset ID + permitted URL; test signed-out mobile path | Not verified; no new Grok task/post | Grok / Praxxis |
| Free archive → usable family-contact guide/tool | Article #15 / Tool #104 911 wording, child information, printing/no-JS and source-scope held | Qualified agency/safety/privacy/accessibility review; test no-JS and printed output without real child data | HARD HOLD, not safely promotable | Preparedness QA |
| Free guide → optional paid kit | No authenticated FV-owned or licensed SKU, relevant rights, checkout, delivery, refunds | Founder/Commerce product audit and sandbox checkout with permission; only draft disclosures until approval | NOT APPROVED; no purchase CTA | Founder / Commerce |
| Landing → relevant CTA → confirmed lead → merchant-confirmed order → net revenue | No authenticated asset attribution or transaction ledger; cannot infer sales from clicks | Read-only 7/30-day reconciliation of privacy-appropriate human sessions, confirmed orders, fees and refunds | NOT COMPUTABLE: realized net revenue per 1,000 qualified human sessions | Claude / Commerce |

**Draft-only CTA candidate:** “Make a plan for how your household can reconnect. Explore free, official preparedness resources.” This is not a paid CTA or a production change. Acceptance requires topic-to-landing match, mobile CTA visibility, accurate free/optional distinctions, original-source labels, link and accessibility tests, no misleading urgency or unverified claims. Cross-reference commercial Issue #820 and charter #818. Existing TASK-008 documents are research-only coordination, not delegated Grok content creation.
