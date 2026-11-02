# R77 — Temporal source metadata and citation-impact custody (PRIVATE DRAFT / HOLD)

**Scope:** Preparedness Archive, Issue #136 ONLY. **Stacked immutable base:** R76 draft PR #668 at 06593b2ee812168991e941b9484753862e96567a. **Separate untouched candidate:** PR #584 at ddb3528ba6494dada1fa1c3a142ce746e3a67706.

## Engineering purpose

R76 provides 244 complete origin-scoped source readings, 2,173 distinct citation occurrences, 2,359 citation/source-variant relationships, 4,070 complete DOM blocks, 35 article drafts and six tool drafts. R77 adds a deterministic, explicitly **nonjudgmental** temporal source-metadata review work order, with the entire R76 source/DOM/citation evidence nested verbatim. No publication approval is derived.

Each source card preserves literal published/updated/reviewed/verified_on values, including missing fields and year/month-only precision, exact URL, source-origin/source-ID pair, complete source-reading digest, original-versus-candidate historical metadata, downstream citation-impact edges, and lexical action/quantity triage counts. The review worklist flags missing machine-fetch dates; missing update/review fields; invalid or unparseable dates; website timestamps that precede a publication date; material updated or reviewed after a recorded machine fetch; and timestamps later than the pinned 2026-11-02 snapshot. No date is silently normalized into a guessed day. Some legitimate government pages show surprising date order; discrepancies trigger **human inspection, not source rejection or safety conclusions**.

The second reviewer index preserves every shared-URL group independently and reports metadata disagreement without combining source identities. Reviewer ordering is by documentation workload, not clinical risk. A machine-verification date does NOT mean a person checked the URL or that the specific citation supports the associated claim.

## Isolated additive files

1. preparedness/tools/r77_temporal_evidence_custody.py — deterministic read-only report and one-way formula-neutralized CSV; NO approval importer.
2. preparedness/tests/test_r77_temporal_evidence_custody.py — source/citation/DOM conservation, date precision, synthetic chronology, forged-approval and source-mutation adversarial tests; no shared-tree fixtures.
3. preparedness/docs/R77_TEMPORAL_EVIDENCE_CUSTODY_HOLD.md — this release-HOLD and coordination record.
4. .github/workflows/preparedness-r77-private-tests.yml — exact SHA, four-additive-file guard, Python isolated/complete tests, original validator and offline private draft build. Not the mandatory 13-stage gate.

Reproduce from an exact R77 checkout:

    python -I -m unittest discover -s preparedness/tests -p test_r77_temporal_evidence_custody.py -v
    python -I preparedness/tools/r77_temporal_evidence_custody.py
    python -I preparedness/tools/r77_temporal_evidence_custody.py --private-review-csv-stdout > /tmp/r77-temporal-review.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Never report test passes unless an actual execution is observed. The CSV is a review navigation aid, never an approval importer or a safety verdict.

## Verified exact Git references (2026-11-02)

| Workstream | Exact current commit |
|---|---|
| Claude start | 2122d856fce9f64887c16df3d52e64be9f59a55b |
| Claude shelter | 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 |
| Claude food | f911ff7a655de8d81535ea86ec3d65a49ee76648 |
| Claude health | d5ef5bafd68361434dd1cc9209915b8e8a4eaf17 |
| Claude historical food | 67e116e536c7410bed30f8f3b1bb8c166f3c223d |
| Claude historical home | 7504a5f099594d635e3dd7332a33a2e1346c43a2 |
| Claude historical field | 4e5caf812727953aa45e3bda2d382f2c67b6a09c |
| Separate RC PR #584 | ddb3528ba6494dada1fa1c3a142ce746e3a67706 |
| Independent safety QA PR #157 | 7d1ae6b8ef93d10cfb6810987672360885e9c1aa |
| Synthetic fixture QA PR #169 | e9cd7766dac59d47ab467d8945269b9146c2aef5 |
| Homepage lead PR #49 | 10495883299d53596992c26a8987f629b2904670 |
| Experience flagship PR #604 | 368399842de1bd4fc02598571c0fa29eb5ad279c |

QA PR #157 makes bounded Start Here safety and gating changes but is unmerged and not approved. QA PR #169 isolates the source-upgrade fixture in a temp copy and the unverified source in memory, but the unchanged test_register_fragments_cannot_duplicate_ids still creates _dup_test.json in the shared fragments folder. This remains a concurrency risk for its owner; do NOT silently modify that PR. Homepage/flagship PRs were verified read-only and untouched.

## Publication HOLD

Last observed mandatory 13-stage integrity failed closed at seven_cluster_git_parity; five historical contributor refs diverge from the frozen provenance baseline. Human source and claim scope checks, source URL/fallback decisions, 15 safety exceptions, 22 release-candidate editorial decisions, expert review of consequential water/food/generator/medical instructions, actual WordPress/browser/assistive QA and independent QD remain incomplete.

No original articles, source records, taxonomy, homepage, public navigation, WordPress or CMS changes. No merge, QD PASS, medical safety assertion or publication permission. Machine diagnostics are not editorial or safety approvals.