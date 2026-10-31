# R24 — Mandatory 81-file custody + full citation occurrence crosswalk

**Issue #136 · 2026-10-31 · DRAFT / RELEASE HOLD. No human link or medical/emergency safety approval, QD PASS, CMS write or publication.**

## Closed preflight gap

R23 introduced a native frozen **81-file** content/source custody gate, but the R18 private preflight and R19 exact-order receipt verifier still enumerated only **11** stages. A green preflight therefore could have skipped R23's original-body and source bytes check. R24 adds `frozen_81_file_archive_custody` as a mandatory **12th** stage invoking `source_group_review_gate.py` from the exact checkout; subprocess exit, literal HOLD result, step order, output fingerprint and Git worktree cleanliness all remain mandatory.

R24 also refuses a producer's contradictory `medical_safety_approved: true`, `independent_QD_approval: true`, `human_source_reviews_completed: true`, `wordpress_publishing_performed: true` or other known approval markers inside otherwise HOLD-shaped JSON. Any emitted authority marker must be exactly Boolean `false`; it cannot be `true`, `1`, `null`, or `"true"`.

## Independent real-repository citation/source-use read

At exact source HEAD `b62a7feaaca43be10ff9c58c025f84b557eed491`, authenticated GitHub reads covered all **35 article bodies and metadata pairs**, the water-planner body and metadata, and eight source inventories. Every `{{cite:source-id}}` token was checked against its author's own cluster inventory or the expressly allowed base-source fallback and against its article-specific `source_use` scope note. The selected record's existing machine `verified_on` field was examined. This is **structural citation binding**, not independent verification that the source page exists now, supports the adjacent assertion, or is clinically safe.

| Source cluster | Articles/tools | Citation occurrences | Distinct article/source-use pairs |
|---|---:|---:|---:|
| Base/water | 6 | 243 | 36 |
| Start Here | 4 | 268 | 65 |
| Shelter/power | 4 | 298 | 53 |
| Food | 4 | 282 | 46 |
| Historical food | 6 | 259 | 63 |
| Health/sanitation | 3 | 185 | 25 |
| Historical home | 5 | 246 | 46 |
| Historical field | 3 | 171 | 30 |
| Water-planner tool | 1 | 7 | 3 |
| **Total** | **36** | **1,959** | **367** |

**Observed structural mismatches: ZERO** missing source IDs, uncited source-use notes, citations without source-use notes, or cited source records lacking their existing machine verification date. **43 distinct article/source pairs** legitimately resolve to the original base register rather than the author's own cluster inventory: these are *additional human reading-depth review priorities*, not cross-cluster approval. Thirty shared-URL source groups still require human reconciliation.

### Per-item occurrence census (article text unchanged)

| Slug | Tokens | Slug | Tokens |
|---|---:|---|---:|
| `homemade-water-filters` | 51 | `making-water-safer` | 52 |
| `salt-beef-salt-pork-age-of-sail` | 49 | `two-week-water-storage` | 28 |
| `water-advisories-explained` | 30 | `water-math` | 33 |
| `go-bags` | 72 | `household-emergency-plan` | 57 |
| `preparedness-real-households` | 64 | `three-day-kit` | 75 |
| `family-communication-plan` | 62 | `home-fire-escape-plan` | 70 |
| `outage-heat-cold-generators` | 116 | `shelter-or-evacuate` | 50 |
| `food-safety-power-outage` | 69 | `pantry-rotation` | 68 |
| `pressure-canning-low-acid` | 74 | `safe-jerky-dehydration` | 71 |
| `history-of-food-preservation` | 47 | `lewis-and-clark-salt-works` | 49 |
| `pemmican-and-dried-meats` | 46 | `pioneer-travel-rations` | 39 |
| `ships-biscuit-and-hardtack` | 42 | `smokehouses-salting-curing` | 36 |
| `emergency-hygiene-sanitation` | 62 | `medication-and-devices` | 68 |
| `warnings-radios-offline-maps` | 55 | `pickling-fermentation-old-recipes` | 42 |
| `rain-barrels-and-cisterns` | 44 | `root-cellars-cool-storage` | 37 |
| `sanitation-before-germ-theory` | 47 | `water-purification-through-history` | 76 |
| `fire-making-across-time` | 67 | `navigation-before-gps` | 47 |
| `pioneer-supply-chains-failed` | 57 | `water-planner` | 7 |

## Source coordination and outstanding review

All seven original contributor branch SHAs were checked at this run: start `2122d856fce9f64887c16df3d52e64be9f59a55b`, shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, food `4b009361277ea1d4617b368f5d45104c7318b284`, health `d2212d0ca0750817d3929865d3069835980faf20`, hist-food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`, hist-home `f654e600f89c321a480dd8f055be4d13d0673490`, hist-field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`. All match frozen author heads.

Safety QA PR #157 (`7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) is a separate older draft whose text replacements are stale relative to the integrated safety copy. Synthetic-fixture PR #169 (`e9cd7766dac59d47ab467d8945269b9146c2aef5`) remains unmerged. Homepage PR #49 (`10495883299d53596992c26a8987f629b2904670`) and flagship PR #254 (`8fa6fc52e034f511b96ae526f4a852e1bd76db04`) are not touched.

**Limitations:** GitHub Actions has previously failed before runner allocation, and the private checkout is unavailable to the local execution environment. The native full-repository validation/build and full twelve-stage hosted preflight have **not** executed. The previously documented food-cluster provenance alias, one contributor metadata discrepancy, all 30 human shared-source reviews, source-link/claim verification, qualified safety review and independent QD approval are still unresolved. Structural source provenance does not constitute medical or emergency guidance approval.

**Release state: HOLD. May publish: false. WordPress/CMS/public/navigation writes: none.**
