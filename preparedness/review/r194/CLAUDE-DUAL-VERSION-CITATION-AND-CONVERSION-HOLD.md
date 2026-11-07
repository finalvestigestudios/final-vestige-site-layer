# R194 — Contributor two-version citation evidence custody (DRAFT / HARD HOLD)

**Preparedness owner:** Issue #136 only. **Business cross-reference:** #820 and #818.  
**Date:** 2026-11-07 PT. **Scope:** preserve old AND new research, not accept or publish changes.

## Newly authenticated evidence, compared to the HISTORICAL source crosswalk

The current seven Claude branch heads were inspected through GitHub against the original
\`preparedness/sources/crosswalk.json\` source-head pins. Separately, each current
head was compared against its own last recorded head: **7/7 identical**, no evidence of
movement during this check. Comparing against the **older crosswalk** instead shows:

| Original cluster | Historical crosswalk → current | Files changed |
| --- | --- | --- |
| Start | identical 0/0, 2122d856 | none |
| Shelter | identical 0/0, 5daeaf2d | none |
| Food | diverged 1 ahead / 1 behind, current f911ff7a | cluster docs and shared test module; authored articles unchanged |
| Health | ahead 1, current d5ef5baf | cluster docs only |
| Historical field | ahead 1, current 4e5caf81 | 2 article bodies, 1 meta, source fragment, docs |
| Historical food | ahead 1, current 67e116e5 | 2 bodies, 2 meta, source fragment, docs, shared tests |
| Historical home | ahead 2, current 7504a5f0 | 3 bodies, 3 meta, source fragment, docs |

The complete 40-character refs and old/new article Git blob identities are preserved in
\`SEVEN-ARTICLE-DUAL-VERSION-OBJECTS.json\`. They were read directly through authenticated
GitHub file retrieval at each historical and current contributor commit. The new
\`r194_dual_version_citation_gate.py\` reads the complete two-version Git objects
locally (when available) and refuses substitution, duplicate routes, malformed citations,
citation-count drift, source-use gaps, changed historical safety-review states,
publication claims and missing objects. A structurally matching docket is **still
DRAFT_HARD_HOLD with exit code 2**, never approval.

## Actual citation and reading-depth changes in seven article bodies

| Article | Citations old → new | Plain-text words old → new | Critical review reason |
| --- | ---: | ---: | --- |
| Navigation Before GPS | 47 → 47 | 2,900 → 2,900 | Different blob despite equal citation sequence; prose context needs review |
| Pioneer Supply Chains Failed | 57 → 63 | 2,788 → 3,149 | Two new primary-reading IDs, Hastings guide and Breen diary; +6 citations |
| Pemmican and Dried Meats | 46 → 46 | 2,413 → 2,413 | **Citation source ID changed** from \`hist-food-nchfp-jerky\` to \`nchfp-jerky\` (7 occurrences); not automatically equivalent |
| Pioneer Travel Rations | 39 → 39 | 2,350 → 2,350 | Same jerky ID shift (1 occurrence), no implicit alias |
| Pickling / Fermentation | 42 → 49 | 2,389 → 2,754 | New 1798 Simmons primary transcription and changed CDC citation counts; food safety reviewer required |
| Root Cellars | 37 → 42 | 2,432 → 2,799 | Simmons primary source added; cannot equate historical storage with safe modern food storage |
| Sanitation Before Germ Theory | 47 → 48 | 2,644 → 2,678 | New Wellcome Chadwick 1842 archival record; distinguish catalogue from primary-text verification |

**Total for these seven only: 315 → 334 citation occurrences (+19).** Neither
the equal-count jerky swaps nor the added citations prove that their cited claims
are actually supported. All seven original and observed full-body Git blobs
remain separately addressable; **no unabridged article was truncated or replaced
by this PR**. This 7-article delta is NOT the complete 35-article/2,000-citation
native validation.

Source fragment row counts from authenticated GitHub: Historical Field **26 → 28**,
Historical Food **28 → 28**, Historical Home **27 → 29**. Old and new fragment
Git identities are in the docket. They must not be silently aliased, merged,
rebaselined or represented as independently verified. Existing 32 shared-URL
groups and their human source-reading review remain OPEN.

## QA and integration governance

- Independent safety PR #157 (\`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`)
  corrects dangerous Start Here breaker wording, medication handling and taxonomy.
- Synthetic fixture PR #169 (\`e9cd7766dac59d47ab467d8945269b9146c2aef5\`) and
  its follow-up #973 (\`4d40996a559b0124d74a9bb3bdcd481ad1992aa8\`)
  isolate in-memory or temporary source tests. **All are draft/unmerged.**
- These contributions alter the common \`preparedness/tests/test_preparedness.py\`.
  Reconcile their exact tests against both source states rather than blind merge.
- No original article/tool body, citation, source registry, canonical URL,
  safety status, homepage, navigation, merchant or analytics code changed in R194.
- Local \`git ls-remote\` still fails with \`Could not resolve host: github.com\`.
  **83 synthetic regressions ran in a locally reproduced R194 module layout,
  zero skipped**, and Python isolated-mode compilation passed. The committed
  GitHub source/test blobs were read back, but differ in formatting/import path
  from that tested reproduction; **exact committed-suite execution, authentic
  seven-object CLI gate, native 35+6 validate/build/36+ repository tests, all 41
  WP exports, browser, safety, privacy and independent QD are NOT VERIFIED.**

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Change / acceptance | Evidence / owner |
| --- | --- | --- | --- | --- |
| Legacy Triage — candidate only | optional purchased household-records pack | Seller rights, real SKU, PDF, paid checkout, delivery/refunds/fees, fit not authenticated | Founder/Commerce/Claude independently verify rights and real fulfillment; **no paid CTA/schema now** | HARD HOLD, zero verified orders |
| Live \`/preparedness/\` official-resource gateway → held Household Emergency Plan | Grok household-document discovery → ungated free guide | Full guide source/safety/QD held; asset_id, public media URL, source rights, CTA destination unconfirmed in TASK-008 | Praxxis/Grok reconcile actual media and approved destination; preserve current creator queue | UNKNOWN attributed sessions |
| Unpublished Family Reunification Card | free reader → optional printable | 11 source decisions, family/child privacy, local storage, mobile/keyboard/printing untested | Site QA stage only synthetic identities at 360/390/768/1440 px; no personal data transmission | HARD HOLD |
| Existing Seven Day Focus Fieldbook | optional direct-audience capture, separate from emergency instructions | No Preparedness-specific authenticated confirmed leads/delivery | Keep existing single signup; require Jetpack-confirmed consent, not a query string | UNKNOWN |
| Authenticated paid order | customer → realized net revenue | No verified merchant settlements, refunds/fees or qualified-human cohort denominator | Commerce/Analytics reconcile 7/30-day cohorts | Net revenue per 1,000 qualified humans NOT COMPUTABLE |

The suggested research-only creator question remains: **“Could you locate your
identity, insurance and family contact records if you had to leave tonight?”**
This is NOT a new Grok content assignment, not proof of a purchasable offer,
and not an authorization to publish drafts or retarget the retired water freebie.

## Required exit gates

1. Trusted complete checkout and exact full-object R194 invocation; reconcile
   source ID readings and original/observed citations individually.
2. Native 35+6 validation/build, 41 WP drafts, 36+ original tests and all independent
   safety, source, food, medication, privacy/accessibility/printing, QD review.
3. Separate merchant/rights/fulfillment and actual Grok TASK-008 attribution proof.
4. Founder release approval. **No merge, WP/CMS/nav/home/site/social/email/merchant
   activation, affiliate write, tracking script, or spending permission.**
