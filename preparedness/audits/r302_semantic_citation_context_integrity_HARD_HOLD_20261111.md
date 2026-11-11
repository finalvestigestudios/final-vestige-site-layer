# R302 — Preparedness semantic structure and citation-to-claim placement gate
Date: 2026-11-11 PT. Scope: Issue #136 only. Cross-reference commercial #820 / charter #818.

**DRAFT / HARD HOLD / NO PUBLISHING / NO INDEPENDENT QD APPROVAL.** No modifications to the 35 article bodies, 35 article metadata files, six tool source bodies, source register, source crosswalk, stylesheet, production site, navigation, analytics, commerce, email or social accounts.

## Source of truth and exact custody
- Stack base: draft PR #2105 R301 HEAD `b2a5c59d12aee975d49074b8c03689d814065c9d` (not merged). R302 is a separate isolated draft branch.
- Frozen seven-cluster R200 custody manifest Git blob `5822f9dfde21d1f3bdfc26658769d852c639438c`.
- R301 executable predecessor blob `51253107b4e367cd13f679f6c70426fea9b8adb9`, imported only after pin check.
- Fresh exact seven comparisons against the **actual** frozen R200 SHAs: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`. **All seven identical (ahead 0 / behind 0 / changed files 0)**. This does not adjudicate the 14 integrated body and 12 integrated metadata divergences from R200.
- Independent QA PR #157 is still draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Fixture PR #169 is still draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; its test `test_register_fragments_cannot_duplicate_ids` retains a write into the real `ROOT/sources/fragments/_dup_test.json` directory. The other upgraded fixture is isolated. This is independent QA ownership; R302 does not edit QA branches.
- Homepage lead PR #1689 remains draft at `f55c36b6598eec558dd8bb24e4c8988becc51be0` and was not changed.

## Why this gate exists
The R301 main-body comparison normalizes all text into one stream and checks citation **order**, not the block/claim to which each citation is attached. A semantically distinct HTML output (e.g., h2 changed to p, ordered list to unordered list, table header scope changed, or a citation moved between neighboring claims without changing its ordinal) may preserve that flat text and citation order. This is an independent mechanical gap; it is **not** an assertion that these mutations are present in the authentic manuscripts.

R302 parses authored HTML and the export `#pa-main` independently; retains ordered heading, list, paragraph, table, warning-class, ARIA, label and citation events; and rejects changed structural attributes, text within blocks and citation-to-block adjacency. It strips source citation/link and inline-JS tokens only according to the pinned builder's known forms. It requires all 35 article destinations and the **verified R301 DRAFT_HARD_HOLD** chain before returning DRAFT_HARD_HOLD. Symlink, missing source/export and malformed upstream states return INVALID_HARD_HOLD. It cannot authorize a release.

## Execution and limitations
- New R302 synthetic Python regression tests: **109/109 PASS**; 72 parametrized negative mutation cases are in-memory (zero writes into actual source directories).
- Inherited R295–R301 tests plus R302: **582/582 PASS** using archived local isolated synthetic evidence. Python compilation PASS.
- Exact new Git blobs: gate `2fa1a9d8818cceac546557ff303f7e9776de5ea7`; tests `072055d1d97500102bf2d0331833f804397dbc20` (both verified against locally executed bytes).
- Missing complete checkout negative control returns `INVALID_HARD_HOLD`, exit status 1, with all approval flags false.
- **NOT EXECUTED:** authentic native `validate.py`, `build.py`, real 41 WordPress exports, browser CSS/perception/privacy/accessibility testing, independent source/medical safety/QD review. Container `git ls-remote` fails resolving github.com. Connector can inspect GitHub but cannot replace complete local execution.
- R302 output semantics cannot prove browser visibility, source accuracy, claim truth, safe emergency instructions, full WCAG compliance, or paid revenue.

## Non-negotiable inherited content holds
Article #7 hazardous-water language; Article #15 / Tool #104 emergency-dispatch threshold, privacy of children's information, no-JS and print behavior; disputed shared source scopes, NCHFP/USDA mismatch, unresolved historical source links; 14 body / 12 metadata lineage differences. None are promoted to QD PASS.

## Conversion-first single audience and acceptance
Audience: households planning emergency communication and reunification. Existing free destination `https://finalvestige.com/preparedness/` links to official primary sources while original guidance is held. This is **not** an endorsement of Tool #104.

Draft reader CTA, **not published**: “Build your household communication plan with official emergency-planning resources.” Secondary optional tool CTA cannot activate until Tool #104's emergency text, privacy, print and accessibility have independently passed.

No authenticated published Grok family-contact `asset_id`, exact mobile campaign landing, qualified session count, rights-cleared and genuinely purchasable audience-fit Preparedness SKU, verified checkout or fulfilled purchase exists in this evidence. Legacy Triage remains **not approved** for Preparedness; another seller's listing does not confer FV licensing. No retired water freebie, speculative paid SKU, email gate, urgency or new tracking script. The existing Seven Day Focus Fieldbook remains a separate, accurately described free subscription offer.

### OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
1. Free agency-resource archive → credible guide: structural/citation displacement blind spot → independent R302 gate → 582 local synthetic PASS; full authentic build NOT EXECUTED → Preparedness Integration / Independent QA.
2. Free guide → optional printable family contact tool: emergency guidance and child-data privacy / print / no-JS holds → qualified device QA and source adjudication → HARD HOLD → Preparedness QA.
3. Free guide → **one approved owned paid practical pack**: ownership, product rights, audience fit, true merchant availability, checkout/delivery, refund/fee disclosure unverified → authenticate an existing SKU and perform staged purchase/fulfillment checks with founder approval, no live order without consent → NOT APPROVED → Founder / Commerce.
4. Grok social video → archive: matching existing posted asset id and mobile destination not verified in TASK-008 → map only published asset and valid source-identified campaign URL → NO VERIFIED MATCH → Grok / Praxxis.
5. Relevant sessions → CTA → confirmed opt-in if applicable → confirmed settled paid sale → net realized revenue: session attribution and actual orders/refunds/fees missing → reconcile consentful 7/30-day cohorts; never substitute clicks/checkout starts for orders → NOT COMPUTABLE → Claude Analytics / Commerce.

KPI net realized revenue per 1,000 qualified human sessions is **not computable** without verified numerator and denominator, and cannot be stated as zero or a sale. No audience acquisition/commerce posting, WordPress edits, new scripts, merchant activity, or spending authorized.

**Release: DRAFT / HARD HOLD. Founder and independent qualified review retain all release decisions.**
