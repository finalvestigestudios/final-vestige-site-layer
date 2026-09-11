# Scale Board R2

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## Visitor job

Help a reader notice scale relationships that are easy to miss when quantities are buried in prose, while preserving the exact published context and avoiding inferred data relationships.

## R2 extraction-truth repair

R2 supersedes the QD-revised R1 candidate while preserving the earlier v1 and R1 payloads in repository history. R1 already resolved overlapping unit expressions by story position and longest span, so `six miles an hour` and `30 miles per hour` remain speed expressions only; it also preserved comma-grouped numerals such as `1,000 feet` and compound written values such as `thirty-five miles per hour`.

R2 closes the remaining suffix-truncation defect. Paragraph text is whitespace-normalized before parsing, so unsupported space-, NBSP-, and narrow-NBSP-grouped numerals can otherwise expose a trailing numeric suffix to the measurement regex. The number-boundary guard now rejects a numeric candidate when the preceding normalized context is another digit followed by whitespace, and it also treats straight/typographic apostrophes and underscore-like numeric separators as disqualifying adjacent numeric punctuation. As a result, unsupported forms such as `1 000 feet`, `1 000 feet`, `1 000 feet`, `1'000 feet`, `1’000 feet`, and malformed adjacent forms such as `12 34 feet` fail closed instead of becoming `0 ft`, `34 ft`, or another partial value.

## Qualification and truth boundary

The runtime requires exactly one canonical `h2#sources.fv-source-heading`, exactly one later `[data-fv-footnotes]` root, 12–120 narrative paragraphs before Sources, no more than 80 recognized measurement mentions, and at least one unit group containing two distinct explicit values.

Supported families remain deliberately bounded: common speed, distance, percentage, voltage, power, pressure, mass, duration, and temperature expressions. Bare numbers, dates, passenger counts, money, source-note numerals, unsupported thousands separators, and malformed grouped numerals are not treated as measurements.

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

## R2 artifact

- payload: `payloads/scale-board-wp-block-r2.txt`
- bytes: **17,306**
- SHA-256: **`8e9c451eb9ec9bbaec4f172d0c6b07f4f05b95033941c716d83ca75bfc4885d5`**
- prior artifacts remain preserved as `payloads/scale-board-wp-block-v1.txt` and `payloads/scale-board-wp-block-r1.txt`

R2 exact-payload browser regressions cover valid `six miles an hour`, `30 miles per hour`, `thirty-five miles per hour`, `20 mph`, `1,000 feet`, and `500 feet`, plus adversarial space/NBSP/narrow-NBSP/straight-apostrophe/typographic-apostrophe grouped thousands and malformed adjacent numeric constructions. They require exactly 6/20/30/35 mph, exactly 500/1000 ft, no false `Distance · miles` group, no partial 0/34/000-foot value, and ambiguous Sources fail-closed behavior.

Passing CI is artifact evidence only. It does not authorize merge or deployment. Independent QD must review the exact frozen PR head SHA. Any code, workflow, fixture, contract, or payload change creates a new identity and requires fresh QD.

The Deployment Bridge bootstrap is active, but this artifact PR is not an executable production release. If independent QD passes R2, runtime integration must still be created from then-current `production`, receive a new executable SHA, fresh CI and independent QD, route through FVS Execution Dispatch, deploy through the governed bridge, and pass live desktop/mobile/accessibility/network/destination readback before `IMPLEMENTED + VERIFIED`. No direct WordPress footer/template write is an acceptable substitute.
