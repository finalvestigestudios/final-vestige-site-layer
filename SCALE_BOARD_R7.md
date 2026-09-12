# Scale Board R7

Scale Board is a visitor-initiated visual-understanding feature for qualifying Final Vestige investigations. It discovers explicit measurements in narrative paragraphs before the canonical Sources boundary and visualizes repeated same-unit magnitudes in proportion.

## R7 QD repair

R7 is the bounded successor to QD-REVISE executable PR #27. R6 made publisher-DOM restoration failure-atomic, but a thrown `scrollIntoView()` or story-target focus operation could occur after the Scale Board dialog had closed while `returnToLaunch` suppressed ordinary return focus. That left the interaction without a deterministic usable focus target even though publisher attributes/classes were restored.

R7 makes interaction state failure-atomic as well. Story jumps still close the feature dialog before scrolling, avoid publisher-owned `id` mutation, and add `tabindex="-1"` only when an otherwise non-focusable paragraph needs temporary programmatic focusability. Failure paths restore that temporary state immediately before recovering focus to a deterministic feature-owned target: the Scale Board launcher when the dialog is closed, or the dialog title/close control if a dialog remains open. A silent focus miss (`focus()` returns without moving `document.activeElement`) is treated as the same recoverable failure.

On a successful jump, an originally non-focusable paragraph retains the feature-owned `tabindex="-1"` only while it is the active focus target; a one-shot blur listener removes that exact feature-owned value when focus leaves. This is necessary because removing the temporary tabindex immediately causes Chromium to drop `document.activeElement` from the paragraph. The cleanup is conditional on the value still being `-1`, so a later publisher change is not overwritten. Pre-owned/nondefault tabindex values are never changed. Successful jumps therefore leave keyboard/screen-reader focus on the story target while guaranteeing automatic restoration of prior absence on blur.

R7 also treats the existence of the publisher's `class` attribute as owned state. `classList.add()` on a paragraph that originally had no class attribute creates one; a later `classList.remove()` leaves an empty `class=""` behind. The feature now records whether the attribute existed before highlighting, removes only its own `fvsb-flash` token, and removes the now-empty class attribute only when the attribute was originally absent. Existing empty/nonempty class attributes and unrelated publisher classes remain untouched. The exact browser state regression that caught this is retained as a release blocker.

The normal dialog close path uses the same guarded feature-owned focus helper, while Escape/cancel restores the ordinary return-focus contract and lets the native close event perform the focus move. No publisher-owned `id`, class, style, ARIA state, text, URL/hash or pre-owned focusability is persistently rewritten.

## Focus/dialog regression boundary

The R7 exact-payload browser suite forces a scroll failure on an attribute-free paragraph and a focus failure on a paragraph with a publisher-owned id. In both cases it requires the dialog to have a coherent closed state, `document.activeElement` to be the launcher, and exact publisher DOM state to match the pre-interaction snapshot. It also proves ordinary success leaves `document.activeElement` on the story paragraph, verifies the temporary tabindex exists only while that paragraph remains focused and restores to absent on blur, proves publisher-owned `tabindex="0"` and `tabindex="-7"` remain exact, preserves publisher-owned highlight classes, preserves the absence of a pre-existing `class` attribute after feature-owned highlight cleanup, repeats jumps, and runs timer cleanup without state drift.

The same R7 payload is executed against the preserved R4, R3, R2 and R1 truth/browser fixtures plus the ambiguous-Sources fixture. R7's dedicated recovery fixture supersedes the R5/R6 fixtures' old focus-duration/failure-propagation expectations while reproducing their publisher-state ownership cases. Thus the full R1–R6 extraction truth, Unicode fraction/division-slash guards, numeric-expression fail-closed behavior, grouped-numeral hardening, overlap resolution, canonical Sources integrity, DOM ownership, accessibility and privacy/no-network/no-storage contracts remain covered.

## Preserved trust and product contract

- exactly one canonical `h2#sources.fv-source-heading` and one later `[data-fv-footnotes]` root are required;
- 12–120 pre-Sources narrative paragraphs and bounded measurement mentions are required;
- only explicitly supported unit-bearing quantities are visualized;
- same-unit values only; no unit conversion or inferred relationships;
- bars compare magnitude only, not importance, causation, confidence, or evidence quality;
- native dialog, 44px controls, focus return, mobile/360px, reduced-motion, forced-colors and print handling are preserved;
- current DOM only; no network calls, cookies, storage, analytics, third-party scripts, clipboard or history mutation;
- visitor-story focus/highlight behavior is failure-atomic across publisher DOM state and interaction focus/dialog state.

## Exact candidate identity

Payload: `payloads/scale-board-wp-block-r7.txt`.

Payload bytes: **18,797**. Payload SHA-256: **`b84460166941060c2dc6150c205d8eb3050d388731354c172e4b725763312154`**.

The final frozen executable head and deterministic package identity are recorded on the pull request after exact-head CI completes. Passing CI is evidence only and does not authorize merge or deployment. Independent QD must review the frozen executable identity. Any subsequent code, workflow, fixture, contract, payload, manifest or package-affecting change creates a new identity and requires fresh QD.
