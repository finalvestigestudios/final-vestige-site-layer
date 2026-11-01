# R32 — Original source-fragment README custody and strict source inventory (DRAFT / HOLD)

Issue #136. Stacked on exact R31 head `268f89c792771f3f69fab013ec3a6af23b6812b1`. The 35 articles, 35 metadata records, water-planner, eight physical source inventories, 30 shared-URL groups, original reading-depth notes, 43 source fallbacks, and 1,959 citation occurrences are **unchanged**.

## Root cause: genuine hosted crosswalk-stage integration failure

R31 hosted run [#41257615583](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41257615583) advanced through checkout, pinned Python, native validation/build/unit tests, claim custody, rendered citation parity, high-consequence triage, and outbound-link custody; it then stopped at `source_crosswalk_truth`. In the exact R31 checkout, `preparedness/sources/fragments/` contains **seven** canonical JSON contributor inventories **plus** the tracked original `README.md`. The earlier crosswalk validator compared *every file* to the seven JSON names and rejected the legitimate documentation file as an unregistered source inventory. Authenticated GitHub directory enumeration independently established the extra README (blob `cec167dd6acaf9f6e92e87a61fa9aeacdad151a5`, 207 bytes). No source fragment was added by this sprint.

## Minimal fail-closed correction

- Treat `README.md` as **documentation, never an eighth source inventory**.
- Require it in the frozen 224-row archive, and pin its original Git blob SHA. A changed, missing or symbolic-linked README fails.
- Synthetic reduced-size fixtures may omit it; if they include it, it must match the frozen original exactly.
- Reject every other unexpected directory entry, hidden file, backup JSON, symlink or nested folder; do not indiscriminately ignore Markdown or silently normalize source URLs.
- Preserve the crosswalk's known food QA-fixture/non-author provenance alias as unresolved, without pretending author approval.
- Include the optional README blob identity in the deterministic HOLD receipt and its canonical audit fingerprint; no green release or human-review state is emitted.

The original README itself says contributor source IDs should be unique; the frozen archive still documents 15 repeated-ID groups across the inventories. This textual tension is **not** repaired by rewriting original documentation or collapsing sources. The existing machine/source identity and human-review gates continue to handle duplicate IDs and URL groups, and the text remains a human editorial-review issue.

## Testing and release policy

Synthetic regression coverage includes the original 207-byte README and pinned Git blob, no-source-loss inventory counts, report checksum determinism, draft-only state, source-file omissions, arbitrary extra files, unexpected directories, symlinks and byte-for-byte documentation tampering. The native test/build/preflight results must be verified on the **exact** PR checkout and reported separately.

**Status: RELEASE HOLD.** This is machine provenance custody only; no human source checks, no claim accuracy approval, no medically safe inference, no QD PASS, no publication. No WordPress, navigation, homepage, CMS, merging, or source/article modifications are authorized by this patch.
