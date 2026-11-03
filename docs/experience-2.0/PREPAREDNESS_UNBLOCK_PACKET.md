# Preparedness release: exact blockers and the shortest legitimate path (2026-11-02)

Read-only analysis of PRs #584 and #668. **Nothing was changed on their branches, nothing was re-frozen, nothing was published.** The machine-integrity workflow reports only hashes (by design), so each cause below was reproduced locally by running the repository's own tools.

This corrects the earlier ledger note, which named only one cause. There are **two independent blockers**, plus the qualified-safety dependency.

## Blocker 1: #584 (integrated candidate) cannot even load its source library

`python -I preparedness/tools/validate.py` at `ddb3528ba6`:

```
ValueError: duplicate source id 'fsis-power-failure' is not documented in source crosswalk
```

`fsis-power-failure` (same URL) is defined in the base register, `fragments/food.json` (verified 2026-10-29) and `fragments/shelter.json` (verified 2026-11-01). The loader requires every redefinition of a verified source to be declared exactly in `sources/crosswalk.json`, which lists only `base` and `food`. The `shelter` text is substantively the same finding (about 4 hours refrigerator; about 48 hours full freezer, 24 if half full). Because this raises inside `build.Library()`, **every** later gate fails closed at `native_validation`.

On the R76 lineage (#668) `validate.py` **passes** (0 errors, 1 warning), because that lineage does not contain the shelter fragment.

## Blocker 2: the frozen seven-cluster parity manifest is stale (#668 fails at `seven_cluster_git_parity`)

Running `cluster_git_parity_gate.py` with the frozen manifest (`R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json`):

```
{"gate": "CLOSED", "error": "food: live contributor branch moved; re-review before integration"}
```

This is the gate working as designed: five of the seven author branches have advanced since the manifest pinned them, so it refuses until a human re-reviews what moved. All five are clean fast-forwards (the pinned commit is an ancestor); `start` and `shelter` have not moved.

| Cluster | Pinned | Live | Commits | Real change (end-of-line-only differences ignored) |
|---|---|---|---|---|
| food | `4b009361277e` | `f911ff7a655d` | 1 | tests and a docs note only; no article or source change |
| health | `d2212d0ca075` | `d5ef5bafd683` | 1 | one docs file (+17 lines) |
| hist-food | `2acf65ca3efa` | `67e116e536c7` | 1 | source id renamed `hist-food-nchfp-jerky` to `nchfp-jerky` (URL trailing slash dropped), two articles reference it (1 to 7 lines each), tests |
| hist-home | `f654e600f89c` | `7504a5f09959` | 2 | Simmons 1798 text read for pickling and root-cellar articles; Wellcome record for Chadwick's 1842 report added to sanitation-before-germ-theory; about 130 lines across 3 articles' bodies and metadata, 29 lines of source records |
| hist-field | `a5ce8a62f168` | `4e5caf812727` | 1 | Breen diary finding aid and Hastings guide added as primary sources; Marcy contents read in full; about 55 lines across 2 articles and the source fragment |

Many files show identical added and removed counts in a plain diff (for example 395/395); that is line-ending churn, not content. The real review is about 200 lines.

**Likely next failure:** the `nchfp-jerky` rename means the old id is now defined in the register, `food`, and `hist-food` under one id. That is the same class of undeclared-variant error as Blocker 1. This is an inference from the diff; it has not been run.

## What would legitimately clear these, in order

1. **A human or independent reviewer re-reads the five moves** above (about 200 semantic lines, mostly historical sourcing, none of it medical instruction) and records the decision per cluster. This is the review the gate demands; it was not done here and I will not self-approve it.
2. **Declare the new variants in `crosswalk.json`** (shelter for `fsis-power-failure`; the renamed `nchfp-jerky` as needed) using the owning workstream's procedure. This changes a custody-hashed evidence file (`citation_fallback_review_gate.py` hashes it; counters such as `raw_source_rows` 224 are asserted), so the dependent gates must be re-frozen in the same change, by that workstream. Do not hand-edit the counters.
3. **Re-pin the R14 manifest** to the reviewed heads and re-run `private_release_preflight.py` at the exact new head.
4. Only then do the remaining gates matter: qualified safety review, and the R76 consequential-citation review.

## Does the archive have anything publishable now?

No wave is cleared. `release_state: HOLD` and `may_publish: false` appear in the manifests; `qualified_emergency_safety_clearance` is false. Wave 1 (landing, Start Here, household plan) is the right first release once steps 1 to 3 pass and the Wave 1 pages carry no unreviewed safety instruction; it must not wait for Wave 2 or 3. The two water guides the founder approved earlier (#6 and #21) are the only items with a recorded approval, and that approval is a founder editorial sign-off, not the qualified safety review.

## Who can do this fastest

The re-review in step 1 is small and well-suited to the same independent reviewer (ChatGPT) that is reviewing the homepage: give it the five commit ranges above and ask for a per-cluster verdict. Steps 2 and 3 belong to the workstream that owns the crosswalk and the R-series gates.
