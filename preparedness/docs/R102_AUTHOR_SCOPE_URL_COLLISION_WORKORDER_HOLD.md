# R102 — literal-URL collision / author-scoped citation workorder (PRIVATE HOLD)

**Issue #136. No merge, publish, import, CMS write, navigation change, fabricated review or QD PASS.** R102 is a mechanical evidence-custody review aid, **not a claim-by-claim fact check**. Any high-consequence water, food, shelter, medical or emergency guidance still needs qualified human review.

## Scope and provenance

This additive branch descends from frozen R101 head `e4e0fc4f6d1441893e020c12baddef542cdaf9f1` (the successful 8,623-test private baseline). The original 35 articles, one actual WordPress-ready tool draft, and the separately tracked five unbuilt tools remain distinct. No original article, fragment, source record, stylesheet, route, build output or release gate has been changed.

Original `preparedness/sources/crosswalk.json` contains **30 shared literal-URL groups**. A same-URL grouping is *not* a permission to merge author-specific reading scope, source title, supporting claim, historical edition, page range, verification date or human check. R102 independently recomputes the collision roster from **every raw source fragment**. It compares the full original source metadata per origin, checks identity rosters, then binds each original `{{cite:id}}` occurrence to its **article origin, selected origin-scoped record, original article-specific `source_use` description, citation ordinal, original article SHA-256 and bounded verbatim proximity excerpt**.

A proximity excerpt is for reviewer navigation only. It is **not proof** that the source supports the nearby statement; it may span more than one sentence or quote. Report fields explicitly label machine checks as machine checks, keep crosswalk review statuses pending, and mark human source/claim review, safety review, browser/WordPress QA and independent QD **NOT_REVIEWED**. The report is JSON-canonical and SHA-256 sealed. It does not modify source records or resolve collisions.

The source crosswalk's `source_head_commits` is a **historical integrated-source manifest**, not a representation of contributor branches' latest Git heads. Both must be tracked separately. As of this run the actual contributor heads read from GitHub were Start `2122d856fce9f64887c16df3d52e64be9f59a55b`, Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`, Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`, Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`, Hist Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`, Hist Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`, Hist Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`. Integrated RC: `ddb3528ba6494dada1fa1c3a142ce746e3a67706` (historical checkpoint; check current head before use). Independent QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; both open draft/unmerged. #169's patch upgrades one temporary fixture to a sandbox but retains a separate shared-tree fragment writer. Homepage #49 `10495883299d53596992c26a8987f629b2904670` and flagship #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` inspected read-only.

## Offline reviewer procedure — never import as an approved page

From a trusted exact-head checkout:

```sh
python -I preparedness/tools/r102_author_scoped_collision_workorder.py > /tmp/preparedness-r102-HOLD-workorder.json
python -I -m unittest discover -s preparedness/tests -p 'test_r102_*.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The first command prints a private workorder; preserve it internally only. For each shared URL, a human reviewer must read the actual identified document/edition/section and compare each **article-specific claim** and source-reading limitation; reconcile machine fetch versus actual human link check, historic source variants and revisions. Do not deduplicate records just because URLs match. Follow the existing crosswalk review/resolution contract with attributable reviewer, date, and scope notes **after** independent review, not through this script. Run the full contributor provenance and mandatory integrity gate before any release consideration; a separate successful Python diagnostic does not override mandatory failure.

## Known blockers preserved

Five historical contributor-provenance discrepancies; 30 unresolved URL collision groups; 15 safety exceptions; 22 editorial decisions; five missing tool drafts; independent human link/source/claim verification; qualified emergency safety/medical/food/water review; actual Chrome/Firefox/Safari print/offline/no-JS/accessibility testing of the R101 experimental planner; independent QD; and the failed mandatory 13-stage release integrity pipeline. No changes to any of those states are inferred by R102. WordPress-ready output remains **private drafts only**. No publication permission is requested.
