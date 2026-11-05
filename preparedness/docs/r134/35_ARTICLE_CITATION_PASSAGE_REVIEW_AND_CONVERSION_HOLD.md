# R134 — 35-article source-to-passage reviewer packet — DRAFT / HOLD

**Scope:** Final Vestige Preparedness Archive only. Governed by [Issue #136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), conversion coordination [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), and charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). No public publishing, CMS, nav, tracking, emails, affiliate activation, social posts or merchant changes are authorized.

**Stacked draft base:** PR #1025 exact head `233ba9876b88508d103c5d7fe13906dd975eabc5`, which is stacked on PR #1012 at `5685b54796d520e8dd50e0cdf4d35e38c9cec7a4` and the original release candidate #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. The R133 source custody manifest fixes 80 Git blobs (35 HTML, 35 metadata, 8 source registers, taxonomy, crosswalk).

## New capability

`preparedness/tools/r134_reviewer_packet.py` is a **read-only** reviewer packet generator. It runs the immutable R133 custody audit first and exits HOLD on drift. It then emits deterministic JSON that binds **each visible citation occurrence** to the specific article passage, contributing author's source register (falling back to base only as declared), source URL/publisher, author's exact `source_use` explanation, source's exact `supports` wording, verification date, human-link-check field, matching pending crosswalk group, and whether a same-ID base record was shadowed by a different author-specific interpretation.

Passages mentioning water treatment, food preservation, electrical/generator/carbon-monoxide hazards, medication and medical dependency, or evacuation are placed in an **attention worklist**. A keyword-matched passage with no inline citation receives an attention flag, **not a finding of falsehood or unsafe advice**. Author-scoped collisions are disclosed, never deduplicated. The packet explicitly returns `status=HOLD`, `may_publish=false`, `qd_pass=false`, and `merchant_offer_verified=false`. It does not rewrite article text, cited IDs, safety metadata, source rows, crosswalk states or any public content.

**Exact-checkout command** (read-only; redirect to a local nonpublic artifact only if wanted):

```bash
python -I preparedness/tools/r133_snapshot_gate.py
python -I preparedness/tools/r134_reviewer_packet.py > /tmp/preparedness-r134-human-review.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -p 'test_*.py'
```

The last three commands must be executed on an authenticated complete checkout. A zero exit from structural validation is **not** human safety/QD approval.

## Actual GitHub article custody check — independently re-fetched November 4, 2026

Authenticated connected GitHub reads at exact R133 head retrieved **all 35 article bodies and all 35 matching metadata records**. All **70/70 exact Git blob IDs matched** the immutable custody manifest. A separate conservative HTML-tag-stripping pass counted **2,000 visible-token-pattern citation occurrences**, **385 distinct per-article `source_use` bindings**, and **~102,404 prose words** (rough approximation, *not* canonical builder word counts). All articles had **at least ~1,846 words** in this pass; no missing `source_use` names, unexplained extra `source_use` keys or non-draft publication flags were observed in these 70 files. Metadata safety states remain **29 pending / 2 marked approved / 4 marked not-required**: these are preserved historical fields, **not an independent approval**. This independent read **does not** substitute for full native R133/R134, source content confirmation, or professional review.

| Exact slug | Approx. words | Citation occurrences | Author source IDs | Historical safety state |
|---|---:|---:|---:|---|
| `emergency-hygiene-sanitation` | 3230 | 62 | 7 | pending |
| `family-communication-plan` | 3530 | 69 | 20 | pending |
| `fire-making-across-time` | 3100 | 67 | 11 | pending |
| `food-safety-power-outage` | 3030 | 69 | 9 | pending |
| `go-bags` | 3604 | 73 | 18 | pending |
| `history-of-food-preservation` | 2157 | 47 | 12 | pending |
| `home-fire-escape-plan` | 4209 | 73 | 13 | pending |
| `homemade-water-filters` | 1914 | 51 | 6 | pending |
| `household-emergency-plan` | 3401 | 57 | 14 | pending |
| `lewis-and-clark-salt-works` | 2292 | 49 | 11 | pending |
| `making-water-safer` | 2869 | 52 | 8 | approved (historical metadata) |
| `medication-and-devices` | 3913 | 68 | 9 | pending |
| `navigation-before-gps` | 2852 | 47 | 10 | not-required (historical metadata) |
| `outage-heat-cold-generators` | 4422 | 121 | 19 | pending |
| `pantry-rotation` | 3016 | 68 | 9 | pending |
| `pemmican-and-dried-meats` | 2379 | 46 | 11 | pending |
| `pickling-fermentation-old-recipes` | 2704 | 49 | 10 | pending |
| `pioneer-supply-chains-failed` | 3084 | 63 | 11 | not-required (historical metadata) |
| `pioneer-travel-rations` | 2302 | 39 | 10 | pending |
| `preparedness-real-households` | 3355 | 64 | 17 | pending |
| `pressure-canning-low-acid` | 3412 | 74 | 17 | pending |
| `rain-barrels-and-cisterns` | 2571 | 44 | 7 | pending |
| `root-cellars-cool-storage` | 2734 | 42 | 8 | not-required (historical metadata) |
| `safe-jerky-dehydration` | 2822 | 71 | 11 | pending |
| `salt-beef-salt-pork-age-of-sail` | 2822 | 49 | 10 | approved (historical metadata) |
| `sanitation-before-germ-theory` | 2611 | 48 | 10 | not-required (historical metadata) |
| `shelter-or-evacuate` | 4156 | 59 | 15 | pending |
| `ships-biscuit-and-hardtack` | 2609 | 42 | 8 | pending |
| `smokehouses-salting-curing` | 2113 | 36 | 11 | pending |
| `three-day-kit` | 3731 | 79 | 18 | pending |
| `two-week-water-storage` | 1868 | 28 | 3 | pending |
| `warnings-radios-offline-maps` | 2891 | 55 | 9 | pending |
| `water-advisories-explained` | 1846 | 30 | 4 | pending |
| `water-math` | 1972 | 33 | 5 | pending |
| `water-purification-through-history` | 2883 | 76 | 14 | pending |
| **TOTAL** | **~102,404** | **2,000** | **385** | **29 pending, 2 approved, 4 not-required** |

**Human prioritization:** qualified reviewers should first inspect medication refrigeration/medical devices, generators/CO and electrical drills, tested pressure canning and jerky, hazardous water treatment, then evacuation and all other safety-relevant content. The author-source binding and excerpt do not establish that the cited source actually supports the sentence; each claim must be read against the underlying source and updated standards.

## Seven-branch snapshot and external QA coordination

Checked exact GitHub refs November 4, 2026:

| Origin | Current commit | Relative to frozen contributor SHA |
|---|---|---|
| Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` | identical |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | identical |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | **diverged**: 1 ahead / 1 behind (docs + fixture tests) |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | 1 commit ahead (cluster doc) |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | 1 ahead (2 article bodies, 2 metadata, source register, tests, doc) |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | 2 ahead (3 bodies/3 metadata, register, doc) |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | 1 ahead (2 bodies, 1 metadata, register, doc) |

Outstanding **S-7**: Historical Food changes 8 occurrences of the NCHFP jerky citation ID to one that conflicts with Food's existing meaning; do not auto-retarget. All **32 source crosswalk groups remain pending human review** even though R132 structurally covers all 32. Independent QA PR #157 remains an open draft with distinct electrical-drill and refrigerated-medication wording requiring qualified adjudication. Food fixture PR #169 is open, and its separate isolated-fixture repair PR #973 is unmerged. Homepage PR #49 (`10495883299d53596992c26a8987f629b2904670`) and flagship PR #604 (`bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`) untouched.

## Conversion-first handoff (do not place new public CTA)

**One high-intent audience:** parents/caregivers planning emergency contacts, school pickup, and household reunification. **Existing source-backed free destination:** the held draft *Household Emergency Plan*. **Optional free tool:** pre-existing family-reunification printable, still needing local-data/privacy, accessible-print and phone QA. **Optional paid practical pack:** **NONE VERIFIED** as currently FV-owned, rights-cleared, genuinely purchasable, deliverable and appropriate; therefore **no paid CTA, price or checkout URL** is staged or published. The retired Water manual remains excluded. The public non-instructional Preparedness gateway was reported live by a separate website owner; this lane did not modify it or treat held 35 articles as live.

**Proposed DRAFT copy only:** “Make a family contact plan you can actually practice. Read the free Household Emergency Plan, then use the optional family-reunification worksheet to put your contacts and pickup arrangements in one place.” Do not surface until both actual assets and destinations pass release review. Paid CTA may be designed only after independent SKU/rights/merchant verification.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Verified owned paid pack → confirmed order | No authenticated matching FV SKU, rights, merchant checkout, delivery or refund evidence | Confirm actual listing/price/files/rights; stage test purchase/refund fulfillment with approved testing authority | **UNVERIFIED / HOLD** | Growth / Claude |
| Free guide → qualified reader | 32 source groups pending; safety wording and R133 custody native execution incomplete | Qualified source/safety adjudication, fail-closed build, source-links and screen reader/mobile proof | **DRAFT / HOLD** | Preparedness / independent QA |
| Grok/Praxxis asset → guide landing | TASK-008 does not yet identify a verified Preparedness asset ID, post URL or approved destination | Coordinate asset_id/UTM, check bio-link routing, 360/390/768/1440 viewports; never own posting | **UNVERIFIED** | Grok / Praxxis |
| Free guide → optional free printable | Printable accessibility, privacy, and offline local-data handling unverified | Check print/digital form flow, no sensitive contact data sent to FV without consent | **NOT TESTED** | Site QA |
| Paid order → realized net | No reconciled orders or qualified-human denominator | 7/30-day reconciliation: UTM asset → landing → CTA → lead where applicable → merchant confirmed paid order → refunds/fees → net | **N/A** | Growth / Claude |

**Primary KPI:** net realized revenue per 1,000 qualified human sessions, reported only when numerator, denominator, provenance and merchant confirmation exist. A CTA click, lead, checkout start, platform view or affiliate outbound link is **not** a sale. Missing merchant evidence means N/A, not zero or conversion success. No extra analytics script.

## Execution and release limitations

Local Python `unittest` ran **72/72 synthetic adversarial and 35-slug coverage tests PASS** on the R134 generator's exact committed source and test blob identities; Python compilation PASS. The test harness uses an explicitly synthetic local R133 stand-in *only when the trusted R133 module is unavailable*, and a full packet cannot pass without **real R133 custody**. No actual full-repo native Python `validate.py`, `build.py`, R133/R134 complete 35-article execution, full regression suite, browser QA or mandatory integrity CI can be claimed. The model sandbox has no mounted repository and direct `git` network DNS fails; connected GitHub reads still enabled actual independent blob/citation checks. Do not mark QD PASS or clinical/technical safety.

**Status:** DRAFT / HOLD — no merge, WordPress/CMS write, publication, navigation, analytics, email, merchant, social posting, spending, or affiliate activation.
