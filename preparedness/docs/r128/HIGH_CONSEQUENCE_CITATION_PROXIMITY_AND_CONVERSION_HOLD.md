# R128 — High-consequence citation proximity triage | DRAFT / HOLD

**Scope:** only Preparedness Archive Issue #136. Cross-references: creator-to-revenue #820 and business charter #818. No protected article, metadata, source register, source crosswalk, taxonomy, URL, tool output, WordPress, navigation, homepage, analytics, merchant or social production changes. No merges, releases, email, spend, or new paid offers.

## Why this exists

R120–R127 established 35 frozen article identities, 2,000 candidate citation-token occurrences, an author-specific explanation register, 32 pending shared-URL groups, and a four-item independent QA #157/RC #584 safety-language disagreement docket. Those structural inventories do **not** identify which **specific nearby visible passages** merit qualified safety and source scrutiny.

R128 adds a separate reviewer-queue generator: `preparedness/tools/r128_hazard_citation_triage.py`. It parses visible HTML text (excluding script, style, template, noscript, hidden/inert/aria-hidden elements and inline display:none/visibility:hidden), spots five indicative high-consequence **keyword** classes, and associates paragraph/list/table/heading-level source IDs. Every matching block is marked `OPEN_HUMAN_SOURCE_AND_SAFETY_REVIEW`. Absence of a citation *within the same block* is flagged for inspection, **not a finding of falsehood, unsafety, or missing evidence elsewhere in the article**. Likewise, a locally present citation does not mean the source supports the claim.

## Deterministic controls

- Requires exactly 35 unique taxonomy slugs under `/preparedness/`, with four Start Here taxonomy safety gates intact.
- Requires every candidate article's publication metadata to remain `draft`; never converts two historical `approved` states into independent QD clearance.
- Detects visible/hidden citation divergence, malformed tokens, unterminated `{{cite:` markers, empty author-scoped source-use explanations, orphan citation IDs, missing article files, and citation-total drift against the **historical RC #584 2,000 occurrence inventory**.
- Emits read-only JSON with article-level Git blob identities and human review snippets. No evidence/source rewrite, automatic source-ID retarget, or publication state change.
- With `--verify-ref`, requires the dedicated candidate checkout HEAD to be EXACTLY `ddb3528ba6494dada1fa1c3a142ce746e3a67706` and that tracked article/taxonomy paths have no uncommitted changes. The flag is mandatory for release-adjacent evidence; omit it only for synthetic tests.
- Returns `HOLD_HUMAN_REVIEW`, `may_publish=false`, `independent_QD_PASS=false`, `medical_safety_verified=false` and `checkout_verified=false` even if every structural check passes.

This is **triage only**, intentionally not a model of hazard completeness, claim truth, or scientific/safety adequacy. It does not implement human URL checking, article-depth comparison, the existing R124 shared-source crosswalk gate, or R127 QA wording adjudication. Run those independent gates as well.

## Exact-source spot checks — 2026-11-04

Using connected GitHub reads of **frozen** RC #584, an independent quick HTML `<p>/<li>` keyword scan (not execution of the Python tool against a full checkout) found:

| Candidate article | Body Git blob | Meta Git blob | Raw citation tokens | Keyword blocks | Blocks lacking same-block citation |
|---|---|---|---:|---:|---:|
| household-emergency-plan | `f81cd43516e8295104230412f18776919148f905` | `0681d51e6e29166eaae27ac2b7f1fbde3f836787` | 57 | 7 | 5 |
| three-day-kit | `933f38ff3cd55a241cf9b392014fc52d4961e84f` | `1c69d5f1636a3a41631a5d93f11254d85cbe1b59` | 79 | 15 | 7 |
| medication-and-devices | `47bbfeefb5aca5f5a8d66ad8c66e2998e6caae5e` | `a49a6d42a3deb14acbe67e7cf636c23cdc5ec49c` | 68 | 32 | 10 |
| outage-heat-cold-generators | `2cd3e30b3a7e3dfdb3fd30cfd2b832355f58dfe2` | `be37b602d0b82593d438083dfc8a1e5ef595dd44` | 121 | 27 | 5 |

The quick scan uses a broader, different keyword pattern than the new Python gate and can include headings, contextual sentences and disclaimers. The numerical columns **must not** be substituted for a full audit or be called unsourced advice. These four priority articles are already `publish:draft`, not live. None of these observations establishes a medical or emergency-safety clearance.

## Python testing and unverified requirements

Locally: `python -I -m unittest discover -s preparedness/tests -p 'test_r128*.py' -q` **76 tests passed**, including distinct negative tests for concealed citations, malformed/truncated citations, unverified/missing metadata, bad slugs/taxonomy gates, and dirty checkout detection. Python compilation succeeded. Source/test Git blobs were compared with their committed GitHub identities after upload.

**Not executed:** `python -I preparedness/tools/r128_hazard_citation_triage.py --candidate-root /exact/RC584 --verify-ref`; `python -I preparedness/tools/validate.py`; `python -I preparedness/tools/build.py`; the complete existing Preparedness regression suite; hosted CI; WordPress draft browser validation; qualified medical/food/fire/CO review; independent QD. There is no trusted RC checkout available to the local test runner. Do not infer a failure or a pass for any of these.

## Current dependency boundaries

Seven Claude heads read on 2026-11-04: Start `2af10621b0f4b5837f9224bf7f7163cc21590293`; Shelter `6a5998ead97eca997e573ce8d3ceacf1c6aabad4`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; Hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; Hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`.

Independent QA #157 is draft `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture PR #169 remains draft `e9cd7766dac59d47ab467d8945269b9146c2aef5`; R125 fix #973 is a **separate draft**, not merged. Release candidate #584 remains `ddb3528ba6494dada1fa1c3a142ce746e3a67706`, unmerged. Homepage #49 `10495883299d53596992c26a8987f629b2904670` and flagship #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` untouched.

Issue #136 has a separate same-day site-lead note that the **non-instructional public Preparedness gateway** page 1868 was published, expressly without any of the 35 drafts. This session made no CMS or public-site changes; a separate browser fetch did not establish current page reachability. Never conflate that gateway with approved emergency guidance.

## Conversion-first, one-intent funnel — strictly nonproduction

**High-intent social hypothesis:** households who want a usable emergency-contact / school-pickup / family-reunification plan. Grok/Praxxis TASK-008 currently provides **no verified exact Preparedness asset_id, post permalink, publishing evidence, and allowed link path**; do not invent one. The authentic planned free asset is the complete Household Emergency Plan (`household-emergency-plan`) in the **unpublished** slate; keep safety instructions ungated and do not advertise it until qualified review and release authorization. Do not replace the active /focus/ Fieldbook or resurrect the retired water guide.

**One paid offer decision:** **NO ELIGIBLE PREPAREDNESS PAID SKU AUTHENTICATED.** A suitable owned digital printable plan pack may be considered *only if an already-current product* is verified from seller-origin Payhip records with price, licensing/rights, exact downloadable bytes, customer instructions, refund policy and real merchant checkout. Do not launch a new SKU, invent pricing or display a buy button. If no such product exists, leave the optional paid step disabled and prioritize the ungated public-service guide.

**Internal draft-only CTA, disabled:** “Read the free Household Emergency Plan.” Suppress it until the article is independently approved and has a verified live route. Conditional secondary copy for later review only: “Optional printable companion — review what is included.” Suppress unless a real product is approved and checkout tested. Never imply payment is required to receive safety information.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing owned Preparedness pack | Merchant sale → download | No verified current SKU/rights/checkout/fulfillment/refunds | Obtain seller-origin product ID, real price, working mobile checkout, rights and delivery evidence; no live link meanwhile | **HOLD / UNVERIFIED** | Growth + merchant / Claude + Site QA |
| Free household guide | Social landing → readable guidance | 35 held article drafts, 32 source groups pending and high-consequence advice unreviewed | Human source/safety review and real accessible mobile/print staging test | **HOLD / NOT PUBLISHED** | Preparedness + QD |
| Grok asset | Permitted platform link → destination | No actual Preparedness media ID, posting proof or allowed click path | Reconcile TASK-008 real `asset_id`, `utm_content`, caption/profile-link eligibility and actual destination with Grok/Praxxis | **NOT VERIFIED** | Grok/Praxxis (creative only) + Claude |
| Optional paid CTA | Guide → checkout → paid order | No approved relevant product or tested merchant acceptance | Keep disabled; when authorized verify full accessible funnel and disclosures | **NOT TESTED** | Growth/Claude/Site QA |
| Realized net revenue | Qualified session → merchant paid conversion | No human-session denominator or settled order/refund/fee records | 7/30-day attribution; reconcile merchant paid orders and net proceeds; do not count taps/signup as sales | **N/A — NOT COMPUTABLE** | Growth/Claude |

No paid service, duplicate analytics script, email, posted video or affiliate activation is authorized.

## Next reviewer actions

1. Execute the new gate on **clean exact RC #584 checkout** with `--verify-ref`, export its JSON privately, and prioritize human review of the returned risk passages **alongside** source-adjudication worklists.
2. Independently adjudicate electrical drill and refrigerated medication wording differences in QA #157 versus RC #584, and all 32 shared-source reading-scope groups before approved integration.
3. Run the established native validator, build, 36+ existing tests, mandatory CI integrity and browser checks; keep QD and release **HOLD** until real evidence is recorded.
