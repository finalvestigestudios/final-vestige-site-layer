# R7: immutable corpus/source custody inspection — DRAFT/HOLD

**Exact source HEAD:** `903e2ce817659bf3d4e5cf7fa44cdda2682a17aa`. On October 30, 2026, the GitHub connector fetched the recursive tree and independently retrieved all **eight source JSON files**. It matched every source record and contributor reading scope to the 30 independent source-collision groups; checked all **72 article/tool source paths against the original immutable evidence-lock SHA and bytes**; verified the current taxonomy contains 35 distinct matching article slugs; and confirmed no new untracked body/metadata files exist.

| Custody fact | Confirmed at source head |
|---|---:|
| Long-form articles / local tool | 35 / 1 |
| Frozen body + meta paths | 72 |
| Distinct contributor source rows | 224 |
| Source input files | 8 |
| Source URLs | 186 |
| Shared-URL groups, still unresolved | 30 |
| Human link checks marked in source files | 0 |
| Detected source crosswalk record discrepancies | 0 |
| Source custody errors | 0 |

The frozen content SHA check establishes **no article text or metadata file changed since the original evidence lock**, preserving pre-existing article depth and stored statuses. This did **not** reparse all 35 bodies to re-evaluate every citation placement and word count. See existing upstream source queue/validation tooling for those checks. No vendor claims, external emergency advice, human source page reads or medically qualified review are certified by this custody snapshot.

## Separate Python execution

The existing **206 synthetic review-module tests** in the local partial checkout were independently rerun with `python -I -m unittest discover -s tests -p 'test_*review*.py' -v` and **206 passed**. The entire private repository checkout was not available due GitHub DNS, so `preparedness/tools/validate.py`, `preparedness/tools/build.py` and the full integration suite were **not** run. The reports here must not be treated as a substitute.

## Source and safety scope

Every contributor's original source row is preserved, including repeated URLs with different inspected sections or contradictory wording. All 30 shared-URL groups remain **pending human source/reading-depth reconciliation**. The machine-fetched source file's `human_link_check` is false for all 224 physical rows. A machine `verified_on` date is **not** evidence of independent human verification.

The seven Claude cluster source heads remain separately tracked in the upstream crosswalk. Independent QA PR #157 and synthetic fixture PR #169 are not changed. Homepage lead's draft PR #212 and homepage release PR #49 are untouched. This PR adds only two audit report files to Preparedness docs; it does not edit content, review statuses, CMS, navigation or the live site.

**RELEASE HOLD:** exact-head full Python validation/build, real external primary-source checking, qualified safety assessment for water/food/medical/infant/fire/CO advice, 30 shared-source reconciliations, hosted CI, independent QD and founder authorization remain outstanding.
