# Experience 2.0 — Sprint 04: Evidence Unfolds fail-open and connected Research Desk

**Status:** locally tested R&D prototypes, NOT production code. The current package is `Final_Vestige_Experience_2_Foundation_v4.zip`, 86 files; SHA256 `d41fdeaa62ad1d71da8a0399146189855c4208bce45cd7642443fc183d91e4ff` (conversation artifact, source bytes not committed to repo).

## Bug fixed

The original standalone Apollo 1 experience applied its `.enhanced` class even in browsers without `IntersectionObserver`. The CSS then suppressed all six inline figures, while the viewer could remain stuck on the first piece of evidence as readers progressed through later chapters. This can mis-associate an original record with the wrong argument, which is an editorial accuracy defect as well as progressive-enhancement bug.

The prototype now requires an observer before applying the enhanced state. Missing API means no enhancement: six readable figures with original NASA source links remain available. Existing thrown-observer fault-injection also fails open. Tested in real Chromium.

## Meaningful evidence navigation

- Every Apollo 1 source-inspection dialog links directly to the matching record in the new Research Desk prototype via relative path and exact chapter anchor.
- Apollo 1 footer now links to the complete Research Desk. The links and target IDs were checked against the packaged files.

## Executed checks

- Overall browser/PHP regression runner: PASS (6 checks, including concept board, flagship real Chromium, Atlas real Chromium, Source Ledger generation/real Chromium, and PHP lint).
- Flagship tested 360,390,768,1024,1440,1920; source-dialog keyboard/focus return, no-JS, missing observer, observer exception; no horizontal overflow.
- Source Ledger six records, search, no-JS native disclosure, safe URL allowlist, multi-instance tests all PASS.
- Byte-identical duplicate archive creation; SHA-256 recorded for ten critical files.
- Isolated WordPress staging plugin ZIP unchanged; SHA256 `8c7afa3378734891ab77e7818d3ccec8d328ef122b03710c1d24bf5467f2ac05`.

## Missing evidence before any release

Loaded-image visual and rights verification, real WordPress.com staging, real screen-reader and mobile Safari testing, performance/field CWV, QD of an exact implementation candidate, hosted CI and founder sign-off. Black Dossier remains a proposed art direction, not founder-approved. Do not modify or merge PR #49 as part of this work.

Full source code/screenshots/tests are in the v4 archive delivered in ChatGPT; this Git branch is planning/verification metadata only.