# R285 — metadata-to-source custody bridge (UNAPPROVED / HARD HOLD)

**Preparedness-only** · Issues #136 and #820 · Charter #818 · NO MERGE / NO PUBLIC RELEASE / NO CMS WRITE.

## Exact review base and change

Parent is **R284 draft PR #2014**, exact commit `9c13bc078f78fa79bb3cad60374c17466312a8fb`. This PR adds a separate read-only mechanical bridge; it **does not change** the original 35 article bodies, six tool bodies, 41 metadata files, 244 registered source records, eight source files, canonical routes, WordPress exporter, contributor branches, original source crosswalk or unresolved human review docket.

Existing R279's 96+1-file pinning checks file identities and draft status, and R284's R282 lineage gate checks 35 historical routes, contributor source identities and publication flags. Neither independently checks every **actual article/tool metadata `source_use` ID** against all eight pinned source registers while binding all 35 article metadata records to the frozen R200 number/section/track and distinguishing historical safety labels from independent QD.

R285 combines BOTH existing gates (exact Git blob-pinned source modules), requires **41** exact pinned metadata records and **244** authenticated source records in exactly eight frozen source inputs, crosschecks 35 article n/slug/section/track, preserves tool number reuse, rejects missing and blank `source_use` evidence explanations and absent source IDs, and returns duplicate source ID candidates for human review rather than silently picking a URL. A historical metadata `safety_review.state='approved'` is explicitly recorded as **not independent medical, privacy or QD approval**. All results are DRAFT_HARD_HOLD or INVALID_HARD_HOLD (exit 2/3), never a release pass.

Independent connected-repository read of the eight genuine frozen registers found **244 source rows, 225 distinct source IDs and 15 duplicated IDs**; no non-HTTPS URLs were found. **This authentic source-register check does not constitute execution of the new bridge on all 41 actual metadata files.** The full-tree source-use join is pending.

## Tests and scope

Locally executed: R285 **54/54 PASS**, Python compile PASS. Also ran R285 tests together with the **older R279–R283** local files from earlier signed review packages: **301 discovered / 299 PASS / 2 SKIP** (native checkout required). This mixed run does **not** include the newer R284 test additions or prove execution against R284 HEAD. The inherited prior R284 report was **286 discovered / 284 PASS / 2 SKIP**, separately reported in Issue #136, not rerun in this run. The R285 test file and implementation blob identities should be checked on GitHub before accepting these test receipts.

The authentic complete GitHub checkout is still unavailable locally because GitHub DNS resolution fails. Thus native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete current-head tests, the new R285 audit against all 41 real metadata files and 41 WordPress draft exports remain **NOT EXECUTED / NOT VERIFIED**.

## Independent ownership and safety

All seven Claude cluster branch references compared to the frozen R200 SHAs: **7/7 identical (ahead 0, behind 0)** in this inspection. Independent QA PRs **#157** (Start Here) and **#169** (food fixture isolation), plus home lead **#1689**, remain separate open drafts and were not modified. PR #169's second real source-directory fixture remains the independent QA concern.

The 21 historic article lineage reviews, 32 shared URL groups, 15 duplicated source IDs, three disputed citations, Article #7 chemical contamination advice and Article #15 / Tool #104 personal-info/printing/accessibility concerns remain on independent HUMAN REVIEW hold. Any metadata label suggesting approval does not override these restrictions.

## Conversion-first, no false income inference

**Audience:** households looking for family emergency-contact and reunification guidance. **Free:** existing live public `/preparedness/` (not the unreleased held contact card or retired water planner). **Optional commercial hypothesis:** Legacy Triage *existing PDF*, but suitability, rights, live paid listing, fulfillment, merchant confirmation and founder approval remain unverified. **No paid CTA authorized.**

| Offer → funnel step | Blocker | Required acceptance / experiment | Evidence status | Owner |
|---|---|---|---|---|
| Existing archive → free reader trust | metadata citations could lack a registered source / scope | R285 held citation-ID / metadata join plus independent source reading | 54 synthetic PASS; authentic all-metadata NOT RUN | Preparedness integration + QA |
| Free guide → optional practical tool | child privacy / print / accessibility pending | qualified independent safe-handling and physical-output review | HARD HOLD | Preparedness QA |
| Existing Grok video → free archive | actual posted asset ID / mobile target unverified | TASK-008 authentic rights / date / post URL / signed-out destination | NO VERIFIED MATCH | Grok / Praxxis |
| Free reader → Legacy Triage | rights / audience fit / order fulfillment / refund unknown | existing product/merchant acceptance and founder release decision | NOT APPROVED | Founder / Commerce |
| Paid orders → net revenue per 1,000 qualified-human sessions | no attributed settled orders, fees, refunds or qualified session denominator | consent-preserving 7/30-day reconciliation | NOT COMPUTABLE (not zero) | Claude / Commerce |

No merge, publishing, site navigation, CMS, analytics script, social post, TASK-008 queue edit, email, checkout, affiliate activation, product creation or paid service occurred.