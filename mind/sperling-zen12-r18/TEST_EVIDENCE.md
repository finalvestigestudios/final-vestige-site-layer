# R18 exact-source audit evidence / 2026-10-31
**Branch:** `feature/mind-sperling-zen12-offer-integrity-20261031-r18`  
**Scope:** UNPUBLISHED. No external earning link, signup, analytics, subscription/WordPress write, deployment or merchant outreach.

## Executed verification
- Read **all eight previously committed GitHub source files** back from the active isolated branch through the authenticated GitHub connector. The `qa.cjs` pure `audit(files,matrix)` function was loaded/executed in an isolated JavaScript V8 environment on their exact returned UTF-8 contents; `EVIDENCE_MATRIX.json` parsed as JSON.
- **104 / 104 source contract checks PASSED**: investigation, A/B buyer-experience parity, text-only content, legitimate historical study source, disabled purchase controls, immediately proximate commission disclosure, no merchant checkout hyperlink in outward-facing HTML, no newsletter forms, no embedded Javascript, no analytics pixels, no autoplay, visible transcript, hidden review-only film source/poster/VTT and captions, Focus and Puységur routes, claim matrix source integrity/permissions flags, privacy-off and accessibility release requirements.
- **14 / 14 deliberately harmful adversarial source changes CAUGHT** in an independently executed V8 mutation pass: removal of earning disclosure, enabling CTA, inserting merchant checkout, injecting email collection, inserting third-party JS tracker, autoplay, unhiding unavailable video, removing captions, deleting free Focus path, turning the educational grid into a diagnostic claim, falsely approving partner, turning tracking on, falsely claiming actual product test, and falsely approving email rights.
- Initial source QA returned **102/104**, due solely to two over-literal text-contract anchors that did not match substantively compliant guide/plan wording; revised audit, then one unnecessarily strict 'No collection enabled here' literal produced **103/104**, and exact explicit privacy heading anchor was corrected. No original page or scientific claim was weakened to force a pass. Final exact source audit is **104/104**.
- Original previously produced 40-second portrait MP4 separately found in this run's review artifact files and independently rehashed with local `sha256sum`. **Actual 155,763-byte binary SHA-256**: `c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc`; prior PR #229 stated this exact hash. Local `ffprobe` returned H264, **540 × 960**, **40.000000 seconds**, 155,763 bytes. This verifies the original previously produced review artifact's technical identity, **not new first-party hosting, WordPress caption synchronization, legibility or browser accessibility**.
- A/B core editorial content equality: `PILOT_B_STAGING.html` is an exact copy of `PILOT_A.html` other than an explicit review-only top comment and the inserted hidden unhosted native media figure. This was checked at source generation and in the committed QA. The complete transcript remains visible in both variants.
- Machine-readable matrix: **60 individually dispositioned claims** and **15 exact research/merchant/regulatory/site URLs**, partner and earning link fail-closed.

## Exact GitHub blob SHAs independently fetched and tested
| File | Blob SHA |
| --- | --- |
| `INVESTIGATION.html` | `8419445cefbadcc706020b34b76348640f17cb85` |
| `ZEN12_BUYER_GUIDE.md` | `2b1ff7af9e770279639c693b81a72bfd06bef0ac` |
| `PILOT_A.html` | `b174b0bd5c3118b6251a8c96c4006130da9a95cb` |
| `PILOT_B_STAGING.html` | `c96723de4f1c4a451bbcc7fadf5526cb7ec35601` |
| `EVIDENCE_MATRIX.json` | `5cf6223fe206b211f09fd76f9a07bfe17915d1a7` |
| `EXPERIMENT_AND_RELEASE.md` | `3d399b330d52b079a1e9f18fc31af14c55b1f0d5` |
| `README.md` | `e3ba305c6b0d149d0c9833887bf625a760f2babc` |
| `qa.cjs` | `81eb1aab1779798d5acf8f109f8f6f2e405aa3f3` |

All eight files originate from the new `mind/sperling-zen12-r18/` path only; no previously existing repo file has been edited by this sprint. This document and the final branch README are documentation additions and are not represented as part of the eight-file executed QA set.

## Reproduce
```bash
node mind/sperling-zen12-r18/qa.cjs --mutation
```
The committed script includes a standalone Node runner that loads the source files and executes 104 static checks and a built-in subset of adversarial mutations. The executed full 14-case V8 mutation pass included four additional flag assertions not present in the Node runner. **Node checkout command was NOT executed in this environment**; the executed result is the isolated V8 audit on GitHub file readbacks.

## Not verified / required release HOLD
Hosted GitHub CI (status not represented as green), Gutenberg HTML retention, actual WordPress staging at 360/390/768/1440/1920, screenreader/keyboard/200–400% zoom, native caption timing and Safari playback, all-media performance/CWV/Lighthouse, first-party media hosting, independent editorial/QD scientific review, media-copy equivalence with the previously rendered exact film, legal/privacy requirements, affiliate acceptance, account-specific Zen12 SKU earning URL and allowed creative/social/email rights, and final founder publication/merchant-activation approval. **No production changes.**
