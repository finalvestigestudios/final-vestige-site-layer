# R131 — Canonical source-URL alias coverage / Preparedness HOLD
**Date:** 2026-11-04 (Pacific)  
**Governance:** #136 (safety/source gate), #820 (conversion), #818 (business charter).  
**Snapshot:** candidate PR #584 `ddb3528ba6494dada1fa1c3a142ce746e3a67706`; R124 source crosswalk `6ca388edbed803e64663e8f0ecfa55bda0fe08c3`.  
**Decision:** DRAFT; do not merge, publish, alter CMS/navigation, approve QD or claim medical/food advice safe.

## Previously hidden coverage gap — actual immutable source rows

R124 correctly inventoried **244 source rows**, **202 exact URL spellings**, and **32 shared-exact-URL groups**. Yet one source relationship is absent from its jerky group because the same NCHFP URL appears with and without a terminal slash. The conservative alias comparison gives **201 canonical URL keys** and **32 shared canonical groups**, *still 32*. The unchanged group count can hide incomplete contributor representation.

| Contributor | Source ID | Source index | URL | R124 jerky group |
|---|---|---:|---|---|
| base | `nchfp-jerky` | 20 | `https://nchfp.uga.edu/how/dry/recipes/jerky` | represented |
| food | `nchfp-jerky` | 3 | `https://nchfp.uga.edu/how/dry/recipes/jerky` | represented |
| hist-food | `hist-food-nchfp-jerky` | 14 | `https://nchfp.uga.edu/how/dry/recipes/jerky/` | **NOT represented** |

The historical-food account describes a different source use and separate author interpretation. R130 independently established a newer historical-food branch wants to retarget eight article citation occurrences to `nchfp-jerky`, which also exists in Food. These are **two distinct problems**: (1) URL-alias crosswalk undercoverage, and (2) a potential source-ID/scope collision. Do NOT solve either by flattening distinct source rows.

## New read-only gate

- `preparedness/tools/r131_canonical_source_alias_gate.py` pins eight source Git blobs plus the frozen R124 crosswalk, validates exact Git object identities, reconstructs the 244-row evidence index, and computes exact vs deliberately conservative URL-alias groups.
- It rejects unsafe schemes, credentials, confusing encoded separators, nonstandard ports, fragments, duplicate source IDs within one fragment, duplicate crosswalk memberships, malformed JSON and false approval/reviewer states.
- It preserves **case-sensitive paths, query-string distinctions, and encoded data**. Terminal path slashes, HTTPS hostname case, and explicit port 443 are considered *review aliases only*, never evidence of identical claims.
- It outputs missing/unexpected `(origin,id,row_index)` members for each canonical group and always reports publication / merge / QD / safety / commercial authorization as **false**.
- Against the frozen R124 crosswalk the intended result is `HOLD_CANONICAL_CROSSWALK_GAP`, **exit 2**, specifically missing `hist-food / hist-food-nchfp-jerky / 14`. A future corrected worklist may pass structural coverage and still reports `HOLD_HUMAN_SOURCE_SCOPE_REVIEW`, not release approval.
- The validator does **not** rewrite any of the 35 article bodies, metadata, source fragments, or crosswalk.

## Tested evidence and limitations

The exact Python source and test blobs in this draft branch match the independently executed local files. **54/54 Python synthetic/adversarial tests PASS; compilation PASS.** Tests cover alias equivalence, distinct query and case paths, unsafe URLs, author ID preservation, missing crosswalk members, source-ID duplicates, false approvals, and review-state lock.

All eight frozen candidate source files and the R124 crosswalk were independently fetched via the connected GitHub API. The live crosswalk mismatch was compared directly against actual indexed rows, not inferred from citation counts. **Full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, repository-wide regression suite, 35-article generated draft/browser QA, and mandatory Actions integrity remain NOT VERIFIED** because this execution environment lacks the full trusted repository clone. Previous exact-head CI jobs failed before executing any step; no CI pass is asserted.

## Human adjudication workorder

1. Add `hist-food / hist-food-nchfp-jerky / 14` as a third **pending-human** identity in the existing NCHFP jerky group in a *separate review-only proposed crosswalk revision*; retain separate source row, supports, notes, citation IDs and author reading scope.
2. Resolve S-7 explicitly with a qualified source/food-safety reviewer; compare NCHFP vs USDA FSIS differences using current official guidance and review dates. Do not silently retarget eight citations or equate shared URLs with equivalent methodological claims.
3. Re-run R123/R124/R126/R130/R131 together against a trusted full clone; reconcile newer contributor heads separately from frozen RC. Do not record safety approval until qualified review.
4. Keep all 32 shared-source groups pending human examination; preserve 35 article routes and draft publication states. Allow independent QA #157 safety-language adjudication before any release.

## Seven-branch / independent QA checkpoints (2026-11-04)

- Start `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Food `f911ff7a655de8d81535ea86ec3d65a49ee76648` (diverged from frozen)
- Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Hist Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Hist Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- Hist Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`
- QA #157 open draft `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; its electrical-drill and refrigerated-medication wording still requires qualified adjudication.
- Fixture QA #169 open draft `e9cd7766dac59d47ab467d8945269b9146c2aef5`; residual shared-folder fixture has isolated draft repair #973 at `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`, not incorporated into #169.
- Release candidate #584 open draft; homepage #49 and flagship #604 inspected for ownership boundaries; not touched.

## Conversion-first Preparedness acceptance — OFFER → FUNNEL → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer / step | Blocker | Safe change / acceptance test | Evidence | Owner |
|---|---|---|---|---|
| One EXISTING paid Preparedness pack → merchant purchase | No authenticated rights-cleared purchasable SKU, price, delivered download or refund policy | Verify merchant listing, ownership, checkout in approved nonpurchase test, rights and fulfillment before any CTA | **NOT VERIFIED; NO PAID CTA** | Growth / Claude |
| Existing Household Emergency Plan free article → reader | Draft, source alias gap, unresolved safety review | Resolve 32 group reviews and #157 safety text; only then staged browser test with citations and accessible free reading | **HOLD** | Preparedness / independent QA |
| Grok Preparedness social asset → approved guide | TASK-008 has no verified Prep-specific asset ID or destination inventory yet | Grok/Praxxis provide genuine asset_id and platform URL; Claude checks landing continuity on stage | **UNOBSERVABLE / NOT TESTED** | Grok / Praxxis / Claude |
| Free guide → optional printable tool | Tools staged/draft; safety/format approval incomplete | Evaluate existing family-reunification card or household worksheet as **free** practical download; ensure no email/paywall on safety advice; mobile 360/390/768/1440, print, local-data handling and alt labels | **DRAFT ONLY** | Preparedness / Site QA |
| Optional owned paid pack → checkout → delivered download | No verified relevant product | *After* merchant evidence, propose narrowly matched optional CTA with proximate commerce labeling; check price/tax/terms/refunds and receipt/download on test orders, with founder authorization | **NOT TESTED** | Claude / Growth / Site QA |
| Qualified human asset sessions → merchant-confirmed paid orders → net revenue | Source-of-truth attribution not accessible | Reconcile asset_id/UTMs → landing → CTA → confirmed lead (if any) → merchant paid order → refund/fees; 7/30-day cohorts and tiny-N flags; never treat click as sale | **N/A** | Growth / Claude |

**Draft on-site free-guide CTA, disabled until qualified review:** "Build a household plan you can practice. Read the source-backed guide free—no signup required." **Draft printable CTA:** "Use the free family-reunification card to record contacts and meeting points; check local school and emergency requirements." Both are internal editorial examples, not validated or published products. **Paid CTA remains withheld**. This lane will not offer the retired water freebie, invent a product, claim commercial revenue, or take over Grok posting, Praxxis coordination, Claude production or founder release approval.

**HOLD until verified source and purchase evidence; no public deployment requested.**
