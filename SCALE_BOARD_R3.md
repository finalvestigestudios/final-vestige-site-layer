# Scale Board R3

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## Visitor job

Help a reader notice scale relationships that are easy to miss when quantities are buried in prose, while preserving the exact published context and avoiding inferred data relationships.

## R3 extraction-truth repair

R3 supersedes the QD-revised R2 candidate while preserving the v1, R1, and R2 artifacts in repository history and as separate payload files. R1 resolved overlapping expressions by story position and longest span. R2 blocked unsupported grouped-number suffix matches such as `1 000 feet`, `1'000 feet`, and malformed adjacent numerals.

R3 closes the remaining numeric-expression suffix class. A recognized number+unit candidate is rejected when its numeric token is immediately preceded by an unresolved numeric expression, including slash fractions, spaced slash fractions, ratios, multiplication/exponent operators, numeric ranges, and bounded textual ranges. This prevents unsupported forms such as `3/4 miles` from becoming a false `4 mi`, `1/2 feet` from becoming a false `2 ft`, and comparable larger numeric expressions from being silently truncated to their final numeric token.

The repair deliberately fails closed rather than trying to interpret fractions, ranges, ratios, or arithmetic. Scale Board still visualizes only the bounded number grammar it explicitly supports.

## Qualification and truth boundary

The runtime requires exactly one canonical `h2#sources.fv-source-heading`, exactly one later `[data-fv-footnotes]` root, 12–120 narrative paragraphs before Sources, no more than 80 recognized measurement mentions, and at least one unit group containing two distinct explicit values.

Supported families remain deliberately bounded: common speed, distance, percentage, voltage, power, pressure, mass, duration, and temperature expressions. Bare numbers, dates, passenger counts, money, source-note numerals, unsupported thousands separators, fractions, ranges, arithmetic expressions, and malformed grouped numerals are not treated as measurements.

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

## R3 frozen payload identity

- payload: `payloads/scale-board-wp-block-r3.txt`
- bytes: **17,508**
- SHA-256: **`b48181a8a0cb7dd319ee0ff091a8f2f8934c0812afc36fabd0ebb009d75a7be4`**
- prior artifacts remain preserved as `payloads/scale-board-wp-block-v1.txt`, `payloads/scale-board-wp-block-r1.txt`, and `payloads/scale-board-wp-block-r2.txt`

## Exact-payload regression boundary

The R3 browser suite executes the exact payload against valid values plus unsupported expressions including `3/4 miles`, `1/2 miles`, `1/2 feet`, `3 / 4 feet`, `3:4 feet`, `3×4 feet`, `3*4 feet`, `3^4 feet`, `3–4 feet`, and `3 to 4 feet`. It also reruns the R2 and R1 truth fixtures against the R3 payload and preserves the ambiguous-Sources fail-closed regression.

The valid result must remain exactly 6/20/30/35 mph and 500/1000 ft, with no false distance-miles group and no extra foot values from unsupported expressions.

Passing CI is artifact evidence only. It does not authorize merge or deployment. Independent QD must review the final frozen PR head SHA. Any code, workflow, fixture, contract, or payload change creates a new identity and requires fresh QD.

The Deployment Bridge is active, but this artifact PR is not an executable production release. If independent QD passes R3, runtime integration must still be created from then-current `production`, receive a new executable SHA, fresh CI and fresh independent QD, route through FVS Execution Dispatch, deploy through the governed bridge, and pass live desktop/mobile/accessibility/network/destination readback before `IMPLEMENTED + VERIFIED`. No direct WordPress footer/template write is authorized.
