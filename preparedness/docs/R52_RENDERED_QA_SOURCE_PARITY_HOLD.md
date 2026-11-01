# Preparedness R52 — frozen R48 rendered QA evidence reconciled with R51 source custody

**Issue #136 · PRIVATE / UNVERIFIED / RELEASE HOLD · no public or WordPress writes**

## Change boundary

This work stacks directly on R51 5d407793f4009c26b1862d4c135a9d62294ca13f.
The R48 author advanced draft PR #483 after R51 was assembled:
dbd53411c8fafd06998cb066c1a462348527f24e →
4fe053c41c0a78e32124991fcfbdb52c36753e49.

The exact **20-file R48 delta** has been grafted as original Git objects on
the R51 integration lineage, without cherry-picking the entire incompatible
R48/R49/R50 stack: two updated readiness-matrix files, three machine QA JSON
records, one QA report, twelve original PNG screenshots, and two local QA
scripts. The original upstream R48 blobs remain byte-identical.

The corresponding preparedness/docs/r48/scripts tree includes its previous
three scripts unchanged. Nothing in the 35 article bodies, water planner,
original source registers, citation crosswalk, contributor reading notes,
original safety taxonomy, homepage, site navigation, WordPress or production
workflow has been edited.

## Added substantive independent gate

Command: python -I preparedness/tools/r52_rendered_citation_custody_gate.py

The R52 read-only gate validates 20 original R48 Git blob pins, including PNG
screenshot bytes, and cross-checks the R48 rendered evidence inventory with
the preserved original 35 articles and one water tool.

- 36 distinct article/tool slugs exactly match 36 matrix rows.
- 8 section hubs + 1 landing page yield 45 private preview pages.
- All five reported viewport widths (360/390/768/1440/1920) are present:
  225 page/viewport measurements.
- **1,959 reviewer-visible citation links** and **367 individual rendered
  source entries** match R51's original 1,959 citation occurrences and 367
  article-specific source-reading relationships. No article's source count
  may drift even if global counts are maintained.
- Citation links, referenced sources and other structural measurement counts
  must remain identical across five widths for each page. Reject missing
  citation anchors, unreferenced source entries, broken hash links, duplicate
  IDs, console errors, altered draft badges or missing page inventory.
- All 90 original axe records are retained as machine-only observations,
  **not an accessibility certification**.
- Explicitly retain unresolved mobile first-screen action-box findings and
  the no-JavaScript planner issue. No test result quietly upgrades QA-F1/F2.
- For every article/tool, the readiness matrix must still say
  human_link_checked=0, publish_state=draft, independent_QD=no,
  publication_eligible=NO. Preserve historical per-article safety metadata
  as metadata, never as qualified clinical or emergency-safety clearance.

Native Python discovery includes R52's 82 synthetic/corpus tests
(26 named tests + 36 independent article source-loss mutations + 20
altered-blob tests). Counts must be confirmed by the exact-head hosted run
before claiming success.

## Important limits and remaining real defects

This package **reconciles historical R48 QA evidence**, not a fresh browser
run of the final R52 integration checkout. R48 tested local offline previews
built from R48 dbd53411, not WordPress/Assembler production, and limited
human inspection to three screenshots. The machine QA reported zero axe
violations in 90 runs, but did not test real mobile devices, real screen
readers, 200% zoom, Safari/Firefox, live theme rendering, or full human
visual QA. The Git blob pins are consistency checks for the originally
observed objects, **not independent human attestation**.

These R48 findings remain openly unresolved:

- **QA-F1 HIGH:** all 36 article/tool emergency-action boxes appear below
  the first screen on phones; median at 390x844 is about 1,151 px.
- **QA-F2 MEDIUM:** water planner has no useful no-JS fallback messaging.
- **QA-F3 MEDIUM:** planner silently clamps/rounds input and ignores pets
  with no entered per-pet amount.
- **QA-F4 MEDIUM:** archive section hubs need stronger editorial structure.
- **QA-F5 LOW/MED:** all 61 tables scroll at 360 px (contained, accessible
  scroll regions, but a possible mobile usability improvement).
- **QA-F6 LOW:** verbose planner ARIA live updates still need screen-reader
  verification.

R52 does **not** modify build/CSS or claim these findings fixed; layout
changes need dedicated coordination and new rendered regression evidence.

Separate source and safety blockers remain: 0/206 independently human-checked
source links, 30 shared-URL scope groups, 43 cross-cluster fallback
relationships, all 15 open R48 safety exceptions (5 HIGH, 7 MEDIUM, 3 LOW),
25 historically unreadable original source IDs, 542 unexamined cited
qualitative high-consequence blocks, qualified hazard guidance assessment,
real WordPress browser QA, independent exact-head QD, and human reviewer
identity/custody. Historical safety_review=approved matrix labels must not
be presented as current medical or qualified hazard-safety approval.

Independent QA PR #157 (Start Here safety wording) and PR #169 (food
synthetic-fixture isolation) remain unmerged, and no superseded wording may
be transplanted without checking the current original articles.

## Required exact-checkout verification

1. python -I preparedness/tools/validate.py
2. python -I preparedness/tools/build.py
3. python -I preparedness/tools/r52_rendered_citation_custody_gate.py
4. python -I -m unittest discover -s preparedness/tests -v
5. The existing 13 private hosted pipeline stages and original R51 joint
   numeric/safety custody check.

If local repo cloning is blocked, record that exactly; rely on successful
hosted CI logs for numerical test claims. A green test is **machine-only**.

**Publication decision: HOLD.** No public CMS writes, navigation edits,
merges, or claims of independently verified citations, QD PASS, medically
safe instructions or visitor-ready accessibility are authorized.
