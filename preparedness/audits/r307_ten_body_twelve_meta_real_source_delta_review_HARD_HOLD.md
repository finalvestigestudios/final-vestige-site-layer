# R307 real-source diff dossier: ten substantive body revisions / twelve metadata changes

**Preparedness Archive only · DRAFT / HARD HOLD · 2026-11-12 UTC**. Exact source read via GitHub connector by blob OID from frozen R200 manifest `5822f9dfde21d1f3bdfc26658769d852c639438c` and integrated R306 crosswalk `c7ab84eeacbd43f17bb3cab72a888430cb102f25`. Each pair below is a **real GitHub source blob read**, not a generated synthetic fixture. No content approved, edited or published. Source of truth: [Issue #136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), with conversion coordination [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

## Source-body change crosswalk: all ten non-format-only revisions

All ten integrated article versions have **different exact Git blob IDs** from their frozen R200 originals. Mechanical counts below count `{{cite:...}}` occurrences, not verified credible claims. "Words" are only approximate whitespace-separated HTML-text tokens; this is **not** full reading-depth or citation-placement certification. All ten retained the same ordered heading markup on this particular comparison; paragraph text, citation contexts, warnings, structure and safety meaning still require human review.

| Article | Frozen → integrated blob prefixes | Approx. tokens old → new | Citation occurrences old → new | New / substituted citation identities | Review priority |
|---|---|---:|---:|---|---|
| 01 `household-emergency-plan` | `8ca5c261` → `f81cd435` | 3,195 → 3,436 | 57 → 57 | No ID-set addition/removal; claim text still revised | Compare changed instructions, official-action priorities |
| 02 `three-day-kit` | `ef5463ca` → `933f38ff` | 3,328 → 3,792 | 75 → 79 | Added `start-fsis-emergency-food`, `start-cdc-power-outage` | **HIGH:** time/temp food safety claims versus exact FSIS/CDC scope |
| 12 `outage-heat-cold-generators` | `47d949d9` → `2cd3e30b` | 4,202 → 4,469 | 116 → 121 | Added `shelter-cpsc-co-tips`, `shelter-nws-winter-during`, `fsis-power-failure` | **HIGH:** CO/generator and food-outage hazard instructions |
| 13 `home-fire-escape-plan` | `ba869874` → `04124843` | 3,749 → 4,259 | 70 → 73 | Added `shelter-usfa-escape-grid`, `shelter-nfpa-high-rise`, `shelter-usfa-high-rise-handout` | **HIGH:** actual escape grid guidance, high-rise and worksheet rights/targets |
| 14 `shelter-or-evacuate` | `b8acf07e` → `de3cb805` | 3,439 → 4,195 | 50 → 59 | Added `shelter-cdc-chemical-sip`, `shelter-cdc-chemical-evac` | **HIGH:** official/local instructions, location/time hazard distinctions |
| 15 `family-communication-plan` | `16e2b1ec` → `8ac8bd7d` | 3,029 → 3,566 | 62 → 69 | Added `shelter-cdc-chemical-sip`, `shelter-ready-tech`, `shelter-ca-cde-safety-plans`, `shelter-cdc-chemical-evac`, `shelter-ncmec-hotline`, `shelter-fema-reunification` | **HIGH:** children, school pickup, 911/text-to-911 limits, contact-card privacy |
| 16 `go-bags` | `51356397` → `e5910015` | 3,399 → 3,640 | 72 → 73 | No new unique IDs; citation placement/claim context may differ | Check medication and disability/infant/pet handling |
| 20 `preparedness-real-households` | `70d03c36` → `68344cf6` | 3,173 → 3,402 | 64 → 64 | No unique ID change; guidance text revised | Check budget/accessibility/renter cases and promises |
| 24 `pioneer-travel-rations` | `a658481d` → `058c90b7` | 2,352 → 2,352 | 39 → 39 | **Replaced** `nchfp-jerky` with `hist-food-nchfp-jerky` | **HIGH:** verify source provenance, publisher and historical-vs-modern advisory scope |
| 25 `pemmican-and-dried-meats` | `1febc892` → `0b3319cc` | 2,415 → 2,415 | 46 → 46 | **Replaced** `nchfp-jerky` with `hist-food-nchfp-jerky` | **HIGH:** same source-identity change; no implicit approval of traditional food handling |

**Important exception:** A citation count staying constant does not mean the original claims remain unchanged or properly supported; newly added citations do not establish that the new cited source actually supports the sentence. Exact citation occurrence context still needs independent claim-to-source review. The replacement of `nchfp-jerky` in two historical pieces must retain a visible provenance trail; the new ID is not automatically equivalent to the old one.

## Frozen-to-integrated article metadata: all twelve changed byte identities

Keys below were identified by parsing **both original and integrated Git blob JSON values**, with exact source bytes retained by their blob IDs. Changed keys are not automatically approved or safe; especially, `safety_review.state="approved"` is **not an independent QD PASS**.

| Article | Frozen → integrated metadata blob prefixes | Changed parsed keys / discrepancy |
|---|---|---|
| 02 `three-day-kit` | `c830e4b8` → `1c69d5f1` | `source_use` |
| 06 `making-water-safer` | `bcb56790` → `827d861e` | `safety_review`: founder attribution explicitly qualified to unconfirmed name/scope while legacy state remains `approved`; **independent safety HOLD** |
| 07 `homemade-water-filters` | `33789d3d` → `91c730bd` | `source_use`: unsafe-water claim support review remains **HIGH** |
| 12 `outage-heat-cold-generators` | `77dd194b` → `be37b602` | `updated`, `last_checked`, `related`, `source_use` |
| 13 `home-fire-escape-plan` | `6a54547e` → `ff1246dc` | `updated`, `last_checked`, `related`, `source_use` |
| 14 `shelter-or-evacuate` | `fe90c9ef` → `cb559141` | `dek`, `description`, `updated`, `last_checked`, `related`, `source_use` |
| 15 `family-communication-plan` | `e63bbe70` → `dcad79fa` | `updated`, `last_checked`, `related`, `source_use` |
| 20 `preparedness-real-households` | `a0c3a091` → `ba840917` | `source_use` |
| 21 `salt-beef-salt-pork-age-of-sail` | `06b1cec8` → `1c4c5396` | `safety_review`: founder identity/scope qualified, legacy `approved` cannot certify modern safe practice |
| 24 `pioneer-travel-rations` | `521e56a3` → `7191acba` | `source_use`: verify `hist-food-nchfp-jerky` citation source identity |
| 25 `pemmican-and-dried-meats` | `c19f68f2` → `03d3824e` | `source_use`: verify `hist-food-nchfp-jerky` |
| 34 `pioneer-supply-chains-failed` | `8789c77d` → `4d2dc495` | **No changed parsed top-level JSON values** despite byte identity difference. This establishes semantic top-level JSON value parity for this comparison, not exact byte parity, rights, or safety approval |

No content deleted or introduced by producing this crosswalk. Frozen canonical routes are unchanged under R306 checks. Four separately confirmed CRLF-only **article-body** revisions are outside these ten; their exact source-bound normalized SHA-256 proofs are recorded in `r307_encoded_fragment_and_frozen_body_proofs_HARD_HOLD.md`.

## Deterministic adjudication queue and release boundaries

**P0 qualified safety review:** 02 food thresholds; 12 CO/generator and emergency refrigeration; 13 fire escape/high-rise/print worksheet; 14 chemical shelter versus evacuation; 15 school reunification and communications; 06/07 water-treatment review state/source scope; Tool #104 card privacy/no-JS/print/emergency dispatch. **P1 source authority:** 24/25 historical jerky-source identity, 21 safety attribution and remaining 12 metadata records. **P2 text/experience parity:** complete article wording including 01, 16, 20; all 41 native WordPress draft exports; mobile, print, actual CTA; no duplicate URL or loss of reading depth.

Acceptance requires full independent source-claim verification, provenance/rights checks, exact native build, WP-ready draft comparison, and qualified safety/privacy review. **The present source diff establishes custody and triage only, not a publishable 35-article slate.** No QD PASS, medical-safety approval or merchant purchase claim.

**Conversion-first: one audience only.** Target a verified existing Grok family-contact asset (none yet authenticated) to the free existing Preparedness Archive, then optional independently reviewed Tool #104; only map an optional *paid* practical pack when Founder/Commerce authenticates one actively buyable licensed/deliverable SKU. No retired water offer or Legacy Triage by default. `utm_content=asset_id` → qualified-human sessions → intent-matched CTA → confirmed lead (if observable) → independently paid order → refunds/fees → realized net revenue per 1k qualified human sessions, 7/30 day cohorts. No verified commercial conversions yet, so KPI **NOT COMPUTABLE**.

**Hard hold:** independent QA [PR #157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157), synthetic fixture [PR #169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) (real-source directory write still present), and R307/ancestor drafts remain unmerged; no public publishing, CMS/navigation, social, email, merchant, analytics or spending changes.
