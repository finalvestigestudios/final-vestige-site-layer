# R286 — Preparedness Inherited-Validator Execution Custody (UNAPPROVED)

**2026-11-11 PT · Issue #136 · Revenue/measurement coordination #820 · Charter #818**

**DRAFT / HARD HOLD. No release permission.** This branch is derived strictly from R285 PR #2017 HEAD \`9ff1ba6378e7d63a3b7d45b7ba0eb24031c01830\`. Only one existing Preparedness validator, one new isolated synthetic regression test and this audit are changed. Original 35 article bodies, 35 article metadata, six tools, source registers, URLs, historical review docket, WordPress exporter, CMS, monetization and social assets remain unchanged.

## Finding and correction

Independent Praxxis review of R285 identified a bounded time-of-check/use and cache-identity gap: \`pinned_bytes(...)\` verifies SHA of the Python source, but the old \`importlib.util.spec_from_file_location(...).loader.exec_module(...)\` executes by **pathname**, potentially using a timestamp/size-valid \`__pycache__\` file rather than compiling those authenticated bytes. No actual malicious cache or bypass was observed.

R286 **binds gate execution to its already SHA-verified bytes**. \`load_pinned_gate()\` performs one authenticated file read, \`compile(raw, filename, "exec", dont_inherit=True)\`, and \`exec(code, dedicated_module.__dict__)\`. It never invokes a path loader or consumes a local \`.pyc\`. Both inherited R279 and R282 validators still must independently return \`DRAFT_HARD_HOLD\` and both explicit publication/QD flags \`False\` before the 41 metadata/244 source crosswalk is evaluated. Syntax errors and absent audit functions are rejected; no approval is inferred.

## Executed verification, precise scope

- **R285+R286 exact source + test pair:** 76/76 PASS; Python isolated compilation PASS; source Git blob \`1b3d4ca5056871ede00101eb5902dfdfa1b20867\`; new R286 test blob \`7882763554db57163a97f0c4e147cd86bd5e9d2f\`. All tests used the committed file bytes, independently matched to local Git-blob hashes.
- **Bounded historical mixed suite:** 323 discovered, **321 PASS / 2 SKIP**. This assembles authenticated R279–R283 review-package scripts/tests with exact current R285/R286 source and tests. **It is NOT the complete current R284–R286 native repo suite**. The two older skipped tests require a complete checkout.
- New 22 R286 tests include: a reproducible synthetic timestamp-valid stale-bytecode scenario where the old loader returns a false LIVE marker; the repaired loader executes verified source and returns HOLD; a source mutation immediately after verification cannot create a second-read swap; missing/changed/symlinked gates fail; a complete 35-article/6-tool/41-metadata/244-source **synthetic composed audit** returns HOLD; release-flag, citation and syntax mutations invalidate the composed audit.
- **Authentic full-tree audits, \`python -I preparedness/tools/validate.py\`, \`python -I preparedness/tools/build.py\`, complete all-current-head tests and 41 WordPress draft exports: NOT EXECUTED.** The partial local packages do not include the native scripts or all genuine manuscripts, and \`github.com\` / \`api.github.com\` DNS resolution fails locally. The GitHub connector can read/commit targeted files but is not a native local checkout. CI/QD have not been certified.

## Fresh upstream coordination

Correct R200 frozen contributor SHAs, checked against exact current branches via GitHub compare (each \`identical\`, ahead 0 / behind 0):
\`start=2122d856fce9f64887c16df3d52e64be9f59a55b\`;
\`shelter=5daeaf2dd5ab71806a6b73c91edfb1d8df5da976\`;
\`food=f911ff7a655de8d81535ea86ec3d65a49ee76648\`;
\`health=d5ef5bafd68361434dd1cc9209915b8e8a4eaf17\`;
\`hist-field=4e5caf812727953aa45e3bda2d382f2c67b6a09c\`;
\`hist-food=67e116e536c7410bed30f8f3b1bb8c166f3c223d\`;
\`hist-home=7504a5f099594d635e3dd7332a33a2e1346c43a2\`.

Independent QA PR #157 HEAD \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\` remains draft, separate/unadopted, medically consequential content edits remain qualified-review HOLD. Synthetic fixture PR #169 HEAD \`e9cd7766dac59d47ab467d8945269b9146c2aef5\` remains a separate draft; its *second* \`test_register_fragments_cannot_duplicate_ids\` still creates a real \`_dup_test.json\` under the repository fragment directory. Do not merge until QA isolates it. Home lead PR #1689 HEAD \`f55c36b6598eec558dd8bb24e4c8988becc51be0\`, unchanged separate draft. Upstream R285 PR #2017 HEAD \`9ff1ba6378e7d63a3b7d45b7ba0eb24031c01830\` unchanged.

## Open substantive holds, not bypassed

21 three-way historical article source differences; 32 shared-URL review groups; 15 duplicated source IDs; three disputed CDC/Ready.gov source occurrences; Article #7 chemical-contamination claims; Article #15 / Tool #104 child-information privacy, physical printing and accessibility; human safety/citation scope; all 41 genuine draft exports; independent QD; founder approval. Metadata \`approved\` labels for Articles #6 and #21 are **historical only**, never QD or clinical clearance. No medically safe claim is made.

## Revenue-first, evidence-honest candidate

**ONE audience:** household emergency contacts/reunification. **Free destination:** the already public, ungated \`https://finalvestige.com/preparedness/\`; unreleased contact cards and historical water planner cannot be used. **Paid candidate:** the existing Legacy Triage PDF only as a *provisional hypothesis*; no approved SKU, merchant listing, rights-cleared product file, audience fit, checkout/fulfillment/refund acceptance or founder authorization has been independently verified. **No paid CTA or invented product.** The Grok/Praxxis TASK-008 owner must independently identify an *already published* genuine asset_id, post URL, post date, rights and signed-out mobile destination. No matching asset is verified here.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:**
1. Public free archive → trust/source authority → authenticated inherited gate could execute stale bytecode → verified-bytes execution → 76/76 exact tests; full checkout NOT RUN → Preparedness integration.
2. Free archive → contact guide/tool → human privacy and source review incomplete → independent qualified review, printing/accessibility checks → HARD HOLD → Preparedness QA.
3. Grok asset → qualified human sessions → matching published asset unknown → source/rights/asset_id/destination reconciliation only → NO VERIFIED MATCH → Grok/Praxxis.
4. Free guide → Legacy Triage optional paid PDF → actual rights/price/fit/checkout/delivery/refund unknown → founder/commerce audit before staged CTA → NOT VERIFIED / NOT APPROVED → Founder/Commerce.
5. Merchant-confirmed orders → fees/refunds → realized net revenue per 1,000 qualified human sessions → transactions/campaign attribution unavailable → privacy-safe 7/30-day cohorts with tiny-sample warnings → NOT COMPUTABLE, not zero → Commerce/Analytics.

No merge, production publish, navigation or CMS edit, paid service, affiliate/merchant activation, email, social posting, retasking Grok, analytics script or spending. This is a technical draft and evidence custody correction only.
