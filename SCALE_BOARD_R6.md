# Scale Board R6

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## R6 QD repair

R6 is the bounded successor to QD-REVISE executable PR #26. R5 preserved ordinary success-path DOM state, but its `View in story` interaction temporarily wrote `tabindex="-1"` before calling `scrollIntoView()`. If scrolling threw, control exited before the restoration `finally`, which could strand feature-owned focusability on publisher content.

R6 is failure-atomic. It performs scrolling before any publisher-node attribute or class mutation. Only after scrolling succeeds does it temporarily add `tabindex="-1"` when the paragraph originally had no tabindex; focus runs inside the same `try/finally`, and the temporary attribute is removed even when focus throws. Existing tabindex values remain untouched. The feature never creates or rewrites a story-point id. The highlight class is added only when not already owned by the page; timer scheduling is guarded so a synchronous scheduling failure removes any feature-added class before rethrowing.

## DOM-state regression boundary

The R6 exact-payload browser suite injects `scrollIntoView()` failures against an initially attribute-free target, a target with publisher-owned `tabindex="0"`, and a target with a publisher-owned `fvsb-flash` class. It also injects a focus failure against a target with a publisher-owned id and no tabindex. In every failure case, exact pre-existing tabindex/id/class state must survive. Successful absent/pre-owned/nondefault tabindex paths, repeated jumps and timer cleanup remain regression-tested through both the R6 fixture and the preserved R5 fixture.

The same R6 payload is executed against the preserved R4, R3, R2 and R1 extraction-truth fixtures plus the ambiguous-Sources fixture. Thus Unicode fraction/division-slash guards, numeric-expression fail-closed behavior, grouped-numeral hardening, overlap resolution, Sources integrity and the prior truth contract remain covered.

## Preserved trust and product contract

- exactly one canonical `h2#sources.fv-source-heading` and one later `[data-fv-footnotes]` root are required;
- 12–120 pre-Sources narrative paragraphs and bounded measurement mentions are required;
- only explicitly supported unit-bearing quantities are visualized;
- same-unit values only; no unit conversion or inferred relationships;
- bars compare magnitude only, not importance, causation, confidence, or evidence quality;
- native dialog, 44px controls, focus return, mobile/360px, reduced-motion, forced-colors and print handling are preserved;
- current DOM only; no network calls, cookies, storage, analytics, third-party scripts, clipboard or history mutation;
- visitor-story focus/highlight behavior is failure-atomic and nondestructive with respect to pre-existing publisher DOM state.

## Exact candidate identity

Payload: `payloads/scale-board-wp-block-r6.txt`.

The final frozen head, exact payload bytes/SHA and deterministic package identity are recorded on the pull request after exact-head CI completes. Passing CI is evidence only and does not authorize merge or deployment. Independent QD must review the frozen executable identity. Any subsequent code, workflow, fixture, contract, payload, manifest or package-affecting change creates a new identity and requires fresh QD.
