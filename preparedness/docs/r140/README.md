# R140 — Contributor article intake review (DRAFT / HOLD)

Scope: Preparedness Archive only. Source-of-truth #136; conversion coordination #820/#818. Exact parent R139 draft #1063 `f88ec21534cf6166e52adab3ed246cdc89f09198`. Source candidate: frozen RC #584 `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. This is a reviewer aid, not a safety approval, QD PASS, commerce verification, or permission to merge/publish.

## Independent observation — 2026-11-05

Read actual GitHub trees for the frozen RC, R139, and all **seven canonical Claude branch HEADs**, then inspected **both authentic body versions for each of 14 SHA-different article pairs** (28 connected file reads). Unlike misleading root-level comparison of divergent branches, this compares exact *overlapping file paths and blobs*; a contributor branch missing most other RC articles is **not** evidence that the release candidate deleted them. Exact branch SHAs and per-article Git blob identities are frozen in `branch_intake_evidence.json`.

### Replaying unreviewed contributor files would regress release-candidate depth

| Article | Approx. RC → contributor words | Citation occurrences RC → contributor | Gate |
| --- | ---: | ---: | --- |
| Start / go-bags | 3,638 → 3,397 | 73 → 72 | HOLD depth/citations |
| Start / household-emergency-plan | 3,434 → 3,193 | 57 → 57 | HOLD depth |
| Start / preparedness-real-households | 3,400 → 3,171 | 64 → 64 | HOLD depth |
| Start / three-day-kit | 3,790 → 3,326 | 79 → 75 | HOLD depth/citations |
| Shelter / family-communication-plan | 3,563 → 3,026 | 69 → 62 | HOLD depth/citations |
| Shelter / home-fire-escape-plan | 4,256 → 3,746 | 73 → 70 | HOLD depth/citations |
| Shelter / outage-heat-cold-generators | 4,463 → 4,196 | 121 → 116 | HOLD depth/citations |
| Shelter / shelter-or-evacuate | 4,193 → 3,437 | 59 → 50 | HOLD depth/citations |
| Historical Food / pemmican-and-dried-meats | 2,413 → 2,413 | 46 → 46 | HOLD source-ID retarget |
| Historical Food / pioneer-travel-rations | 2,350 → 2,350 | 39 → 39 | HOLD source-ID retarget |
| Historical Home / root-cellars-cool-storage | 2,793 → 2,793 | 42 → 42 | BLOB provenance review |
| Historical Home / sanitation-before-germ-theory | 2,673 → 2,673 | 48 → 48 | BLOB provenance review |
| Historical Field / navigation-before-gps | 2,889 → 2,889 | 47 → 47 | BLOB provenance review |
| Historical Field / pioneer-supply-chains-failed | 3,136 → 3,136 | 63 → 63 | BLOB provenance review |

**Eight Start/Shelter body substitutions collectively remove ~3,245 whitespace-counted words and 29 citation-token occurrences relative to the richer frozen RC.** HTML tags and citation tokens were excluded from the approximate word metric. Citation-token count does not prove an individual claim is supported; potential material loss does justify withholding automatic replacement. Protect high-stakes CO/generator, fire, chemical evacuation, school pickup and family-reunification material for qualified review.

Some citation IDs disappear entirely from the smaller bodies: `start-fsis-emergency-food`; `shelter-cdc-chemical-sip`; `shelter-cdc-chemical-evac`; `shelter-ready-tech`; `shelter-ca-cde-safety-plans`; `shelter-ncmec-hotline`; `shelter-fema-reunification`; `shelter-usfa-escape-grid`; `shelter-nfpa-high-rise`; `shelter-usfa-high-rise-handout`; `shelter-cpsc-co-tips`; `shelter-nws-winter-during`; `fsis-power-failure`. No source adequacy is inferred from missing/present identifiers alone.

The Historical Food two-article drift retargets `hist-food-nchfp-jerky` to `nchfp-jerky` across eight citation occurrences while leaving counts and approximate words unchanged. The original author's source interpretation and the Food author record must remain separately traceable: S-7 HOLD. All **32** shared-source crosswalk groups remain subject to human review. No automatic source merging or historical technique safety inference.

## Review-only deterministic gate

Use only on an authenticated full checkout with every draft article and the locked R133–R139 gates:

```sh
python -I preparedness/tools/r140_contributor_intake.py --manifest preparedness/docs/r140/branch_intake_evidence.json --root . --report /tmp/r140-intake.json
python -I -m unittest discover -s preparedness/tests -p 'test_r140_contributor_intake.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The tool validates seven exact 40-character branch-head identities, 14 unique path-safe article slugs, frozen Git blob SHA-1 identities, author/source-ID drift and review-only manifest shape. It checks current worktree bytes without changing them: `BASELINE_BLOB_PRESERVED_NOT_SAFETY_APPROVED`, `UNREVIEWED_CONTRIBUTOR_REPLACEMENT_HOLD`, `UNREVIEWED_THIRD_VERSION_HOLD`, `MISSING_ARTICLE_HOLD`, `SYMLINK_ARTICLE_HOLD`. Malformed manifests, forged approval fields, reused source-ID mappings and changed articles fail closed. Even intact blobs print `DRAFT_HOLD_NO_PUBLICATION`; the tool cannot grant medical safety, source acceptance, QD PASS or publishing. R133/R139 remain responsible for full 35-article custody. Run independent QA #157 and fixture #169 plus proposed fix #973 with qualified reviewers before release.

## Conversion-first, source-safe staged funnel (no live change)

**High-intent audience:** households preparing emergency contacts, school pickup and family reunification. **Free page:** existing *Household Emergency Plan*, unpublished and safety-review pending. **Optional practical download:** existing family-reunification card, accessibility/privacy and print QA pending. **Paid pack:** no authenticated matching FV-owned, rights-cleared, *currently purchasable* Preparedness SKU, merchant acceptance, download entitlement or refund record—**HOLD**. Do not invent a product or price, resurrect retired water freebies, or attach unrelated affiliate offers.

Draft on-page CTA for future review: “Make a family emergency plan. Read the free guide; download the printable contact and reunification card.” This is not permission to publish, gate core safety guidance behind email or change navigation.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE EXPERIMENT | EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Real FV paid pack → paid order | No authenticated seller SKU, rights, fulfillment or refunds | Verify live merchant listing and staged delivery, then obtain founder approval before any paid CTA | HOLD / UNVERIFIED | Growth / Claude |
| Free household guide → reader | R140 article drift, #157 high-stakes wording, 32 shared groups, independent safety review | Keep richer RC text; adjudicate citations and qualify emergency instructions before staging | 14 authenticated comparisons / 71 local tests | Preparedness / QD |
| Grok asset → source-backed guide | No verified Preparedness `asset_id`, social placement or destination URL | Reconcile authentic TASK-008 asset, campaign UTMs and approved link path, without editing Grok queue | UNVERIFIED | Grok / Praxxis |
| Guide → optional card | Privacy, download, keyboard, print, mobile QA incomplete | Check 360/390/768/1440px, source visibility, no PII in URLs or analytics, free no-email access | NOT TESTED | Preparedness / Site QA |
| Qualified human → realized net revenue | No paid orders, refunds, fees or qualified-session attribution reconciled | 7/30d exact `asset_id` cohorts; *paid order only* counts as sale | NOT COMPUTABLE | Growth / Claude |

Do not conflate Jetpack views, affiliate outbound clicks, checkout starts or confirmed leads with purchases. No production/WP/CMS/navigation/homepage/analytics, seller, social, affiliate, subscriber or email writes.
