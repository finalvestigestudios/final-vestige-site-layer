# Prototype sources, Sprints 1-4 (superseded)

Kept **verbatim** from `Final_Vestige_Experience_2_Foundation_v4.zip` (SHA-256 `d41fdeaa62ad1d71da8a0399146189855c4208bce45cd7642443fc183d91e4ff`) for provenance and so the three art directions remain available for comparison. Text sources only; screenshots, generated HTML and QA JSON were not committed.

- `concept-board.html`: Black Dossier, Museum After Hours and Observatory side by side. Black Dossier is the provisional direction, not founder-approved.
- `flagship-apollo1/`, `source-ledger/`, `build_atlas_preview.py`, `atlas_seed_catalog.json`: the original generators and data. **Not maintained.** The maintained versions are in `../data`, `../design-system`, `../tools` and `../atlas`.
- The verifiers hard-code `/usr/bin/chromium` and expect a sibling directory layout; they will not run unmodified outside the original sandbox.

Known defects in these files, fixed in the maintained code: a mockup photograph captioned as the original hatch; context and museum photographs not labelled as such; fixed element ids in the shortcode template; a sticky evidence viewer that depended on script state. See `../../docs/experience-2.0/SPRINT-05.md`.
