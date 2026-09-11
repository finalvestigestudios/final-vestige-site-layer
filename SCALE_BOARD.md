# Scale Board v1

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers only explicit, published measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## Visitor job

Help a reader notice scale relationships that are easy to miss when quantities are buried in prose, while preserving the exact published context and avoiding inferred data relationships.

## Interaction principle

The feature adapts the multi-view, full-screen exploration and prominent-source-context principles of best-in-class data products such as Our World in Data. Final Vestige applies the idea to quantities already present in one investigation rather than importing a dataset or external visualization service.

## Qualification and truth boundary

The runtime requires exactly one canonical `h2#sources.fv-source-heading`, exactly one later `[data-fv-footnotes]` root, 12–120 narrative paragraphs before Sources, no more than 80 recognized measurement mentions, and at least one unit group containing two distinct explicit values.

Supported families are deliberately bounded: common speed, distance, percentage, voltage, power, pressure, mass, duration, and temperature expressions. Bare numbers, dates, passenger counts, money, and source-note numerals are not treated as measurements.

Scale Board groups values only when they share the same normalized unit family. It does not convert across units, infer that two values describe the same phenomenon, rank importance, infer causation, score confidence, or score evidence quality. Story-context cards return to the original paragraph.

## Accessibility / performance

- native modal dialog with accessible name
- 44px minimum controls and visible focus
- Close/Escape focus return
- story jump transfers keyboard focus to the published paragraph
- full-height mobile mode and 360px tuning
- reduced-motion and forced-colors handling
- print suppression
- current-DOM parsing only; lazy dialog construction
- no network calls, cookies, storage, analytics, third-party scripts, clipboard, or history mutation

## Frozen artifact

- payload: `payloads/scale-board-wp-block-v1.txt`
- bytes: **16,198**
- SHA-256: **`7e0109c4315e2206ee73ed1f1fa1ed808953362561a7a82652fc4541ad7fe729`**
- verifier: `tests/verify_scale_board.py`
- workflow: `.github/workflows/scale-board-ci.yml`

Passing CI is artifact evidence only. It does not authorize merge or deployment. Independent QD must review the exact frozen PR head SHA. Any code, workflow, verifier, contract, or payload change creates a new identity and requires fresh QD.

The Site Layer bootstrap remains controlling. Any later executable integration must start from then-current `production`, receive a new executable SHA, fresh CI and independent QD, then route to FVS Execution Dispatch. Live destination readback is mandatory before `IMPLEMENTED + VERIFIED`.
