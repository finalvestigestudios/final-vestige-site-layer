# Case Packet R1 — live citation contract + source-note provenance repair

## Scope

This is the bounded successor candidate to the original Case Packet v1 artifact in PR #19. The original four governed v1 files remain preserved for review history; **R1 is the only current Case Packet release candidate** and must be reviewed by its own exact PR head identity.

R1 changes no Final Vestige editorial content and performs no WordPress mutation. It remains an inert Site Layer candidate until a later governed executable integration is derived from then-current `production` and receives fresh CI, independent QD, merge/deployment authority, and destination verification.

## QD defects repaired

1. **Wrapper-independent citation contract.** Runtime discovery now uses the governed live anchor contract `.fv-fn-ref[data-fv-fn]` directly. It does not require `sup.fv-fn-mark`. Paragraph/source selection and packet citation normalization use the same anchor contract. The browser suite treats wrapper-free markup as the primary valid fixture and legacy wrapper-present markup as a compatibility fixture.
2. **Published source-note text fidelity.** Case Packet no longer removes external anchors from cloned source notes. Backlink/script/style utility nodes are removed; remaining anchors are converted to their visible text so semantic linked wording survives in the packet.
3. **Deterministic external-link handling.** Source links are extracted from the original source note in DOM order, excluding `.fv-fn-backlinks`, relative URLs, same-origin URLs, malformed URLs, and duplicates. At most four external HTTP(S) links are surfaced per source note. Visible anchor labels are preserved.
4. **Adversarial browser fixtures.** R1 tests wrapper-free and legacy wrapper-present citations; semantic external-anchor text; two legitimate external links in deterministic order; same-site, relative, and backlink utility URL rejection; selected-section/source filtering; focus return; and the existing ambiguous/partial/reversed/duplicate/missing/insufficient source-boundary fail-closed cases.

## Exact R1 payload identity

- Payload: `payloads/case-packet-wp-block-r1.txt`
- Bytes: `20,410`
- SHA-256: `2b661516a5932a0e4d50c183aba25eec306d8163b10017069104777d5ef8b90c`
- Verification: `tests/verify_case_packet_r1.py`
- Workflow: `.github/workflows/case-packet-r1-ci.yml`

Any change to the payload, verifier, workflow, contract, or PR head after QD review invalidates that review identity and requires a fresh exact-head review.

## Live compatibility read

A fresh WordPress read of published post 621 (`Six Miles an Hour`) on 2026-09-11 confirmed the current article still has one canonical `h2#sources.fv-source-heading`, one later `[data-fv-footnotes]` list, and current citations rendered as `.fv-fn-ref[data-fv-fn]` anchors inside `.fv-fn-mark` wrappers. R1 deliberately supports that current wrapper-present shape **and** the governed wrapper-independent anchor contract so a harmless wrapper change cannot silently disable the feature.

## Privacy, performance, and accessibility boundaries

- Current DOM only; no fetch/XHR/WebSocket/sendBeacon.
- No cookies, local/session storage, IndexedDB, analytics, behavioral profile, or third-party service.
- No image duplication; figure references use already-published caption/alt text only.
- Source-page URL is normalized to same-origin path without query or fragment.
- Native dialog; Escape/cancel behavior and focus return; 44px controls; mobile full-screen dialog; 320–360px handling; forced-colors and reduced-motion support; print-specific output.
- Case Packet remains a reading/research aid. It does not infer citations, rate evidence, establish confidence, create a revision history, or create a separate edition.

## Governance / identity hygiene

The canonical Website Feature Ledger identity **FVF-20 belongs only to Case Packet**. `Source Route` is a separate pre-ledger/control-plane feature candidate and must not use the FVF-20 label. Source Route's existing Decision/Handoff records must be relabeled as `Source Route — provisional feature identity` (or assigned a future canonical ledger ID only by the ledger process) before R1 can satisfy its control-plane acceptance condition.

## Release gate

R1 is not merge/deploy authority. Required sequence remains: exact-head R1 CI SUCCESS → independent QD on that exact head → preserve separate bootstrap/founder gates → later executable integration from then-current `production` → new SHA + fresh CI + fresh QD → governed merge/deploy → live desktop/mobile/zoom/keyboard/focus/source-integrity/print/network destination verification → only then `IMPLEMENTED + VERIFIED`.
