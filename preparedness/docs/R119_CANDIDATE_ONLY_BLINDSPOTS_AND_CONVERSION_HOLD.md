# R119 — Release-candidate-only evidence blindspot: complete 35-route reviewer matrix (HOLD)

**2026-11-04 | Owner:** Preparedness Archive integration, Issue #136; cross-reference #820 and charter #818.  
**Status:** engineering draft; **no safety approval, QD PASS, production publish, merge, or merchant revenue verified**.

## Material finding

R118 and R117 reconcile contributor-changed paths. The release candidate also changes files where no current Claude cluster contributor changes that exact path versus the frozen original. Consequently **R118's 18-path review inventory omitted 17 release-candidate-only files**. This is a review-worklist coverage gap, not evidence that the original author or release candidate is factually incorrect.

Nine exact Git refs were independently checked on 2026-11-04. All seven Claude cluster SHAs, RC SHA and R118 SHA remain unchanged. Deterministic comparison of R117's immutable snapshot and workorder inputs shows:

| Measure | Exact count |
|---|---:|
| Original body + metadata pairs | 35 |
| Candidate-changed original article paths | 24 |
| Candidate-changed source fragment paths | 4 |
| All candidate-changed protected paths | 28 |
| Contributor-changed observations | 24 |
| Contributor-changed unique paths | 18 |
| Both candidate + contributor changed | 11 |
| Candidate-only changed (missed by R118 review list) | **17** |
| Contributor-only changed | 7 |
| **Complete human review path union** | **35** |

Every review decision remains UNREVIEWED. The new `r119_complete_delta_crosswalk_gate.py` derives candidate-only and contributor-only paths directly from R117 evidence instead of trusting an editor-supplied list. It verifies the original 35 paired routes, rejects a changed release-candidate source fragment roster, checks workorders against actual contributor blob changes, preserves nine original/current head references, and verifies a submitted matrix byte-for-byte via `--verify-crosswalk`.

## 17 candidate-only paths that require **new** review workorders

Abbreviated Git blob IDs are display conveniences; the full immutable IDs remain inside R117's authoritative JSON inputs.

| # | Protected path | Original blob | RC blob | Triage | Disposition |
|---:|---|---|---|---|---|
| 1 | `preparedness/content/articles/family-communication-plan.body.html` | `16e2b1ec37fd…` | `8ac8bd7dba3b…` | P1 | UNREVIEWED |
| 2 | `preparedness/content/articles/family-communication-plan.meta.json` | `e63bbe70f5b9…` | `dcad79faa8e0…` | P0 | UNREVIEWED |
| 3 | `preparedness/content/articles/go-bags.body.html` | `5135639786bb…` | `e5910015fc6e…` | P0 | UNREVIEWED |
| 4 | `preparedness/content/articles/home-fire-escape-plan.body.html` | `ba869874b5ee…` | `0412484304a3…` | P0 | UNREVIEWED |
| 5 | `preparedness/content/articles/home-fire-escape-plan.meta.json` | `6a54547ef145…` | `ff1246dcbfb0…` | P0 | UNREVIEWED |
| 6 | `preparedness/content/articles/household-emergency-plan.body.html` | `8ca5c261dba5…` | `f81cd43516e8…` | P0 | UNREVIEWED |
| 7 | `preparedness/content/articles/making-water-safer.meta.json` | `bcb567905444…` | `827d861eb3be…` | P0 | UNREVIEWED |
| 8 | `preparedness/content/articles/outage-heat-cold-generators.body.html` | `47d949d97ddb…` | `2cd3e30b3a7e…` | P0 | UNREVIEWED |
| 9 | `preparedness/content/articles/outage-heat-cold-generators.meta.json` | `77dd194b096b…` | `be37b602d0b8…` | P0 | UNREVIEWED |
| 10 | `preparedness/content/articles/preparedness-real-households.body.html` | `70d03c366e10…` | `68344cf6c402…` | P1 | UNREVIEWED |
| 11 | `preparedness/content/articles/salt-beef-salt-pork-age-of-sail.meta.json` | `06b1cec809cb…` | `1c4c5396da70…` | P0 | UNREVIEWED |
| 12 | `preparedness/content/articles/shelter-or-evacuate.body.html` | `b8acf07e533e…` | `de3cb8050419…` | P0 | UNREVIEWED |
| 13 | `preparedness/content/articles/shelter-or-evacuate.meta.json` | `fe90c9ef50e2…` | `cb559141d1e4…` | P0 | UNREVIEWED |
| 14 | `preparedness/content/articles/three-day-kit.body.html` | `ef5463ca6681…` | `933f38ff3cd5…` | P0 | UNREVIEWED |
| 15 | `preparedness/content/articles/three-day-kit.meta.json` | `c830e4b8b0ee…` | `1c69d5f1636a…` | P0 | UNREVIEWED |
| 16 | `preparedness/sources/fragments/shelter.json` | `d9eeb4546e58…` | `2a3f1a7ddeab…` | P0 | UNREVIEWED |
| 17 | `preparedness/sources/fragments/start.json` | `29574c328cba…` | `96140d6d1872…` | P0 | UNREVIEWED |

**Immediate P0:** reconcile `household-emergency-plan.body.html`, `three-day-kit.body.html`, `home-fire-escape-plan.body.html`, other actionable safety guidance and `start.json`/`shelter.json` with author-specific source-use, warning/caveat preservation, qualified emergency guidance review, and source citation scope. R118's 18 contributor-path rows also remain UNREVIEWED. No automatic cherry-pick or citation ID migration.

## Independent QA, historical source and ownership coordination

* Safety QA #157 remains draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. It specifically replaces a dangerous main-breaker practice drill. Current RC `household-emergency-plan.body.html` at `f81cd43516e8295104230412f18776919148f905` **also** explicitly says not to switch off the main breaker; text differs from #157, so qualified QA must compare wording instead of claiming #157 was automatically incorporated.
* Fixture PR #169 remains draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`: its `test_register_fragments_cannot_duplicate_ids` still targets a shared `sources/fragments/_dup_test.json`. Keep fixture isolation in that PR owner's lane, not this branch.
* Release candidate #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706` remains HOLD. Homepage PR #49 `10495883299d53596992c26a8987f629b2904670` and #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` were checked, not edited.
* Seven contributor SHAs: `food=f911ff7a655de8d81535ea86ec3d65a49ee76648`; `health=d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; `historical-field=4e5caf812727953aa45e3bda2d382f2c67b6a09c`; `historical-food=67e116e536c7410bed30f8f3b1bb8c166f3c223d`; `historical-home=7504a5f099594d635e3dd7332a33a2e1346c43a2`; `shelter=5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; `start-here=2122d856fce9f64887c16df3d52e64be9f59a55b`.
* Other tracked release blockers: 30 shared source URL groups, 15 safety exceptions, 22 editorial decisions, five incomplete tools, qualified safety review, browser QA, mandatory integrity, independent QD. These figures are carried forward as historical *unresolved* totals, not freshly recomputed in this round.

## Reproducible nonproduction commands

```bash
python -I preparedness/tools/r119_complete_delta_crosswalk_gate.py --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json --workorders preparedness/docs/R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json > /tmp/fv-r119-full-crosswalk-HOLD.json
python -I preparedness/tools/r119_complete_delta_crosswalk_gate.py --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json --workorders preparedness/docs/R117_SEVEN_BRANCH_SOURCE_CITATION_DIFF_WORKORDERS_HOLD.json --verify-crosswalk /tmp/fv-r119-full-crosswalk-HOLD.json
python -I -m unittest discover -s preparedness/tests -p 'test_r119_*.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The last four commands **have not yet passed on this exact head**; workflow execution or a complete clean checkout is required. Git blob equality alone does not verify advice, article completeness, web appearance, clinical suitability, live status, or revenue.

## ONE conversion-first, nonpublic, unpaid campaign acceptance pathway

**Intent:** a household wants an emergency contact/reunification plan.  
**Guide:** existing source-linked **A Household Emergency Plan That Actually Gets Practiced** (authentic free guide; source and qualified safety reviews **HOLD**).  
**Optional paid product:** none added until an *existing* FV-owned Preparedness pack is independently verified as rights-cleared, actually purchasable, sufficiently relevant, deliverable, priced and correctly described. Retired water freebies excluded.

**Draft ungated CTA:** “Make a plan your household can actually use. Read the free, source-linked emergency planning guide.” Keep all current safety instructions accessible without signup.

| OFFER → STEP | BLOCKER | CHANGE / ACCEPTANCE EXPERIMENT | EVIDENCE / RESULT | OWNER |
|---|---|---|---|---|
| Existing owned pack → verified paid order | No seller-verified Preparedness SKU, product rights/price/file delivery/refund evidence | Inspect seller-origin SKU and stage checkout/delivery tests only with permitted access | NOT VERIFIED / NO PAID CTA | Growth / Claude |
| Guide → visitor trust | Candidate-only and contributor source/safety differences remain | Complete 35-path human crosswalk, source URL adjudication, independent safety assessment | HOLD | Preparedness + independent QA |
| Grok creator asset → guide | TASK-008 has no verified matching Preparedness asset_id/post URL | Use existing Grok/Praxxis inventory; accept unique `asset_id`, intended destination, and policy-compliant platform link mapping before any campaign URL | NOT VERIFIED | Grok / Praxxis |
| Landing CTA → optional pack | Guide not live; product unverified, mobile/keyboard and disclosure tests not run | For eventual stage: 360/390/768/1440 widths, accessible CTA, clear optional price/terms, real merchant checkout/delivery; no email gate on safety advice | NOT TESTED | Claude / Site QA |
| Source-verified net revenue | No first-party qualified-human sessions and no independently confirmed merchant orders/refunds/fees | Use existing privacy-compliant measurement; 7/30-day tiny-sample-aware cohorts; compute net revenue/1,000 qualified sessions only with both denominators | N/A | Growth / Claude |

No permission to modify Grok queue, TASK-008 Drive, public WordPress, navigation, analytics tags, mailing, affiliate settings or Payhip.
