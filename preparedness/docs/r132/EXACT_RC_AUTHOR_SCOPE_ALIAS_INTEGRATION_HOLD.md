# R132 — Exact-release-candidate URL-alias / author-scope reconciliation (DRAFT / HOLD)

**Date:** 2026-11-04 Pacific. **Lane:** Preparedness Archive #136; cross-reference measurement #820 and business charter #818. **Candidate:** #584, immutable input `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. This is an **isolated review branch rooted on that exact candidate**, not on the older 224-row review stack.

## Finding and bounded correction

The R131 review found that the 32 shared-URL source worklist failed to include the Historical Food contributor for the NCHFP jerky page. The two URL spellings differ by a terminal slash. Group-count-only checks missed the omitted contributor, and simply appending the variant without changing the draft builder/validator would continue to lose the warning or report a false mismatch.

R132 changes one *crosswalk* and its source-integrity gates. No original article bodies, citation tokens, author metadata, source registers, route slugs, taxonomy, safety states, or WordPress content was changed.

- `preparedness/sources/crosswalk.json`: preserves exactly **244 original source records**, **202 literal URL spellings**, **201 conservative alias keys**, and **32** shared exact/alias groups. The previously incomplete NCHFP jerky group now lists the **three** independent source identities: base `nchfp-jerky` row 20, Food `nchfp-jerky` row 3, Historical Food `hist-food-nchfp-jerky` row 14 (terminal slash). The Historical Food `supports`/reading-scope `notes` remain distinct. Every group stays `pending-human-source-and-reading-scope-review` with null reviewer/date.
- `preparedness/tools/build.py`: adds an author/origin/source-ID/**literal URL** lookup for the draft source block. Each contributor receives a visible **independent review pending** warning even when its URL has a terminal slash. Preserves original citation links; does not rewrite or normalize a reader's source URL. Explicitly checks only same source-ID records in an existing duplicate-ID declaration.
- `preparedness/tools/validate.py`: compares the actual contributor source records to the 32 groups by a *review-only* terminal-slash alias. Maintains the **literal-URL** census and full original claims, and checks pending source review before publication using actual contributing author identity.
- `preparedness/tools/r124_source_crosswalk_integrity.py`: standalone exact register/crosswalk custody validation with conservative alias coverage; no human approval can be synthesized.
- `preparedness/tests/test_r124_source_crosswalk_integrity.py`: adversarial isolated synthetic test suite including per-group source-use tampering, forged approvals, missing member/alias, modified provenance and URL safety.
- `preparedness/tests/test_r132_alias_scope_build_regression.py`: **14 added** article-, source-, and draft-builder-level tests covering author-specific NCHFP URLs, retained eight original hist-food citation identities, all 35 draft articles, warnings, same-URL/different-reading interpretations, and protected release HOLD.

### Reproducible evidence / limits

Directly fetched all eight **actual RC** source-register blobs and the revised crosswalk on this isolated branch through the connected GitHub API. An independent in-tool JavaScript comparison passed **144 structural assertions**, checking all 244 original rows, all 32 full source variant bodies and contributor identities, literal vs alias counts, review-state restrictions and the corrected jerky triad. This is **not** a Python unit test, source-safety review, or independent QD pass.

**84 Python test cases are defined** in the two R132-included test modules (38 static + 32 generated per-group + 14 new), but they were **NOT EXECUTED** in this runtime. The trusted full checkout is not mounted: native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v`, WordPress draft rendering/browser QA and GitHub Actions CI are **NOT VERIFIED**. Run them only on an isolated full checkout with the exact RC and relevant branches fetched. Do not mislabel defined tests as passing tests. GitHub Actions has a previously observed pre-step dispatch blocker, but this branch has no proven exact-head CI outcome.

Historical R131 test pins the **older R124** evidence object and correctly continues to report its *historical* missing contributor. That does not mean the R132 proposed revision is applied to the older historical blob. Preserve both custody records.

### Repro commands, without publishing

```sh
git fetch origin integration/preparedness-release-candidate-20261101 integration/preparedness-r132-exact-rc-crosswalk-alias-hold-20261104
git switch --detach origin/integration/preparedness-r132-exact-rc-crosswalk-alias-hold-20261104
python -I preparedness/tools/r124_source_crosswalk_integrity.py --root .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The build generates local WordPress-ready draft markup only. Do **not** upload, publish, merge, deploy or treat this work as QD acceptance. Before review, check the candidate/branch exact SHA against the current GitHub references.

### Seven contributor heads checked in GitHub

| Contributor | Observed exact SHA | RC drift |
|---|---|---|
| Start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | unchanged from freeze |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | unchanged |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | diverged; do NOT autoconflate |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | newer documentation |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | newer S-7 citation retarget HOLD |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | newer edits require 3-way review |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | newer edits require 3-way review |

Independent safety QA PR #157 draft head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` was inspected: electrical drill and refrigerated medicine advice differs; qualified independent adjudication remains required. Fixture PR #169 draft head `e9cd7766dac59d47ab467d8945269b9146c2aef5` was inspected: remaining shared-folder temporary test write is still present; standalone fixture repair PR #973 has not been incorporated. Homepage #49 and flagship #604 have separate owners and were untouched.

### One high-intent, conversion-first **DRAFT** path

Social topic candidate: family emergency contact, school pickup and reunification planning. **Grok owns actual assets and posting**; Praxxis coordinates TASK-008. The reviewed Google Docs task/handoff contain no authenticated Preparedness-specific asset ID, dated published social permalink, actual allowed link, or confirmed matching campaign. Do not invent one or change the social queue.

**Free destination**: existing *Household Emergency Plan* article, presently DRAFT/HOLD for qualified safety/citation adjudication. Draft CTA (NOT LIVE): **“Make a household plan you can actually practice. Read the source-backed guide free—no signup required.”** Optional free existing family-reunification printable is also DRAFT and awaits safety, accessible-print QA; do not gate essential safety content. Do not resurrect retired water freebies.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| ONE existing purchasable paid Preparedness SKU → paid order | No authenticated FV-owned/rights-cleared SKU, price, approved checkout, refund terms or delivered file | Verify seller listing/rights and test permitted nonpurchase purchase-path flow **before** writing any paid CTA | **HOLD / NOT VERIFIED** | Growth/Claude; founder approval |
| Household free guide → human reader | Human shared-source scope and safety #157 adjudication outstanding | Qualified source+medical/food/electrical review, no email/paywall, 360/390/768/1440px and print checks | **DRAFT / NOT RELEASED** | Preparedness/independent QA |
| Real Grok household asset → correct guide | TASK-008 has no real matched Preparedness asset ID / landing destination | Grok/Praxxis supply actual ID, URL/date/rights, legal link path; Claude validate staging destination and permitted UTMs | **UNVERIFIED** | Grok/Praxxis/Claude |
| Guide → optional download and paid pack | Existing free printable unreviewed; no accepted paid SKU | Source and accessibility check on free card; **defer** paid, clearly labeled optional CTA until SKU and fulfillment verified | **DRAFT ONLY / NO PAID CTA** | Preparedness/Site QA/Growth |
| Qualified human session → CTA → verified lead (if any) → merchant-paid order → net revenue | No merchant reconciliation or qualified-session denominator | Only existing privacy-safe analytics; deduplicate orders, verify fees/refunds, 7/30d cohorts, tiny-N warning | **N/A, NOT ZERO** | Growth/Claude |

**Net realized revenue per 1,000 qualified sessions: NOT COMPUTABLE.** Neither link clicks, affiliate outbounds, signup events nor impressions are paid orders. No new scripts, vendors, paywalls, emails, social content, checkout, CMS writes, releases, merges or spending. All source review remains pending and **independent_QD_PASS=false**.

**Decision: HOLD; qualified source and emergency-guidance review and native full-checkout/CI/WordPress draft QA still required.**
