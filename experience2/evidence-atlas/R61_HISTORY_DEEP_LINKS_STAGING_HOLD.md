# Apollo R61 — source-preserving browser-history deep links (STAGING HOLD)

## Why
When a reader searched the original R38 Research Desk for one of six NASA references, a pasted fragment URL or browser-history transition to a different **Research Desk** record could target an article still `hidden` by that search. R60's Atlas hash handler restored Atlas records, but ignored Desk fragments unless the reader clicked an enhanced Atlas-to-Desk shortcut. The document's original records were present in the DOM yet not visible at the destination.

## Implementation
- `atlas.js`: a source-validated `onDeskHash()` branch handles only the six exact `#fv-ex2-ledger-apollo1-record-0N` identifiers. It validates all six NASA URL/catalog associations against the immutable crosswalk, clears the original Desk's active search with a native `input` event only when needed, and focuses the restored original article for keyboard and screen-reader continuity. If provenance does not match, it withdraws optional shortcuts rather than synthesizing source content.
- Suite integration (`0.0.61-staging`) pins the new exact Atlas JavaScript Git blob before enqueue; existing Research Desk R38 bytes, NASA source metadata, published WordPress and homepage code remain untouched.
- Does not manufacture source geography, assert a historical link between photos, embed images, or clear image rights.

## Acceptance
- `python -I -m unittest discover -s tests -p 'test_*.py' -q`: **94 tests, 93 passed, 1 skipped** in the isolated original-source package.
- `python test_atlas.py`: **11/11 passed**.
- `python tests/browser_r61_hash_qa.py --output /path/to/qa-r61`: **16/16 Chromium cases** at 320/360/390/428/768/1024/1440/1920 CSS pixels, JS on/off, touch<=390, reduced motion. Tests actual pinned R38 source and compiled Atlas through R59's PHP WordPress API simulator; validates hidden Desk record reveal, programmatic focus, browser back and Atlas hash restoration, six original sources, printing all 30 Desk and 54 Atlas custody values, no external requests or page JS errors. Two reproduced screenshots have SHA-256s in receipt.
- R60 original-source accessibility regression: **16/16 passed**; min target 44px, native details keyboard focus preserved.
- `node --check atlas.js`, `php -l integration/fv-ex2-apollo-suite.php`: passed.
- Deterministic archive generator: repeat builds must match exactly; all archived data rehashed.

## Release blockers / limitations
- **Not authentic installed WordPress/Assembler QA**: controlled PHP API simulator is used; early stylesheet behavior needs private WP read-only acceptance.
- **Axe-core not run**: no independently SHA-verified local axe bundle. CDP AX-tree results are not an axe substitute. Manual NVDA/VoiceOver testing is not complete.
- Lab fragment measurements are not production p75 LCP/CLS/INP; live performance release criteria remain open.
- All six NASA photo rights decisions remain pending and record 01 S67-19766 source-photo catalog attribution remains provisional. No photographs embedded, no map pins.
- Independent QD, green CI on the exact R61 head, editorial approval and production change authorization are outstanding. **Do not merge, install, publish or deploy.**
