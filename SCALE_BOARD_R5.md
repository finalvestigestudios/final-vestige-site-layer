# Scale Board R5

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## R5 QD repair

R5 is the bounded executable successor to the QD-REVISE Scale Board R4 integration. R4's `View in story` interaction created an unnecessary random paragraph `id` and unconditionally wrote `tabindex="-1"`, which could permanently damage publisher-owned DOM state. It also added and later removed the feature's flash class without distinguishing a class that might already belong to the page.

R5 makes the interaction nondestructive. It never creates or rewrites a story-point `id`. If a target paragraph has no `tabindex`, R5 temporarily adds `tabindex="-1"` only long enough to move focus and then removes it immediately. Existing `tabindex` values—including `0` and nondefault negative values—are left untouched. The flash class is temporary only when R5 added it; a pre-owned `fvsb-flash` class is preserved.

## DOM-state regression boundary

The exact-payload browser suite covers an initially absent `tabindex`, a publisher-owned `tabindex="0"`, a nondefault negative `tabindex="-7"`, a publisher-owned `id`, a pre-owned `fvsb-flash` class, and repeated `View in story` jumps. After the interaction, the exact pre-existing state must remain intact and no random `id` may be left behind.

The same R5 payload is also executed against the preserved R4, R3, R2 and R1 extraction-truth fixtures plus the ambiguous-Sources fixture. Thus the Unicode fraction/division-slash guard, numeric-expression fail-closed behavior, grouped-numeral hardening, overlap resolution, Sources contract and all prior truth boundaries remain regression-tested.

## Preserved trust and product contract

- exactly one canonical `h2#sources.fv-source-heading` and one later `[data-fv-footnotes]` root are required;
- 12–120 pre-Sources narrative paragraphs and bounded measurement mentions are required;
- only explicitly supported unit-bearing quantities are visualized;
- same-unit values only; no unit conversion or inferred relationships;
- bars compare magnitude only, not importance, causation, confidence, or evidence quality;
- native dialog, 44px controls, focus return, mobile/360px, reduced-motion, forced-colors and print handling are preserved;
- current DOM only; no network calls, cookies, storage, analytics, third-party scripts, clipboard or history mutation;
- visitor-story focus/highlight behavior is nondestructive and restores pre-existing DOM state.

## Exact candidate identity

The final frozen head, exact payload bytes/SHA and deterministic package identity are recorded on the pull request after exact-head CI completes. Passing CI is evidence only and does not authorize merge or deployment. Independent QD must review the frozen executable identity. Any subsequent code, workflow, fixture, contract, payload, manifest or package-affecting change creates a new identity and requires fresh QD.
