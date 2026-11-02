# R66 — Original cited-source identity and unreviewed claim-citation ledger
**Issue #136 · PRIVATE / DRAFT / HOLD · 2026-11-02**

## Exact integration boundary

R66 stacks only on unmerged R65 draft PR #585, commit `b9f482c159accf1d00761d03ef5cc28399f44bd6`. No modification to any original article, water planner, research note, source fragment, safety metadata, frozen source custody, release controls, homepage, navigation or WordPress. Unlike an article-count-only gate, R66 processes **35 original cited articles and the separately cited water-planning tool**. The original token census is **1,959 exact citation occurrences = 1,952 article + 7 water-tool**.

Only cited original source identities are indexed by **exact (source_origin, source_id) pair**. Every identity retains its full unabridged original source reading, its exact URL as originally recorded, its full original citation contexts, all article/source relationship records, exact original R58 work-order hashes, offsets and original HTML SHA anchors. The R65 fingerprint anchors the full proposed-versus-frozen contributor records, including all 29 original contributor articles, six integrated-only articles and unreviewed proposed changes. **R66 does not purport to inventory uncited sources**; the original R57/R63 source records remain required and independently preserved.

### Safety-sensitive difference from superficial URL deduplication

A citation to the same URL from two distinct original source records **must not imply equivalent research evidence**. R66 only groups **identical recorded URL strings** for a HUMAN review queue. It retains every distinct full reading and source identity, never uses URL normalization to auto-match evidence, and never converts structural identity into claim support. A malformed URL remains on the queue with an explicit retrieval flag, not deleted. Shared URL groups, changed contributing article bodies, citations inside integrated-only articles, and the original water-tool sources are all visible, unresolved review signals.

The signed-by-a-hash report is a deterministic *machine fingerprint*, not an independent human signature. It does **not** establish that URLs resolve today, support any claim, or establish medical, food, generator, medication, potable water, or other emergency advice is safe.

## Reviewer workflow — private only

From a trusted full repository checkout with all seven exact contributor Git refs:

```sh
python -I preparedness/tools/r66_cited_source_identity_ledger.py
python -I preparedness/tools/r66_cited_source_identity_ledger.py --task-csv-stdout > /private/path/r66-cited-source-review.csv
python -I -m unittest discover -s preparedness/tests -p 'test_r66_cited_source_identity_ledger.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The CLI by default prints only a HOLD summary, with no writes or network requests. CSV mode is a **derived, untrusted, non-authoritative human-task projection** that prints to standard output; save only in a private reviewer workspace, not in public build artifacts. Cells starting with spreadsheet-formula prefixes are neutralized. Do not use reviewer CSV annotations as source truth, write them back into the archive, or mark their presence as safety clearance. The complete original notes/contexts are in the deterministic Python report, not shortened into spreadsheet cells. Never attach the full original evidence ledger to a public site or push it to WordPress.

The production entrypoint regenerates R65 using both historical R58 and independently verified R61/R64 Git-object evidence. Caller-supplied synthetic census values are for adversarial tests only and cannot change the production CLI's frozen (35,1,1959,1952,7) contract.

## Non-negotiable failure gates

A missing source, changed original reading under the same (origin,id), lost or reused citation identity, mismatched source/article relationship, missing context, modified source status, falsified QD/safety/link approval, corrupt original checksum, missing water-tool citation, or count drift fails closed.

An unreviewed source is not approved merely because the URL is a valid HTTPS URL. The original HTML/source/codepoint structural match is likewise **not proof of source support**. The integrated 35 plus tool are private drafts until qualified human review and independent QD have actually occurred. The separate mandatory 13-stage integrity pipeline remains **FAIL CLOSED** while advanced contributor branches diverge from frozen R14 provenance; no rebaseline or bypass is authorized.

## Current coordination snapshot

At inspection, all seven Claude original contributor branch heads were:

| Contributor | Exact Git HEAD SHA | Original frozen parity |
| --- | --- | --- |
| Start Here | `2122d856fce9f64887c16df3d52e64be9f59a55b` | unchanged |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | unchanged |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | advanced / HOLD |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | advanced / HOLD |
| Historical Food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | advanced / HOLD |
| Historical Home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | advanced / HOLD |
| Historical Field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | advanced / HOLD |

**Independent QD PR #157:** `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Its live patch was inspected: safety-critical household power-drill and refrigerated-medication prose, Red Cross nonprofit correction, stricter Start Here taxonomy, and related tests. It remains unmerged and **has not** been treated as independent QD approval.

**Independent fixture PR #169:** `e9cd7766dac59d47ab467d8945269b9146c2aef5`. Its live patch was inspected: food-source synthetic test isolation and no original source overwrite. It remains unmerged and does not relax citation checks.

**Homepage lead PR #49:** `10495883299d53596992c26a8987f629b2904670`. **Separate release candidate PR #584:** `ddb3528ba6494dada1fa1c3a142ce746e3a67706` includes unpublished article/tool and safety-register drafts on an R61 base; DO NOT merge, rebase, cherry-pick or authorize it from this lane. The RC's separately reported **244 source-link checks and 41 safety-register items** have a different inventory scope from the earlier **206 source-link check** baseline and R65's **35 + 1 cited-document ledger**; reconcile these **without claiming either number represents completed human review or equating their units**. This R66 ledger is an independent original-source identity audit, **not RC approval**.

### Outstanding human gates

Original source human-link checks (previous baseline 0/206; release-candidate workstream reports 0/244 across a different scope), 30 historical shared-URL groups, 43 fallback relationships, 15 open safety exceptions, changed five-contributor research custody, contextual claim-support review (especially consequential emergency advice), true WordPress/browser keyboard/print/screen-reader review, independent QD and founder release authorization remain outstanding.

**Release = HOLD.** Machine-only diagnostics cannot produce a QD PASS, publish publicly, create live site navigation, or validate unreviewed emergency/medical advice.