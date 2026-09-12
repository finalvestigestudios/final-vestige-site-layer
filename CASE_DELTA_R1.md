# FVF-19 — Case Delta R1

Case Delta lets a visitor deliberately save a bounded browser-local snapshot of one published Final Vestige investigation and later compare the current published page against that saved snapshot. It is not an official publication history and does not infer why a change occurred.

## R1 repair scope

Independent QD found that the original candidate accepted one exact canonical Sources heading even when a competing partial Sources marker also existed in the same article. R1 adopts the hardened Visual Trail trust primitive: activation requires exactly one `article h2#sources.fv-source-heading`, and that exact element must also be the only in-article element carrying either trusted marker (`#sources` or `.fv-source-heading`). Any ID-only, class-only, mixed exact+partial, duplicate exact, earlier/later misleading partial, missing, reversed-footnote, or otherwise ambiguous boundary fails closed before Case Delta inserts UI or reads/writes its snapshot store.

R1 also applies the current nondestructive-DOM-state rule to `View current`. Scroll is attempted before any focusability/highlight mutation. Case Delta records whether `tabindex` and the focus class were already publisher-owned, adds only what it owns, restores temporary focusability immediately after the focus transaction, removes only a class it added, and leaves pre-owned/nondefault state untouched. Browser regressions exercise both an absent `tabindex`/class path and a pre-owned `tabindex="0"` plus pre-owned `fvcd-story-focus` path, including repeat jumps.

## Preserved product contract

- Explicit visitor action is required before a snapshot is stored.
- Storage remains browser-local `localStorage`, maximum six investigations, maximum age 120 days, and maximum 90,000 serialized characters per snapshot.
- The feature sends no snapshot or article text to Final Vestige and introduces no fetch/XHR/beacon/WebSocket, analytics, cookies, IndexedDB, clipboard write, iframe, external script, or history mutation.
- Story comparisons describe bounded structural/word-count change rather than claiming an official line-by-line editorial diff.
- Source snapshots remove citation backlinks and retain published source text/URLs already present in the article.
- Figure comparison remains bounded to published pre-Sources image metadata.
- Replace remains two-step; Forget removes only this page's saved snapshot.
- Native dialog labeling, focus return, 44px controls, responsive layouts, reduced-motion, forced-colors and print suppression remain part of the acceptance contract.

## Exact R1 artifact contract

- Target branch: `production`
- Source base: `3f7841a7c671f9e8e955b417480d853ad0a0a948`
- Payload: `payloads/case-delta-wp-block-r1.txt`
- Expected payload bytes: `21851`
- Expected payload SHA-256: `3144b3675a331b15d0aac6611c93fde67050577e4de348c88107309993e6eb04`
- Verifier: `tests/verify_case_delta_r1.py`
- CI: `.github/workflows/case-delta-r1-ci.yml`

## Browser/adversarial matrix

The exact payload is browser-executed against: valid canonical markup; ID-only; class-only; duplicate exact; exact+ID-only earlier; exact+class-only earlier; exact+ID-only later; exact+class-only later; reversed footnotes; insufficient narrative; insufficient sources; blocked storage; absent focusability/class state; and publisher-owned focusability/class state with repeated `View current` interactions.

## Governance

This is a source/build repair candidate only. Green CI is evidence, not QD approval or merge/deploy authority. Freeze the final PR head after all repository changes, run the dedicated Case Delta R1 workflow and repository-wide Site Layer CI on that exact head, then return the exact head SHA, payload identity and CI evidence to independent QD. Do not merge or deploy before that exact identity is QD-cleared and routed through the governed release path. No whole-site launch/indexing, private-user processing, spending/payment, account/permission change, public Scout release or other separately gated action is authorized by this artifact.
