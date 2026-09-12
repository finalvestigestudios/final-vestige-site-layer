# Scale Board R7

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## R7 QD repair

R7 is the bounded successor to QD-REVISE executable PR #27. R6 restored publisher-owned `tabindex`, `id`, and class state when injected `scrollIntoView()` or focus operations failed, but it closed the modal and suppressed launcher-focus restoration before those operations completed. A failed jump could therefore leave the interaction in a closed-dialog, indeterminate-focus state even though the publisher DOM itself had been restored.

R7 makes the whole `View in story` interaction failure-atomic. Scrolling is attempted while the Scale Board dialog remains open. Only after scrolling succeeds does the feature suppress the next normal close-focus return and close the dialog for the story-focus transaction. If target focus or highlight scheduling fails after that close, R7 reopens the same feature-owned dialog and returns focus to the exact `View in story` control that initiated the transaction (falling back to the feature close control or launcher only when necessary). A failed scroll never closes the dialog. Successful jumps still end with the dialog closed and focus on the published story target.

Publisher-owned DOM state remains nondestructive: R7 never creates or rewrites story-point ids; an absent `tabindex` is temporary only around programmatic focus and is restored in `finally`; authored/nondefault tabindex values are never rewritten; and a pre-owned `fvsb-flash` class is never removed. Feature-added highlight state is rolled back if scheduling fails.

## Focus/dialog regression boundary

The R7 exact-payload browser suite asserts `document.activeElement` and dialog open/closed state after injected scroll failure, injected focus failure, injected timer-scheduling failure, successful story jumps, repeated jumps, and timer cleanup. Failure paths must leave the dialog open with focus recovered to the initiating jump control; success paths must close the dialog with focus on the intended story target. The suite simultaneously snapshots absent and publisher-owned/nondefault `tabindex`, `id`, and class state before and after every transaction.

The same R7 payload is also browser-executed against the preserved R5 nondestructive-DOM fixture, the R4/R3/R2/R1 extraction-truth fixtures, and the ambiguous-Sources fixture. Thus Unicode fraction/division-slash guards, numeric-expression fail-closed behavior, grouped-numeral hardening, overlap resolution, Sources integrity and prior truth contracts remain covered.

## Preserved trust and product contract

- exactly one canonical `h2#sources.fv-source-heading` and one later `[data-fv-footnotes]` root are required;
- 12–120 pre-Sources narrative paragraphs and bounded measurement mentions are required;
- only explicitly supported unit-bearing quantities are visualized;
- same-unit values only;
- bars compare magnitude only, not importance, causation, confidence, or evidence quality;
- native dialog, 44px controls, mobile/360px, reduced-motion, forced-colors and print handling are preserved;
- current DOM only; no network calls, cookies, storage, analytics, third-party scripts, clipboard or history mutation;
- story navigation is failure-atomic across both publisher DOM ownership and focus/dialog interaction state.

## Exact candidate identity

Payload: `payloads/scale-board-wp-block-r7.txt`.

The final frozen head, exact payload bytes/SHA and deterministic package identity are recorded on the pull request after exact-head CI completes. Passing CI is evidence only and does not authorize merge or deployment. Independent QD must review the frozen executable identity. Any subsequent code, workflow, fixture, contract, payload, manifest or package-affecting change creates a new identity and requires fresh QD.
