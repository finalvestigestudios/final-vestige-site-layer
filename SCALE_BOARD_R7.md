# Scale Board R7

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## R7 QD repair

R7 is the bounded successor to QD-REVISE executable PR #27. R6 made publisher-DOM restoration failure-atomic, but a thrown `scrollIntoView()` or story-target focus operation could occur after the Scale Board dialog had closed while `returnToLaunch` suppressed ordinary return focus. That left the interaction without a deterministic usable focus target even though publisher attributes/classes were restored.

R7 makes the interaction state failure-atomic as well. Story jumps still close the feature dialog before scrolling, still avoid publisher-owned `id` mutation, and still add temporary `tabindex="-1"` only around focus when the target had no tabindex. If scrolling or story focus fails, the feature catches the failure after restoring any temporary publisher state and moves focus to a deterministic feature-owned recovery target: the Scale Board launcher when the dialog is closed, or the dialog title/close control if a dialog remains open. A silent focus miss (`focus()` returns without moving `document.activeElement`) is treated as the same recoverable failure. Successful jumps still leave focus on the story target.

The normal dialog close path uses the same guarded feature-owned focus helper, while Escape/cancel simply restores the ordinary return-focus contract and lets the native close event perform the focus move. No publisher-owned `tabindex`, `id`, class, style, ARIA state, text, URL/hash or focusability is persistently rewritten.

## Focus/dialog regression boundary

The R7 exact-payload browser suite forces a scroll failure on an attribute-free paragraph and a focus failure on a paragraph with a publisher-owned id. In both cases it requires: the dialog to have a coherent closed state, `document.activeElement` to be the launcher, and exact publisher DOM state to match the pre-interaction snapshot. It also proves ordinary success focuses the story paragraph while restoring an absent tabindex, proves publisher-owned `tabindex="0"` and `tabindex="-7"` values remain exact, preserves publisher-owned highlight classes, repeats jumps, and runs timer cleanup without state drift.

The same R7 payload is executed against the preserved R6, R5, R4, R3, R2 and R1 fixtures plus the ambiguous-Sources fixture. Thus R1–R6 extraction truth, Unicode fraction/division-slash guards, numeric-expression fail-closed behavior, grouped-numeral hardening, overlap resolution, canonical Sources integrity, DOM ownership, accessibility and privacy/no-network/no-storage contracts remain covered.

## Preserved trust and product contract

- exactly one canonical `h2#sources.fv-source-heading` and one later `[data-fv-footnotes]` root are required;
- 12–120 pre-Sources narrative paragraphs and bounded measurement mentions are required;
- only explicitly supported unit-bearing quantities are visualized;
- same-unit values only; no unit conversion or inferred relationships;
- bars compare magnitude only, not importance, causation, confidence, or evidence quality;
- native dialog, 44px controls, focus return, mobile/360px, reduced-motion, forced-colors and print handling are preserved;
- current DOM only; no network calls, cookies, storage, analytics, third-party scripts, clipboard or history mutation;
- visitor-story focus/highlight behavior is failure-atomic across both publisher DOM state and interaction focus/dialog state.

## Exact candidate identity

Payload: `payloads/scale-board-wp-block-r7.txt`.

Payload bytes: **18,458**. Payload SHA-256: **`de765b59a8bef8c4e5c62e9a44897cf4e73f2216aef3b3da5d2834b7fbd344a8`**.

The final frozen executable head and deterministic package identity are recorded on the pull request after exact-head CI completes. Passing CI is evidence only and does not authorize merge or deployment. Independent QD must review the frozen executable identity. Any subsequent code, workflow, fixture, contract, payload, manifest or package-affecting change creates a new identity and requires fresh QD.
