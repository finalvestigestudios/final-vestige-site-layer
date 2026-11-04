# R117 | Nine-head article and source-fragment Git-object reconciliation — PRIVATE HOLD

**2026-11-04 PT. Preparedness Issue #136; acquisition/revenue coordination #820; charter #818.**
**NOT MERGEABLE / NOT PUBLISHABLE / NO QD PASS / NO MEDICAL-SAFETY APPROVAL.**

## New, independently fetched integration evidence

Authenticated GitHub directory inventories were read against **nine specified branch heads**: the R116 frozen-integration head, the independent release candidate PR #584, and **all seven current Claude contributor branches**. The results are committed as immutable, review-only Git blob-OID catalogs:

- \`R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json\` — all article HTML and metadata blob identities, plus source-fragment catalog and README identity, for each branch and its exact commit SHA.
- \`R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json\` — reproducible delta workorders, never interpreted as factual/safety approval.
- \`r117_seven_cluster_object_parity_gate.py\` — pure crosswalk reconstruction, nine-head identity checks, original 35 paired article routes, author-source fragment identity, and fail-closed manual-adjudication queue checks.
- \`test_r117_seven_cluster_object_parity_gate.py\` — 75 synthetic/adversarial Python tests; 35 separately named missing-original-metadata mutations and 7 separately named stale-contributor-head mutations.

Snapshot heads at the time of the check:

| Source | GitHub head SHA |
|---|---|
| R116 provenance baseline / PR #919 | \`980659031b0bd5787a326d38698138c1e8cad82d\` |
| Integrated release candidate / PR #584 | \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\` |
| Claude food | \`f911ff7a655de8d81535ea86ec3d65a49ee76648\` |
| Claude health | \`d5ef5bafd68361434dd1cc9209915b8e8a4eaf17\` |
| Claude historical field | \`4e5caf812727953aa45e3bda2d382f2c67b6a09c\` |
| Claude historical food | \`67e116e536c7410bed30f8f3b1bb8c166f3c223d\` |
| Claude historical home | \`7504a5f099594d635e3dd7332a33a2e1346c43a2\` |
| Claude shelter | \`5daeaf2dd5ab71806a6b73c91edfb1d8df5da976\` |
| Claude Start Here | \`2122d856fce9f64887c16df3d52e64be9f59a55b\` |

**Actual object-level findings** (this narrow comparison is NOT the historical R107's 23-file change census):

- R116 and the release candidate each expose **35 paired article HTML + 35 metadata files** and identical filename slates. **24** file OIDs differ between the two 70-file directories. Changed Git blobs do not establish substantive editorial quality or reading-depth equivalence.
- All seven contributor branches have paired article-file inventories and source-fragment catalogs; each includes \`README.md\`.
- Comparing contributor Git object identities to R116 yields **24 divergent observations across 18 distinct paths**, including **three source-fragment observations**.
- Of those 24 observations, **five** match the release candidate's blob exactly, **13** find the release candidate retaining R116's frozen version, and **six** find a third, different candidate version. **Nineteen observations do not exactly match the release candidate.**
- One overlapping path, \`homemade-water-filters.meta.json\`, occurs on **all seven** contributor branches with the **same contributor blob OID**, while both R116 and the RC retain a different object. This is **one shared physical path repeated across seven head comparisons**, not seven independent editorial changes. **No version is deemed correct without reviewing the author metadata and source-use evidence.**
- The source-fragment deltas must be reviewed alongside changed article context; matching author source IDs or URLs alone do not prove citation support.

**Audit interpretation:** These counts are evidence of recorded object relationships at the named snapshot heads. They are not proof that all seven branches were semantically merged, that the candidate is complete, that 30 reused source URLs were human verified, or that any emergency advice is safe.

## How to reproduce / safely adjudicate

At a full, clean source checkout, run:

\`\`\`bash
python -I preparedness/tools/r117_seven_cluster_object_parity_gate.py --repo-root .
python -I -m unittest discover -s preparedness/tests -p 'test_r117_*.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

For **strict independent local Git proof**, first fetch the nine named branch refs and their objects into a trusted local clone, then run the gate with \`--require-local-git-heads\`. Missing/stale remote-tracking refs or missing exact file objects **fail closed**; there is no fallback to accepting a stale head. The normal read-only structural report sets \`snapshot_heads_verified_locally=false\` and release \`HOLD\` even on success. Reviewer must separately compare **meaning, source interpretation, reading depth, caveats, dates, safety status and citation placement** for each workorder before accepting a contributor or candidate version. No automatic source-ID retargeting or manuscript mass overwrite.

**Testing truth:** A local test layout of the R117 Python validator and tests ran **75/75 synthetic unittest cases** plus Python compilation. The actual nine-snapshot manifest and full repository build/validation were *not executable inside the scratch runtime* because no authenticated complete repository Git checkout is available. Hosted exact-head checks require a GitHub Actions runner; previous R116 workflows failed before their first step. Do not infer a production PASS from local synthetic tests.

## Independent QA / release coordination

- **Safety QA PR #157** at \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`: unmerged and pending qualified human review. The R116 and RC versions of the household-plan practice passage already contain explicit **"Do not switch off the main breaker"** language; newer byte identities differ from the historical #157 source. That overlap does **not** establish equivalence of all risk caveats or approval of #157. Avoid blindly cherry-picking its older article bodies.
- **Synthetic-fixture QA PR #169** at \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`: still unmerged. The patch isolates \`_upgrade_test.json\` but a separate \`test_register_fragments_cannot_duplicate_ids\` test still creates \`sources/fragments/_dup_test.json\` inside the shared tree. Fix in its own owner branch and test under parallel/concurrent execution; do not silently merge it here.
- **Homepage PR #49** \`10495883299d53596992c26a8987f629b2904670\`; **flagship PR #604** \`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176\`. Inspected but untouched. Claude retains core website/measurement ownership.

## Founder conversion-first handoff — one audience, NO unverified purchase link

**Verified product gate remains missing:** No seller-origin inventory confirms an existing, genuinely purchasable, FV-owned, rights-cleared Preparedness pack and its current pricing, file delivery and refund policy. An archived WordPress draft with a retired water Payhip link is **not** evidence of an active offer and MUST NOT be revived.

| Offer → funnel step | Blocker | Change / acceptance experiment (DRAFT only) | Evidence | Owner |
|---|---|---|---|---|
| Proposed household emergency-contact planning guide → reader | Guide and citations remain draft/pending safety | Preserve free unrestricted guidance; complete 30 URL-group review, contributor adjudication and qualified safety approval before a public destination | Snapshot OIDs verified as GitHub listings; NOT safety-passed | Preparedness + independent safety/QD |
| Existing owned Preparedness practical pack → checkout | No verified present SKU/rights/price/fulfillment | Require authentic merchant inventory, one suitable verified product, terms and working PDF delivery; otherwise **omit** paid CTA | NOT VERIFIED; no paid product link included | Claude/Growth; founder release |
| One Grok high-intent household planning asset → free guide | No actual immutable matching asset_id/post + permissible landing | Grok/Praxxis TASK-008 supplies asset ID, post URL, UTM and platform link placement; Claude/Site QA stage-checks path without posting | UNOBSERVABLE | Grok/Praxxis/Claude |
| Optional relevant paid pack → mobile checkout | Safety/merchant eligibility and path unverified | Once verified, inspect precise product, honest optional disclosure, price/refund terms, 360/390/768/1440 accessibility, checkout and file recovery without unauthorized payment | NOT TESTED | Claude/Site QA/founder |
| Qualified human sessions → realized net revenue | No merchant-confirmed paid order or joined session cohort | Existing consented attribution only, 7/30 day cohorts, fees/refunds deduction, tiny-sample warning; no duplicate script | Net revenue / 1,000 qualified-human sessions **N/A** | Claude/Growth |

**Draft on-site CTA text only, not a live link or product claim:** "Make a household plan you can actually practice. Read the complete, free guide when editorial and safety review are complete." A second optional pack CTA remains ABSENT until a merchant-verified appropriate product exists. The existing Focus Fieldbook remains the separate approved lead magnet; no retired water freebies, posting, email send, CMS write, analytics installation, merchant operation, or public release.

**Release gates remain**: 23 historically flagged contributor-file revisions; 30 shared-source URL groups; 15 safety exceptions; 22 editorial decisions; five unfinished tools; qualified human emergency-safety review; real browser, keyboard, print and mobile QA; native validation, build and all tests; mandatory integrity; independent QD; founder release. **HOLD.**
