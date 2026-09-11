# Scale Board R4

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## R4 QD repair

R4 is the bounded successor to independent-QD-REVISE Scale Board R3. R3 correctly rejected the tested ASCII slash fraction/range/arithmetic suffix class but omitted two Unicode slash characters from its invalid numeric-expression boundary sets: U+2044 FRACTION SLASH (`⁄`) and U+2215 DIVISION SLASH (`∕`). That omission could allow the final numeric token of an unsupported expression such as `3⁄4 miles` or `1∕2 feet` to suffix-match as a false supported quantity.

R4 adds U+2044 and U+2215 to both the immediate invalid-prefix character set and the broader numeric-expression operator/separator set. It deliberately fails closed rather than attempting to interpret Unicode fractions or division expressions. Both unspaced and spaced forms are covered.

## Regression boundary

The exact-payload browser suite requires the valid result to remain exactly 6/20/30/35 mph and 500/1000 ft. It proves fail-closed behavior for U+2044/U+2215 forms including `3⁄4 miles`, `3 ⁄ 4 feet`, `1⁄2 feet`, `3∕4 miles`, `3 ∕ 4 feet`, and `1 ∕ 2 miles`. The same R4 payload is also executed against the preserved R3, R2, and R1 truth fixtures plus the ambiguous-Sources fixture, so the prior extraction-truth repairs remain regression-tested.

## Preserved trust and product contract

- exactly one canonical `h2#sources.fv-source-heading` and one later `[data-fv-footnotes]` root are required;
- 12–120 pre-Sources narrative paragraphs and bounded measurement mentions are required;
- only explicitly supported unit-bearing quantities are visualized;
- same-unit values only; no unit conversion or inferred relationships;
- bars compare magnitude only, not importance, causation, confidence, or evidence quality;
- native dialog, 44px controls, focus return, mobile/360px, reduced-motion, forced-colors, and print handling are preserved;
- current DOM only; no network calls, cookies, storage, analytics, third-party scripts, clipboard, or history mutation.

## Exact R4 payload identity

- base production at branch creation: `3f7841a7c671f9e8e955b417480d853ad0a0a948`
- payload: `payloads/scale-board-wp-block-r4.txt`
- bytes: **17,520**
- SHA-256: **`ecd9a6aed288061abd2ec55d53a049595174f8579178be773802d8ce7b325fee`**

Passing CI is artifact evidence only. It does not authorize merge or deployment. Independent QD must review the final frozen pull-request head SHA and exact-head CI. Any subsequent code, workflow, fixture, contract, or payload change creates a new identity and requires fresh QD.

This artifact is not an executable production release. If independent QD passes R4, the governed release must be created from then-current `production`, receive a new executable SHA, fresh CI and fresh independent QD, route through FVS Execution Dispatch, deploy through the Site Layer bridge, and pass live desktop/mobile/accessibility/network/destination readback before `IMPLEMENTED + VERIFIED`. No direct WordPress footer/template write is authorized.
