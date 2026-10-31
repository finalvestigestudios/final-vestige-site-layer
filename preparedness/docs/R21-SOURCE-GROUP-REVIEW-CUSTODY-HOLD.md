# Preparedness R21 — 30-group source evidence custody (DRAFT / HOLD)

Issue: #136. Base: R20 draft PR #305 at `b88ff46aefc178c51aa862fa842b7f810060fba6`. This change does **not** merge PRs, approve sources, publish content, touch WordPress, alter navigation, or rewrite any article.

## Deliverable

`preparedness/tools/source_group_review_gate.py` reads the current source crosswalk, taxonomy, register and seven contributor fragment JSON files. Its output is a sorted, deterministic, SHA-256-bound **human review queue**, not a publication approval.

The validator checks:
- 35 distinct article slugs and the gated water-planner record;
- 8 exact source file paths and Git blob identities, including original source reading notes and `supports` explanations;
- 224 physical source records, 186 URLs, 30 shared-URL groups, and 15 multiply used source IDs;
- each of the 30 crosswalk groups' source variants and origin / source-ID / row-index identities against the eight original physical source inventories;
- `pending-human-source-and-reading-scope-review` state, with no reviewer/date fabricated;
- the previously identified food provenance discrepancy between fixture PR #169's commit `e9cd7766dac59d47ab467d8945269b9146c2aef5` and actual contributor commit `4b009361277ea1d4617b368f5d45104c7318b284`. The discrepancy remains flagged rather than silently corrected.

Any missing source, changed citation-context description, alternate destination, altered provenance path, changed review state or duplicate/missing URL triggers a fail-closed exception. Even a valid machine receipt always says `HOLD`, `may_publish=false`, `independent_qd_pass=false` and `medical_safety_approved=false`.

## Verification

Local synthetic / adversarial tests: **52 passed** in `preparedness/tests/test_source_group_review_gate.py`. An additional 63 locally staged R20-only tests passed; **115 total available local tests passed**, but the R20 source/test modules have not yet been committed and cannot be counted as repository-integrated tests.

An independent authenticated GitHub read of the **exact R21 commit** examined all eight live source inventory files, compared their Git blob IDs with the crosswalk and checked all 30 source-variant/identity groups: **224 rows, 186 URLs, 30 duplicate-URL groups, 15 duplicate-ID groups; zero source crosswalk discrepancies observed**. This is a remote read and cannot replace a trusted-checkout Python execution.

Run when a trusted checkout is available:

```bash
python -m unittest discover -s preparedness/tests -p 'test_source_group_review_gate.py' -v
python preparedness/tools/source_group_review_gate.py --root preparedness > /tmp/preparedness-r21-source-review-queue.json
# The queue is a HOLD receipt for private review. Never publish it or treat it as approval.
```

## Coordination / noninterference

At this run, seven contributor branch HEADs matched their frozen values:
`start 2122d856`, `shelter 5daeaf2d`, `food 4b009361`, `health d2212d0c`, `hist-food 2acf65ca`, `hist-home f654e600`, `hist-field a5ce8a62`.

Independent QA PR #157 remains a draft at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and is based on older article versions. Synthetic-fixture PR #169 remains a draft at `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Neither was merged. Homepage PR #49 was read at `10495883299d53596992c26a8987f629b2904670`; flagship PR #254 was read at `8fa6fc52e034f511b96ae526f4a852e1bd76db04`. Neither is within scope.

## Unresolved blockers — RELEASE HOLD

Local git access to the private repository fails DNS resolution (`Could not resolve host: github.com`). GitHub Actions run `41200742724` failed with `runner_id=0`; the 11-gate R18 full checkout validation and WordPress draft build have not executed. R21's real-corpus Python CLI has **not** run in a trusted checkout.

All **30 shared-source groups still need qualified human reading-scope reconciliation**; the original 1,959 citation occurrences need independent claim/link validation. Consequential emergency/medical advice remains unreviewed; qualified safety signoff and independent QD are outstanding. No source group is approved by this gate.

**No WordPress/CMS writes, no live publishing, no release changes.**
