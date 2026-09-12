# FVF-13 — Case Compass R1

## Repair purpose

This is the governed successor to the original FVF-13 Case Compass artifact. It preserves the visitor job and structural-map behavior while closing the independent-QD citation-cleaning and keyboard-focus defects and bringing story jumps under the current nondestructive DOM-state contract.

## Visitor job

Help a reader understand the shape of a long Final Vestige investigation, see their current section, and jump to another major turn in the story without opening search, losing their place, or reducing the article to a generic table of contents.

## R1 repair contract

- Structural headings, passage qualification and narrative-character qualification use a detached-clone cleaner that removes both legacy `.fv-fn-mark` UI and the live `.fv-fn-ref[data-fv-fn]` citation marker contract before reading text.
- Citation-marker text therefore cannot leak into Case Compass section labels or inflate the longform thresholds.
- Mini-rail, opener, dialog-card and close controls expose an unmistakable 3px `:focus-visible` indicator in standard mode and a 3px `Highlight` indicator in forced-colors mode.
- Story jumps scroll before touching publisher-owned state.
- Temporary `tabindex="-1"` is added only when the destination had no tabindex and is removed immediately after the focus transaction.
- The temporary arrival class is added only when Case Compass owns that token, is cleaned on failure/repeat/timeout, and an originally absent `class` attribute returns to absent.
- Pre-owned/nondefault tabindex values and pre-owned classes, including a pre-owned `fvcc-arrived` token, are left intact.
- Scroll/focus failures recover focus to the invoking feature control and do not strand temporary publisher-node state.

## Qualification and fail-closed boundary

The feature activates only on a `single-post` page when native `<dialog>` is supported; the trusted `h2#sources.fv-source-heading` boundary and `.fv-source-list[data-fv-footnotes]` exist in the required order within the same content root; at least three story H2 headings, twelve substantive citation-clean paragraphs, and 2,800 citation-clean narrative characters occur before Sources; an opening narrative passage exists before the first story H2; and the resulting map contains at least four sections including Opening. If a requirement fails, Case Compass adds nothing.

## Visitor experience

Case Compass remains a compact structural map: a prominent `Open full map` control, an inline section rail, a live `You're in` indicator, a full native-dialog map, exact structural passage/figure/linked-note counts, Arrow/Home/End keyboard navigation, and a return to the selected published story section. Counts describe page structure only and are not evidence or confidence scores.

## Accessibility / responsive / state safety

- native modal dialog behavior and logical close/focus handoff;
- 44px minimum controls;
- explicit standard and forced-colors keyboard focus treatment;
- `aria-current="location"` plus polite current-section announcement;
- reduced-motion, 700px/360px mobile and print behavior;
- browser regressions for citation-bearing headings, standard focus visibility, dialog keyboard movement, absent DOM state, pre-owned/nondefault DOM state, repeated jumps, forced scroll failure and forced focus failure;
- no permanent tabindex/id/class/style/ARIA mutation of publisher story destinations.

## Privacy / network / evidence boundary

Case Compass reads only the current page DOM. It does not use cookies, local/session storage, IndexedDB, analytics, fetch/XHR/WebSocket/sendBeacon, third-party scripts, account state, or history mutation. It does not change article wording, citations, source destinations, figure pixels, or source records. It does not infer evidence quality or confidence.

## R1 frozen payload identity

- repository: `finalvestigestudios/final-vestige-site-layer`
- base production at build start: `3f7841a7c671f9e8e955b417480d853ad0a0a948`
- branch: `repair/case-compass-r1-citation-focus-state`
- payload: `payloads/case-compass-wp-block-v1.txt`
- payload bytes: `16752`
- payload SHA-256: `0d36b0dcdccc36404f9aa5b1236199de4ac5d86950dbf9e4adb86e5867c62731`
- deterministic verifier: `tests/verify_case_compass.py`
- dedicated workflow: `.github/workflows/case-compass-ci.yml`

The exact successor head SHA is frozen only after the final source/test/workflow/contract commit and fresh CI attempt. CI success is evidence, never approval. Do not merge or deploy this artifact because tests pass. Independent QD must review the exact final identity first; any later executable integration must be rebuilt from then-current production and receive its own fresh QD review and governed dispatch.
