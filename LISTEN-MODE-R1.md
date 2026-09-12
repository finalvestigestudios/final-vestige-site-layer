# FVF-11 — Listen Mode R1

## Repair target

Independent QD found that the original Listen Mode cleaned the legacy `.fv-fn-mark` wrapper but did not explicitly remove the governed live citation anchor `.fv-fn-ref[data-fv-fn]`. A wrapper-free live citation could therefore contribute its visible marker text to `SpeechSynthesisUtterance` even though source notes were meant to stay outside narration.

R1 closes that defect without merging or mutating the original artifact PR.

## Visitor job preserved

Listen Mode remains an opt-in narration utility for qualifying Final Vestige longform. A reader can listen to story headings and narrative passages in document order, move backward or forward, pause/resume, select a bounded narration rate, retain section context, and close the player with focus returned to the launcher.

The speech engine comes from the visitor's browser or device. Final Vestige does not add an audio backend, voice profile, narration account, or external speech request.

## R1 citation-cleaning contract

`spokenText()` works only on a detached clone. Before text is normalized for speech it removes:

- `.fv-fn-ref[data-fv-fn]` — the live Final Vestige citation-anchor contract;
- `.fv-fn-mark` — legacy/current wrapper compatibility;
- `.fv-fn-backlinks`;
- Passage Kit action UI;
- nodes already marked `aria-hidden="true"`.

The published article DOM remains the source of truth and is not rewritten to make narration clean. Narrative wording surrounding a citation remains intact. Source records remain outside the narrated segment set.

## Nondestructive DOM state

R1 also brings Listen Mode's current-passage treatment under the current Site Sprint state-preservation rule. The feature no longer removes every `.fv-listen-mode-current` class it can find. It tracks only the exact node/token it owns.

If a story node had no `class` attribute before Listen Mode added its temporary marker, cleanup returns that attribute to absent rather than leaving `class=""`. If a publisher/theme node already owned `fv-listen-mode-current`, R1 does not remove it. Repeated open/play/close interactions are part of the browser regression contract.

Listen Mode does not add or rewrite publisher `id`, `tabindex`, style, ARIA, or focusability attributes.

## Behavioral verification

The R1 headless-browser fixture uses the exact payload and a deterministic browser speech-synthesis double. It proves:

- a wrapper-free `.fv-fn-ref[data-fv-fn]` marker does not enter utterance text;
- a legacy wrapped live citation marker does not enter utterance text;
- narrative surrounding both citation forms is still spoken;
- source-list records never enter the utterance sequence;
- published narrative/source `innerHTML` remains unchanged;
- a classless story node returns to having no `class` attribute after Close;
- publisher-owned classes and a pre-owned `fv-listen-mode-current` token survive;
- repeat open/play/close does not drift publisher DOM state;
- Close returns focus to the launcher.

Static verification also locks exact payload bytes/hash, JavaScript syntax, single-post/longform/source qualification, native speech capability gating, transport/rate controls, 44px targets, small-mobile, forced-colors, reduced-motion and print behavior, and the no-persistence/no-network/no-analytics/no-voice-enumeration boundary.

## Privacy and performance boundary

- current rendered DOM only;
- no `fetch`, XHR, WebSocket or `sendBeacon`;
- no local/session storage, IndexedDB, cookie or account state;
- no analytics emission;
- no third-party script or speech service added by Final Vestige;
- no voice enumeration;
- no article/source/citation rewrite;
- narration is created only through the browser/device `SpeechSynthesis` interface after visitor activation.

## Frozen source/build identity

The exact head SHA is frozen only after all branch files are committed and CI runs on the pull request. The governed payload identity for this R1 candidate is:

- `payloads/listen-mode-wp-block-r1.txt`
- 13,303 bytes
- SHA-256 `d627607ed5cda5ae6eed5fc972bf83da73d9f70c64e8cb8fd51e40220a810f92`

## Delivery boundary

This is a source/build repair candidate created from then-current `production`. Green CI is evidence, not approval. Do not merge or deploy this artifact. Independent QD must review the exact frozen PR head plus payload/test/workflow identity. Any code, test, workflow, contract or payload change after the freeze creates a new identity and requires fresh QD.

If QD PASS later requires executable Site Layer integration, rebuild from then-current `production`, preserve the passed narration and adversarial contract, freeze a new executable SHA/package, run fresh feature and repository CI, and return that new identity to QD before the existing FAST APPROVAL → Chief of Staff → FVS Execution Dispatch path can act. Live destination readback remains mandatory before `IMPLEMENTED + VERIFIED`.
