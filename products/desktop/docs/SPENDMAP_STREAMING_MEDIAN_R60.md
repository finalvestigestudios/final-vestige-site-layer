# SpendMap Lite R60 — exact streaming monthly median

**Status:** Pre-release source improvement only. All six Windows x64 apps remain unreleased; this change does not modify compiled files, download URLs, premium entitlements, or production/site resources.

## Fixed bottleneck

R59 called statistics.median(prior) once for each observed vendor month, re-sorting every earlier monthly total each time. A vendor with M observed months requires approximately **O(M² log M)** sorting work in the worst case. Long historical CSV exports could therefore run disproportionately slowly despite the input row and byte limits.

R60 uses a RunningDecimalMedian with two heaps per vendor: insertion **O(log M)** and historical median lookup **O(1)**. Values are **finite Decimal only**, never floats. Even-sized medians retain exact half-cent midpoints. Median-maintenance work is **O(M log M)** across all observed months, excluding the unchanged input aggregation, month sorting, and output writing.

**Current-month exclusion:** Compute the review threshold from previous observed months, then add the current month to the running median. The existing >= 2 × positive historical median spike rule starts after three previous observed months, unchanged. Case-insensitive vendor collisions, original source-row references, categories, CSV column order, formula-safe output, and human review requirements are unchanged. Absence of a spike does not mean compliance or payment approval.

## Local diagnostic evidence and limitations

The exact R59 source baseline (spend_analysis.py Git blob e0a92d284ee150a2e46400ecacd3badaf7bc6aa0) and the modified R60 source produced **identical complete report rows** for synthetic single-vendor histories of **1,200** and **3,600** observed months, under local Linux Python 3.13.5. On one 3,600-month fixture, observed local times were approximately 1.175 seconds (previous implementation) versus 0.031 seconds (streaming implementation). These are **machine-specific diagnostic observations**, not guaranteed customer performance; tests do not assert elapsed timing thresholds.

13 new regression tests exercise nonfinite/non-Decimal rejection, negative refunds, duplicates, half-cent exactness, large amounts, the 50,000-value running-median reference result, independent vendor histories, unchanged review behavior, 4,800 synthetic monthly report rows, and deterministic reexecution. 20 existing R59 provenance/spike regressions also pass with the new implementation.

### Reproduce in a trusted complete checkout

1. PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p 'test_spend*_r*.py' -v
2. PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p 'test_spend*_r*.py' -v
3. python products/desktop/scripts/offline_source_gate.py --report <new-private-external-path>

These focused local tests **do not** prove the complete repository's source gate or the Windows executable build. The full source suite, six synthetic smokes, Windows 11 x64 builds and actual GUI/PE runtime smoke, malware scan, checksum/accessibility tests and gated premium download controls remain required. GitHub Actions runner-start failures are tracked in [issue #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75).

**Release hold:** no publication, license/distribution changes, production merge, or bypass of independent QD and founder approval.
