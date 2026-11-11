# R279 — Raw citation-identity erratum and fail-closed replay (DRAFT / HARD HOLD)

**Owner:** Preparedness integration, Issue #136. **Review only.** Do not merge, publish, export to CMS, alter navigation, activate an offer, or claim independent QD/safety clearance.

## Evidence finding: R277 citation-identity assertion is inaccurate

Independent connected-GitHub reads compared both authentic HTML versions for **all 14 historically changed article bodies**, at the exact R200 contributor SHAs and R275 frozen integrated commit `df96120007ceb33290764392a5900e356e04deac`. The original and integrated body Git blob identities match the existing R200/R277 witnesses. The R277 receipt correctly records the unchanged citation **occurrence totals** for articles 24 and 25, but incorrectly claims their **raw source-ID loss sets are empty**.

| Article | Original cited ID | Integrated cited ID | Exact occurrences replaced | Total cite occurrences before → after |
| --- | --- | --- | ---: | ---: |
| #24 `pioneer-travel-rations` | `nchfp-jerky` | `hist-food-nchfp-jerky` | **1** | 39 → 39 |
| #25 `pemmican-and-dried-meats` | `nchfp-jerky` | `hist-food-nchfp-jerky` | **7** | 46 → 46 |
| All other changed article bodies | No raw-ID loss identified in the authenticated pairwise scan | New IDs are separately inventoried in the R277 receipt | **0 replacements** | R277 totals rechecked |

**Raw source-ID substitutions: eight occurrences in two articles.** R277's `removed_citation_id_sets: 0` is not accurate as a claim about the true original/integrated HTML sources. Historical R277 files are preserved as immutable evidence; this addendum supersedes ONLY that false raw-ID conclusion. Do not silently normalize different identifiers and call them equal.

The original `hist-food.json` Git blob is `c1856c998c6c728f0de72221e5654a238df994a9` at `67e116e536c7410bed30f8f3b1bb8c166f3c223d`. The integrated fragment Git blob is `d10628342fea5f177a8d1be00dd906d0c9c7850e` at R275. Their `Jerky` source records have the same title and `supports` text, and URLs differing by a trailing slash. Their **literal IDs and notes differ**. Those are *candidate provenance-equivalence facts*, not a verified safety or sourcing approval. Preserve both records, the NCHFP/FSIS drying-temperature disagreement, and the food-safety editorial hold.

## New executable gate

`preparedness/tools/r279_reconciliation_citation_guard.py` derives from the R278 source/custody guard and adds **30 local Git-object checks**: 28 original/integrated HTML bodies across the 14 changed articles and both original/integrated `hist-food` source registers. It verifies exact source Git IDs, citation counts, raw ID-set changes, unchanged-ID occurrence multiplicities, the known 1+7 substitution, and both source register identities. It refuses an unrecognized removed ID, concealed loss of occurrences, malformed citation placeholders, switched origin, altered source record, or implicit sign-off.

Run only against a FULL repository containing the historical objects:

```bash
python -I preparedness/tools/r279_reconciliation_citation_guard.py \
  --root preparedness --repo .
```

Exit 2 denotes an accurate **DRAFT_HARD_HOLD** report, **not publication PASS**; exit 3 denotes **INVALID_HARD_HOLD** and must block draft export. The R278 original `inspect` still reports historical structural census; only R279's raw Git replay can correct the inaccurate R277 citation-ID statement. A complete audit **cannot be marked run without access to the authentic Git objects**.

## Test/evidence status

- **BUILT:** New R279 source and expanded R278-derived regression suite. No article, tool, source register, canonical URL, or publisher modified.
- **TESTED IN ISOLATION:** Local Python 101/101 tests pass on source-equivalent files; Python compileall passes. These exercise synthetic adversarial citation data and inherited 70 provenance/structure tests, not the full authentic Git replay. GitHub committed file identities must be compared separately.
- **AUTHENTIC GITHUB READ VERIFICATION:** 14 original/integrated body pairs, with original/integrated OIDs and citation occurrence totals checked; only #24 and #25 had raw lost-ID sets. Original/integrated NCHFP source fragment records and exact OIDs checked.
- **NOT EXECUTED:** Local native `validate.py`, `build.py`, full inherited suite, R279 full Git replay, and all 41 intended WordPress draft exports because local GitHub DNS cannot provide a full repo checkout.
- **UNRESOLVED:** 32 shared-URL groups, 15 duplicate source-ID groups, three CDC/Ready.gov disputed occurrences, Article #7 chemical-contamination discussion, Article #15/Tool #104 child-information privacy, readability, print and accessibility, plus substantive semantic review of 17 historically changed articles. No medical/privacy approval or independent QD PASS.

## Commercial / conversion-first hold — coordinate #820, #818, TASK-008

**One provisional candidate only: Legacy Triage existing paid PDF** for households interested in emergency contact/reunification planning. It is **not approved** as a Preparedness upsell until the founder/Commerce audits the complete rights-cleared product, appropriate audience-fit, actual checkout/fulfillment, refund policy and merchant evidence. Do not introduce a retired water freebie or an unreleased contact card.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Free existing public Preparedness Archive | Existing published Grok asset → archive | No verified published family-contact asset ID, rights or mobile click packet | Grok/Praxxis validate a single already-published `asset_id`, `utm_campaign`, post URL/date, native phone link | **NO VERIFIED MATCH** | Grok / Praxxis |
| Free emergency planning guidance | Guide → optional practical download | Source safety and family privacy holds | Independent editorial, accessibility, physical printing/cutting and source review | **HARD HOLD** | Preparedness / QA |
| Legacy Triage (provisional owned PDF) | Relevant guide → optional paid pack | Product relevance, licensing, privacy and founder approval unknown | Inspect actual PDF, pricing/rights and merchant terms; draft CTA only after evidence | **NOT APPROVED** | Founder / Commerce |
| Optional verified paid pack | CTA → checkout → delivered usable PDF | Mobile checkout, fees, refunds, delivery unverified | Authorized signed-out mobile checkout test without unapproved spend | **NOT TESTED** | Commerce |
| Paid order → realized net | Seven/30-day attributable customer cohort | Merchant-confirmed order IDs and qualified-human session attribution absent | Deduplicate qualified sessions; reconcile fees/refunds against confirmed paid orders | **NOT COMPUTABLE** | Analytics / Commerce |

**Provisional draft-only CTA (NOT TO DEPLOY):** “Start with the free emergency-planning information. A separate practical download may be offered if its contents, delivery and pricing pass review.” Do not show a paid purchase button or imply Legacy Triage contains approved emergency instructions.

**Measurement contract:** unique consent-appropriate Grok `asset_id` / `utm_campaign` → qualified-human session → landing visit → relevant CTA → confirmed lead where applicable → merchant-verified paid order → fees and refunds → realized net revenue. Primary KPI: confirmed net revenue per 1,000 qualified human sessions, segmented by 7- and 30-day cohorts. Current value **NOT COMPUTABLE, not zero**; do not count clicks, leads or checkout starts as paid sales.

**Governance:** No public, CMS, navigation, publishing, merchandise, analytics, email, social, affiliate, spending or checkout changes. Grok owns creation/posts; Praxxis QA; Claude owns site engineering; founder owns production release and spend.
