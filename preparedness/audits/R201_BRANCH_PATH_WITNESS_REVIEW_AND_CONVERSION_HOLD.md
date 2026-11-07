# R201 — 35-article Git-branch path custody / no-release reviewer packet

**Status: DRAFT_HARD_HOLD.** Engineering custody evidence, **not** independent claim review, medical/food safety approval, QD, merchant verification or publication authorization. Source-of-truth issues: #136, #820 and #818. Applies only to the Preparedness Archive; no homepage, Grok task board, analytics, CMS or merchant modifications.

## New observation: two independently meaningful kinds of source proof

R200 preserved 35 body object IDs and 35 metadata object IDs. A bare Git blob ID proves content identity **if the bytes are available**, but does not, by itself, prove which branch and file path originally carried it. R201 adds path-provenance verification.

On 2026-11-07 the connected GitHub API was queried for the **exact Git refs and article Git Trees** of all seven Claude contributor branches. The original R200 JSON manifest was read at commit `11ed080e54845c1d933d6a221c28203f62583c60`, manifest blob `5822f9dfde21d1f3bdfc26658769d852c639438c`. The resulting read-only docket is `r201_branch_path_witness_observation_20261107.json`.

| Git tree custody observation | Exact count |
| --- | ---: |
| Frozen original article positions | 35 |
| Distinct authored canonical routes | 35 |
| Branch heads unchanged from R200 | 7 / 7 |
| Owner article+metadata pairs | 35 |
| Inherited identical article+metadata pairs | 36 |
| Total branch-article pair witnesses | 71 |
| Exact file paths independently checked for Git blob SHA and regular-file mode | 142 / 142 |
| Missing, mismatched, symlink or non-blob observations | 0 |

**Caution:** GitHub API path proof does not replace a trusted native Git checkout and native `validate.py` / `build.py` execution. Nor does it establish that cited claims are true, food preservation is safe, medication advice is safe, or every article retains high editorial reading depth. Current observation shows preservation of frozen source identity and location, not approval.

## Validator / tests

`preparedness/tools/r201_branch_path_witness_gate.py` consumes the previously pinned R200 manifest without rebaselining it and uses `git ls-tree -r -z <exact commit> -- preparedness/content/articles/` for each contributor head. It rejects missing or differently located files, wrong IDs, symlinks, wrong Git types, duplicate routes, missing branch witnesses, altered governance and unsupported QD/commerce/pub claims. A structural match returns **exit 2 / DRAFT_HARD_HOLD**; any absent Git commit, missing manifest, malformed JSON or drift returns **exit 3 / INVALID_HARD_HOLD**. It never returns a PASS state.

```sh
# Trusted clone with all seven Claude commit objects and the R200 manifest:
python -I preparedness/tools/r201_branch_path_witness_gate.py --repo . --report /tmp/preparedness-r201.json
# Exit 2 means structural DRAFT_HARD_HOLD, not permission to release.
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

At R201 authoring, local container DNS could not resolve github.com, so the complete trusted repository, native build and 41 authentic WordPress outputs were not accessible. The R201 Python test suite ran from the **exact authored and GitHub-matched** Python/test Git object identities: 101/101 local synthetic unittest methods PASS, including 70 distinct per-article path substitution methods. `py_compile` PASS. These tests do not make a medical or editorial claim.

## Required independent QA/reconciliation before any release

1. Review QA draft PR #157 against the Start Here source safety state and actual build output. Its corrected lights-out drill avoids cutting main household power; its refrigerated-medication caution still requires qualified review. Never borrow #157's changes silently or mark QD PASS.
2. Review PR #169 and its stacked #973 against the original test suite; their isolated fixtures avoid writing test fragments into shared source directories. Do not overwrite their branch histories.
3. Human source adjudication: preserve all provenance options for `loc-prairie-traveler`, `loc-pioneer-diaries`, `nchfp-jerky`, `nchfp-home`, `nps-lewis-clark-salt`, `nps-salt-works`, `nchfp-historical-origins`. Preserve the distinct `hist-food-nchfp-jerky` identifier pending documentary evidence; **no alias**.
4. Full 35-body depth/content review, 649 original/revised historical citation-occurrence docket from R199, full structural source crosswalk, native source citation resolution and rendered HTML/browser source visibility; never infer safety from machine gates.
5. Inspect all 35 WordPress-ready article exports plus six companion-tool exports for URL duplicates, safety labels, click/print/keyboard, script/network privacy, source notices, mobile and screen-reader use; **do not publish**.
6. Qualifying human source and safety reviews, child-data privacy, food and medical reviewers, separate independent QD and founder release approval must be recorded independently.

## One conversion-first audience and disabled funnel — owned only in Preparedness

**Audience/intention:** a household urgently preparing essential identities, insurance and family-contact records for an evacuation. **Social lead:** Grok/Praxxis TASK-008 retains media and asset_id ownership; no authentic matching published Preparedness asset ID + actual link placement + rights + approved UTMs has been supplied. Do not create/alter their queue. No new posting.

**Free source-backed destination today:** the existing public `https://finalvestige.com/preparedness/` gateway to public-agency resources. **Unpublished candidate free guide:** Household Emergency Plan; requires independent source/safety review. **Unpublished optional free tool:** Family Reunification Card; child-data privacy, browser, paper print and source gates unresolved. **Single optional paid-product candidate:** Legacy Triage; **not authenticated as currently purchasable, rights-cleared, actually deliverable, or good audience fit**. Its CTA MUST remain disabled; do not promise its existence/price/benefits publicly. The existing Seven Day Focus Fieldbook is the sole active lead magnet and is not modified. Do not resurrect retired water lead magnets.

### Draft, NOT-LIVE on-site copy (conditional on all safety and release gates)

> Protect the records and contacts your household would need in an evacuation. Start with verified public-agency planning resources. When independently reviewed, our Household Emergency Plan and optional printable family contact card will be available without a purchase requirement. [No paid product button until verified merchant listing, rights, fulfillment and refund terms.]

No urgency countdown, fabricated health/safety outcomes or lead/email requirement for essential safety information.

### OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| Offer / funnel step | Current blocker | Change / acceptance experiment | Evidence state | Owner |
| --- | --- | --- | --- | --- |
| Legacy Triage candidate → paid order | Rights, exact SKU, price, actual checkout/delivery/refunds/fees unknown | Inspect authenticated seller listing; complete permission, terms, sandbox purchase and fulfilled download checks *without live changes* | **HARD HOLD / NOT VERIFIED** | Founder + Commerce |
| Grok emergency-records topic → website | Exact published `asset_id`, URL, consent/rights, permitted link and approved UTM unknown | Reconcile TASK-008; confirm a matching actually published asset; no production edit | **NO ATTRIBUTABLE ASSET** | Grok + Praxxis |
| Public official-resources gateway → Household Emergency Plan | Original guide source/food/medication QD unresolved | Free guide accessible ungated only after qualified reviews; full citations, no unsupported safety claims | **DRAFT / HOLD** | Preparedness + independent QA |
| Guide → free Reunification Card | Source provenance, child-data privacy, print & keyboard acceptance | Test offline/local-only storage; 360/390/768/1440px; keyboard, no third-party requests, printable legibility; no real child data | **DRAFT / HOLD** | Preparedness + Site QA |
| Optional paid link → merchant confirmed order → net revenue | CTA/merchant/payment acceptance unverified | Test clear price/refunds/disclosure, mobile checkout, merchant-confirmed delivery, fees and refunds before enabling paid CTA | **DISABLED / NO VERIFIED SALE** | Commerce + founder |
| 7/30-day cohort: source qualified-human visit → relevant CTA → confirmed lead → paid order → net realized revenue | No joined source+merchant records | Privacy-respecting aggregate consented attribution; distinct CTA and confirmed signup; no duplicated scripts | **NOT COMPUTABLE** | Analytics / Commerce |

Measurement once permitted: `utm_source`=actual platform, `utm_medium=organic_social`, `utm_campaign=preparedness_pilot_2026_11` only for a *verified* posted asset, `utm_content`=unique actual `asset_id` (never PII). Distinguish qualified human sessions, landing, CTA, confirmed signup, merchant-confirmed order, refund/fees and **realized net**. Report 7/30-day cohorts and small-denominator warnings; no click/view/signup counts are sales. Key KPI net realized revenue per 1,000 qualified human sessions is **NOT COMPUTABLE**.

**Release policy:** DRAFT / HARD HOLD. No WordPress, CMS, navigation, analytics, merchant, affiliate, email, social, founder approval, QD or production writes authorized.
