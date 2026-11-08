# R210 — Start Here safety-intent carry-forward and independent QA reconciliation (Issue #136)

**Observed 2026-11-08 UTC.** **DRAFT / HARD HOLD.** Read-only inspections plus isolated regression code. No original article, taxonomy, source register, URL, CMS record, payment flow, shared social task queue, or public page changed.

## Exact contributor identity checks

Seven active Claude article-cluster heads matched the R209 frozen custody manifest:

| Cluster | SHA |
|---|---|
| Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent draft QA PRs: [#157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) (Start Here), [#169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) (source fixture isolation), [#973](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/973) (stacked follow-up). These were read at their existing frozen heads. **Do not apply older PR head files onto the newer contributor branches.**

## Exact five-file QA #157 carry-forward decisions

| Current Start Here blob SHA | QA #157 target | Independently observed in the newer authored file | Disposition |
|---|---|---|---|
| `8ca5c261dba56eeaf79c445332381a74867233de` | Household Emergency Plan, power-drill sentence | **Already contains** simulated-outage instead of a deliberate main-breaker shutdown; names refrigeration, smoke/CO alarms and medical/safety equipment. The old `switch off the main power` text is absent. 57 citation occurrences in observed body. | Preserve newer authored text; named human reviewer required. |
| `ef5463ca668166766ca3d868908bc0bcb6040a23` | Three-Day Kit, refrigerated medicines | **Already contains** FEMA December 2023 discussion, prescriber/pharmacist consultation, interim-use/replacement planning, Ready.gov citation. 75 citation occurrences. Older blanket discarding text absent. | Preserve newer authored text; qualified medication review still required. |
| `29574c328cbab0548e6e5d4a026694857d56b6b4` | start.json Red Cross publisher kind | `start-redcross-older-adults` already `kind=nonprofit`, explicitly not a regulator. | Preserve newer provenance; source still needs editorial review. |
| `eea601e53e16e36cd4fc890876bc249b39632370` | taxonomy Start Here safety gates | Exactly 35 slated items; all four relevant Start Here slugs (`household-emergency-plan`, `three-day-kit`, `go-bags`, `preparedness-real-households`) have `gate=true`, `status=not-started`. | Preserve current flags; no publication authorization. |
| `dd1e7bc35cc83da6174c56464583cbbadfd6751f` | test_preparedness.py | QA #157's negative human-safety-review test is NOT present; existing original tests include writes to shared-tree temporary fragments. | Test carry-forward and #169/#973 isolation are **open**; do not cherry-pick stale tests. |

This is an **intent-level comparison**, not proof the article is safe or the older QA PR is redundant. PR #157 remains draft. The new R210 gate guards all five expected Git blob SHAs; it refuses missing, substituted or symlinked files, duplicate JSON keys, changed four-article safety gates, resurrected unsafe phrases, removed critical caveats or changed source classification. It does not edit a source file. On a trusted copy of the *current* Start Here contributor checkout:

```bash
python -I preparedness/tools/r210_start_qa_semantic_carryforward.py --checkout /path/to/trusted/claude-start-checkout --report /tmp/r210-carryforward.json
python -I -m unittest discover -s preparedness/tests -p 'test_r210_start_qa_semantic_carryforward.py' -v
```

The CLI deliberately exits **2 for DRAFT_HARD_HOLD**, **3 for invalid**; never exits with a release PASS. The test-only `expected_oids` override is not accessible through CLI.

## Execution and evidence boundaries

- **BUILT:** Two added Python files under `preparedness/`; one documentation record and a static observation receipt. No old article files modified.
- **TESTED:** Python compilation and **66/66 isolated unittest cases PASS**. Cases include 35 independently named article-position mutation tests, extra 35 subtests, four critical-gate state mutations, source-destination checks, stale unsafe wording checks and symlink rejection. Exact committed code/test blob SHA comparison recorded.
- **AUTHENTIC GITHUB READ-ONLY STATIC INSPECTION:** All five current original Start Here files fetched from connected GitHub; original content markers and Git blob identities checked. This is not execution of the Python gate against a complete original Start Here checkout.
- **NOT TESTED:** Full project `validate.py`, `build.py`, original suite, authentic all-35 citation/source adjudication, or 41 WordPress exports. This container's Git DNS lookup of `github.com` failed; independent QD and medically qualified review remain outstanding.
- **REMAINING CITATION BLOCKERS:** Article #7 has two `cdc-find-clean-water` occurrences without article-level explanations; Article #20 has one `start-ready-plan` occurrence without an explanation. Seven historical shared-source conflicts remain. No automatic adjudication or reclassification.
- **SAFETY STATUS:** Neither matching phrases nor passing synthetic tests mean a source claim or health/food/water/electrical practice is safe.

## Conversion-priority mapping (#820; #818)

**One preliminary audience/offer:** adults who want trusted household contingency planning *and* an organized record locator for dependents. Do **not** frame a legacy/end-of-life workbook as a lifesaving emergency guide; the latter is a meaningful audience-intent mismatch.

**High-intent social topic, research-only to Grok/Praxxis TASK-008:** “Can someone in your household find your contacts, insurance and important records when you cannot?” The authentic **LIVE** free destination is [Preparedness Archive](https://finalvestige.com/preparedness/) → its linked official FEMA household-planning resource. Original FV 35-article guides and the Family Reunification Card remain unpublished / pending review. No retired water freebies.

**Optional clearly labeled commercial hypothesis:** [Legacy Triage public Payhip listing](https://payhip.com/b/n1RhV) advertises a $19 / ~580KB print-ready PDF as an instant download; it describes household finances, document locations, people to call and legacy instructions. It is a *different, optional organizational product*, **not** official emergency guidance or a verified transaction. Seller ownership/rights, actual successful checkout, delivery, refunds, mobile accessibility and practical-fit acceptance still unverified. No paid CTA activation.

**DRAFT ONLY on-site CTA, not deployed:** “Make a household plan with the free official resources above. If you also want to organize financial contacts and document locations for someone stepping in, Legacy Triage is a separate $19 printable organizer. It is optional and not emergency, legal or medical advice. [View product details — not enabled until verified]”. Keep urgent safety instructions free and outside purchase/email gates.

| Offer → funnel step | Blocker | Proposed check/change | Evidence now | Owner |
|---|---|---|---|---|
| Free official resource → useful planning | Original long-form guides unreviewed | Keep live official-source links; independently verify destinations | Public archive observed LIVE; original guides HOLD | Preparedness + independent QA |
| Grok content → authentic archive | No confirmed posted Preparedness `asset_id`, post URL, intended destination in reviewed TASK-008 | Record immutable Grok `asset_id`, posted URL, exact destination / UTM content and permission before campaign | NOT VERIFIED | Grok / Praxxis |
| Free plan → optional PDF details | Legacy/intention mismatch and disclosure uncertainty | Test reader clarity, FTC/commercial labeling and mobile CTA; never gate free guidance | DRAFT ONLY | Preparedness + Commerce / QA |
| Product details → paid order → delivery | Seller rights, Payhip acceptance, real checkout/fulfillment and refund terms not verified | Founder/Commerce verify merchant account, signed-off offer, staging or authorized controlled purchase and delivered document | HARD HOLD (public listing is **not** order) | Founder / Commerce |
| Sessions → clicks → leads → verified orders → realized net | Qualified-human sessions, consent, merchant orders, fees and refunds missing | Reconcile asset_id/UTM to 7/30-day merchant-confirmed cohorts without duplicate scripts; compute net / 1,000 qualified sessions only with denominator | NOT COMPUTABLE | Analytics / Commerce |

**Acceptance test before any release:** valid public free resource on 360/390/768/1440 px; accessible links and descriptive CTA; no affiliate opacity or false urgency; full source provenance; checkout terms, taxes/refunds and post-payment PDF delivery verified under merchant authorization; correct attribution labels (click ≠ sale); no collection of sensitive household data on FV pages. Grok controls media/posts; Claude controls core website production; founder authorizes production/commercial release.

**All changes remain isolated in a draft PR; no merge/publishing, nav/CMS, email, merchant, analytics, social or spending actions.**
