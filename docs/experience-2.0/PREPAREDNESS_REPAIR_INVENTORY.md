# Preparedness custody repair: measured inventory (2026-11-03)

Authorized by the PR #584 follow-up review (comment 6594203784): *prepare* a repair branch; no merge, no publication, #584 stays frozen at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.

**Branch:** `integration/preparedness-custody-repair-20261103`, head `5ca6b73bc95ff5f09739f581560069fba197e4da` (work in progress, HOLD). One commit on the frozen head: a 24-line insertion declaring the `shelter` origin as the third reading of `fsis-power-failure` in `sources/crosswalk.json`. A JSON round trip reproduced the file byte for byte before the edit, so nothing else changed.

## What the single fix revealed

The loader crash (`duplicate source id 'fsis-power-failure' is not documented in source crosswalk`) had been hiding the integrated candidate's real validation state. With it fixed, `python -I preparedness/tools/validate.py` runs to the end and reports **72 errors and 1 warning**:

| Class | Count | What it means |
|---|---:|---|
| `freeze:` evidence-lock drift | 59 | `article-evidence-lock.json` and the raw-source counts describe an older tree. 15 articles differ in body and/or metadata bytes (family-communication-plan, go-bags, home-fire-escape-plan, household-emergency-plan, making-water-safer, navigation-before-gps, outage-heat-cold-generators, pickling-fermentation-old-recipes, pioneer-supply-chains-failed, preparedness-real-households, root-cellars-cool-storage, salt-beef-salt-pork-age-of-sail, sanitation-before-germ-theory, shelter-or-evacuate, three-day-kit). Four source fragments differ in bytes and row count (hist-field, hist-home, shelter, start). The article inventory and the tool count differ from the 35-article baseline, and some body or metadata inputs are unpaired. |
| Sources never checked | 5 | `shelter-fcc-comms`, `shelter-fema-power-outage-sheet`, `shelter-nfpa-escape`, `start-ready-plan`, `start-ready-supply-list`: cited by articles but not checked by their own cluster or the base archive. |
| `register:` crosswalk | 8 | The integration now has **244 raw source rows against the crosswalk's 224 baseline**. Two URLs are duplicated with no crosswalk entry (the FSIS "keep your food safe during emergencies" page and `weather.gov/safety/winter-during`), and two entries have changed scope, metadata or verification (the LOC Prairie Traveler contents record and the CDC power-outage page). |

The warning (30 duplicate-URL groups have not received human source-scope review) is by design and remains.

## Why a merge was not the right tool

The integration branch holds each contributor cluster as **copied blobs**; none of the pinned contributor commits is an ancestor of it (checked), and every live contributor head's merge base is the base branch. A `git merge` would conflict on every cluster file. The right operation is a blob-level re-pin after review, which is what the R14 manifest asserts ("SHA-1 Git blob equality ... not commit ancestry").

## Where each cleared cluster actually stands

| Cluster | Integration tree vs reviewed live head |
|---|---|
| food `f911ff7a65` | already equal on all 10 scoped paths; only the manifest pin is stale |
| health `d5ef5bafd6` | already equal on all 8 scoped paths; only the manifest pin is stale |
| hist-home `7504a5f099` | equal on 10 of 12; two article bodies differ (the line-ending pattern seen earlier) |
| hist-field `5c807fbf45` (corrected) | all 5 changed paths differ: the integration carries a third version, neither the old pin nor the live head. This matches the R60/R61 "two-version contributor lineage" gates and must not be overwritten blindly |
| hist-food `67e116e536` | held per the review (needs the three `nchfp-jerky` readings declared and merged-test isolation checked) |

## There is no generator for the crosswalk

`crosswalk.json` is consumed by `build.py`, `source_crosswalk_truth_gate.py`, `source_group_review_gate.py` (which hard-codes its git blob SHA, `1d907264...`), `citation_fallback_review_gate.py` (which hashes it) and others, but nothing in the repository produces it. It is hand-maintained evidence. So "regenerate through the governed tooling" means a new, reviewed re-freeze through each gate's pinned constants, not running one script. Gates with pinned constants or expected counters (`source_group_review_gate.py`, `citation_fallback_review_gate.py`, the R14 manifest, `article-evidence-lock.json`, the R23 81-file archive freeze, and the claim-occurrence counts) all move together.

## What is mechanical and what needs a person

Mechanical once the intent is fixed: declaring variants from exact source rows (done for `shelter`); re-pinning the manifest for food, health and (after the line-ending question) hist-home; regenerating the evidence lock with `evidence_freeze.py` for the changed articles and fragments; updating counters.

Needs human judgement and cannot be inferred: the 20 additional source rows and their reading scopes (new duplicate-URL groups); the two crosswalk entries whose scope or verification changed (which reading is which); whether the five unchecked sources should be verified or their citations removed; how the integration's third hist-field version relates to the corrected live head; the hist-home body line endings; and, throughout, the human source-scope review of the 30 duplicate groups and the qualified safety review, neither of which exists.

## Recommendation

Do not attempt the whole re-freeze as a single patch. Proceed in reviewable stages, each a new exact head: (1) crosswalk completeness (the 20 rows and the two changed entries) with the five unchecked sources decided; (2) the contributor re-pin per cluster, starting with the two that already match (food, health); (3) the evidence lock and R-gate constants; (4) the full fail-closed preflight at the exact head. Nothing here moves any article toward publication; `safety_review` stays pending and `may_publish` false.
