# Scale Board R1

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## Visitor job

Help a reader notice scale relationships that are easy to miss when quantities are buried in prose, while preserving the exact published context and avoiding inferred data relationships.

## R1 extraction-truth repair

R1 supersedes the QD-revised v1 candidate while preserving the original v1 payload in repository history. Measurement parsing now resolves candidate spans deterministically by story position, longest span, then stable unit-family rank. Overlapping shorter candidates are discarded. As a result, `six miles an hour` and `30 miles per hour` are speed expressions only and cannot also manufacture `Distance · miles` values.

The number grammar now treats properly comma-grouped numerals as one token, so `1,000 feet` is 1000 feet rather than a suffix match on `000 feet`. Compound written values through ninety-nine are consumed as one number, including `thirty-five miles per hour`; unsupported longer constructions fail closed rather than suffix-truncating into a smaller value.

## Qualification and truth boundary

The runtime requires exactly one canonical `h2#sources.fv-source-heading`, exactly one later `[data-fv-footnotes]` root, 12–120 narrative paragraphs before Sources, no more than 80 recognized measurement mentions, and at least one unit group containing two distinct explicit values.

Supported families remain deliberately bounded: common speed, distance, percentage, voltage, power, pressure, mass, duration, and temperature expressions. Bare numbers, dates, passenger counts, money, and source-note numerals are not treated as measurements.

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

## R1 artifact

- payload: `payloads/scale-board-wp-block-r1.txt`
- bytes: **17,266**
- SHA-256: **`64e30ec217524a7a124cf0939d74ef02d8cde234e3734078419a30814dbfead3`**
- prior v1 payload remains preserved as `payloads/scale-board-wp-block-v1.txt`

R1 requires deterministic browser/runtime regressions for `six miles an hour`, `30 miles per hour`, `1,000 feet`, `thirty-five miles per hour`, valid same-unit comparison, and missing/reversed/ambiguous Sources boundaries before independent QD can pass the successor identity.

Passing CI is artifact evidence only. It does not authorize merge or deployment. Independent QD must review the exact frozen PR head SHA. Any code, workflow, verifier, contract, or payload change creates a new identity and requires fresh QD.

The Site Layer bootstrap remains controlling. Any later executable integration must start from then-current `production`, receive a new executable SHA, fresh CI and independent QD, then route to FVS Execution Dispatch. Live destination readback is mandatory before `IMPLEMENTED + VERIFIED`.