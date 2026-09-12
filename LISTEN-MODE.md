# FVF-11 — Listen Mode

## Visitor job

Let a reader listen to a long Final Vestige investigation while retaining the story's section context and an on-page visual place marker, without requiring an account, external audio service, or a separate media edition.

## Final Vestige adaptation

Listen Mode adds one prominent **Listen to this investigation** launcher near the beginning of qualifying longform. After explicit visitor activation, a compact in-page player uses the speech synthesis capability provided by the visitor's browser or device to narrate the published story in document order.

The player provides:

- Play / Pause / Resume
- Previous and Next passage
- 0.8× / 1× / 1.25× / 1.5× narration rates
- a visible passage count and nearest section label
- a restrained bronze marker on the passage currently being narrated
- automatic scrolling only when the active passage leaves the useful viewport
- Escape or Close to stop narration and return focus to the launcher

Narration covers story headings and qualifying narrative paragraphs before the Sources & Further Reading section. Final Vestige footnote-marker numerals, source records, captions, navigation, forms, sharing controls, and existing feature UI are excluded from spoken text. Sources stay available in their normal published location rather than being flattened into the narration stream.

## Inspiration principle

- **Microsoft Edge Read Aloud** demonstrates that web narration is most useful when playback, skipping, speed controls, and visible follow-along remain attached to the page being read.
- **Firefox Reader View Read Aloud** demonstrates progressive enhancement: narration appears only when the operating system/browser has appropriate text-to-speech support.
- **Apple Safari Listen to Page** reinforces the value of simple page-level listen, pause, and resume controls on supported web content.
- **MDN Web Speech API / SpeechSynthesis** provides the technical model for device/browser-provided speech synthesis without a Final Vestige audio backend.

Final Vestige adapts those principles to evidence-rich longform: narrative-only playback, explicit source boundaries, section-aware progress, restrained visual tracking, and no voice-account or cloud-audio product.

## Qualification and failure behavior

The feature activates only on a single-post view with a recognizable Final Vestige Sources/References section, at least 12 qualifying narrative paragraphs, and at least 3,000 narrative characters before the source section. Native `speechSynthesis` and `SpeechSynthesisUtterance` support are required.

If any qualification fails, Listen Mode remains inert. If the browser/device speech engine reports an error, playback stops and a polite status message reports the failure. Closing the player or leaving the page cancels the current narration.

## Privacy and content boundary

- Final Vestige does not send article text to a speech service
- speech is requested through the browser/device speech-synthesis interface
- no browser persistence
- no cookies, fingerprinting, account, or server state
- no analytics emission
- no fetch/XHR/WebSocket/sendBeacon
- no third-party scripts
- no voice enumeration or voice-profile storage
- no article/source/citation mutation
- published article text remains the source of truth

The visitor-facing copy deliberately says the speech engine is provided by the browser or device; voice behavior can therefore vary by browser, operating system, installed voices, and device settings.

## Performance budget

- one isolated Gutenberg HTML payload
- 12,842 bytes uncompressed / SHA-256 `87e33999aed82a79992f4875ce22278202b55e5b545e70dfd806a2fac9b2fb99`
- zero Final Vestige network requests and zero third-party dependencies
- no pre-generated audio and no media download
- story segments are derived once from the already-rendered DOM
- speech begins only after explicit visitor activation

## Accessibility and responsive behavior

Listen Mode uses native buttons, a labelled region, 44px minimum targets, a polite live status, explicit playback labels, disabled edge-state Previous/Next controls, visible current-passage treatment, Escape dismissal, and focus return to the launcher. It does not automatically steal focus as narration advances. At narrower widths the sticky player becomes an ordinary in-flow player to avoid obscuring content. The payload includes 360px treatment, forced-colors support, reduced-motion behavior, and print cleanup.

Listen Mode is an additional listening convenience, not a screen-reader replacement; the original semantic article and all existing accessibility relationships remain intact.

## Delivery boundary

This branch is an artifact candidate based on the current inert `production` branch. It does not modify the Site Layer bootstrap/deployment runtime or any open feature PR and must not be merged merely because CI passes. Runtime-manifest integration waits for the governed deployment lane. Any later executable integration creates a new SHA and requires fresh CI + independent QD review before deployment and live destination verification.
