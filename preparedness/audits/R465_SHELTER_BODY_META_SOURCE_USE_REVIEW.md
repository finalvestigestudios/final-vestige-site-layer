# R465 Shelter original–candidate body/metadata evidence (DRAFT · HARD HOLD)

**Observed:** 2026-11-18 PT. **Issue:** #136. **Conversion charter:** #818 / #820. **Base:** R464 draft PR #3025 at `83f79c13b641428dcc6828f2a4f073f18fe84303`. All checks are read-only, no winner selected. No QD, medical, child-privacy, fire, evacuation, generator or emergency-safety approval is inferred.

## 16 authentic source witnesses inspected

The GitHub connector fetched all four article HTML bodies AND their original metadata JSON from original Shelter commit `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, continuation `ac8625faf30dd5538fadc31e06cb5a2cea1defae`, followup `6a5998ead97eca997e573ce8d3ceacf1c6aabad4` and integrated candidate `b36f3134c66131acc2dad8af25d541e6dcbc3d15`. Each returned body Git blob matched the existing R464 frozen body pin; each metadata Git blob was pinned anew in `R465_SHELTER_META_PINS.json`.

| Article | Original source-use IDs | Continuation | Followup | Candidate | Candidate added since original |
|---|---:|---:|---:|---:|---|
| Family communication (Article 15) | 14 | 18 | 20 | 20 | 6 |
| Home fire escape (Article 13) | 10 | 13 | 13 | 13 | 3 |
| Generator/outage safety (Article 12) | 16 | 18 | 19 | 19 | 3 |
| Shelter vs evacuation (Article 14) | 13 | 14 | 15 | 15 | 2 |
| **Total source-use memberships** | **53** | **63** | **67** | **67** | **14** |

All **16/16 original body/metadata pairs** had matching sets of actual literal `{{cite:source-id}}` citations and authored `source_use` identities; no missing or uncited source IDs were observed. All 16 retained `status.publish=draft`, `safety_review.state=pending`, null safety reviewer and date. Across all four articles, the candidate preserves the *verbatim reading scopes* of the preceding three versions for every retained source ID. The followup and candidate have the same source-use ID sets and reading-scope strings, even where their full HTML Git blobs differ. This is **source custody, not a claim-support verdict or a qualified safety finding**.

Literal citation occurrence counts, original → continuation → followup → candidate: family **62→67→69→69**; fire **70→73→73→73**; generators **116→120→121→121**; shelter/evacuation **50→58→59→59**. Candidate total **322** literal citation occurrences, which is not equivalent to 67 distinct source-use memberships. Original-to-candidate source membership increases do not independently prove quality or safety.

## New engineering

- `tools/r465_shelter_source_use_pair.py` verifies the paired Git-blob identities, authentic article identity/number, exact citation-to-source-use bijection, all pending/draft safety states, duplicate JSON keys, and preservation of every older source ID and its full authored reading scope. **16 file-pairs / 12 version comparisons**, no auto merge, no winner or QD PASS.
- `audits/R465_SHELTER_META_PINS.json` freezes 16 metadata blobs against R464's original commit refs.
- `tests/test_r465_shelter_source_use_pair.py` contains **341** deterministic synthetic tests, including regenerated-pin attacks that still must fail on unsafe metadata and 256 evidence mutations.
- Python compilation and **341/341** isolated R465 tests passed locally. Combined isolated `test_r46*.py` regression: **676/676** PASS, using locally saved source copies whose new Git blob hashes matched the exact committed R465 files.
- Native R465 CLI returned expected exit **2/HARD HOLD** because the original 16 article/version bytes and complete authenticated checkout are not mounted in the local runtime. Authentic `validate.py`, `build.py` and dual WP/private exports: **NOT EXECUTED/NOT VERIFIED**. GitHub source inspection is not a native builder run.

## Source and ownership coordination

Seven original Claude heads and both Shelter descendants checked against pinned exact current Git refs: **9/9 match**. Independent QA PR #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and synthetic fixture PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` remain draft/unmerged. Dependent repair #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a`, independent Article #11 editorial #2789 HEAD `977f45001cc6fcb2a97c479faad7f74b3caa8603`, and Apollo/home lead #3027 HEAD `4b8198491daaf792d8fdba22e6d3d1924d6dedd2` were inspected and not edited.

Original disputed source semantics (5), unselected manuscript forks (9), 17 article version divergences and 32 current shared-URL reading-scope groups remain independently unresolved. **No currently payable, rights-cleared Preparedness-owned toolkit or matching published Grok family-contact asset ID has been authenticated**; no new paid CTA or sale is claimed. The free Archive must remain ungated. Preserve Grok/Praxxis TASK-008 ownership and never use retired water offers.

## Release posture and required next evidence

**DRAFT / HARD HOLD** until a reviewer runs the native 35-article validation/build, source crosswalk, 16-pair R465 gate and authentic dual exports, followed by qualified human safety/source/QD review and founder release authorization. No public publication, CMS/navigation write, affiliate/merchant activation, social post, email, spending, offer-state mutation, tracking-script deployment or net-revenue claim was made.
