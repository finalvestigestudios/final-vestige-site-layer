# R402 — Policy Delta Desk exact Unicode spacing-mark custody

**2026-11-13 | Issue #73 | DRAFT, QD + founder HARD HOLD.**
Scope: **Policy Delta Desk only**, one of the four free Final Vestige Labs desktop utilities. No premium entitlement, six-app deployment, WordPress publication, matching/amount rules, or automated compliance decision changed.

## Source-level defect and correction

Policy Delta Desk's \`_visible_source_char\` escaped Mn/Me combining marks but not Unicode **Mc** (spacing combining marks). In Unicode source lines, Bengali \`ক\u09cb\` (composed) and \`ক\u09c7\u09be\` (decomposed) normalize to the same NFC string. Before this sprint, their **diff source rows were rendered using the original glyphs**, which may look indistinguishable in common fonts. The source SHA-256 and canonical navigation note already revealed that a change existed, but the primary human-readable diff did not expose exactly which spacing marks changed.

The display-only renderer now escapes **Mn, Mc and Me**, preserving the original source codepoints/bytes, physical line citations, source SHA-256, exact diff hunk coordinates, file immutability and no-clobber report publication. The report's legend has been updated to match. Escapes remain lowercase hex (\`\u09cb\` / \`\u09c7\u09be\`) in Policy Delta's preexisting format. Literal source backslash notation stays distinct (\`\\u09be\` vs actual \`\u09be\`). Regular ASCII and precomposed multilingual letters remain readable.

This is textual audit visibility, **not** legal interpretation, semantic equivalence, a fraud judgment or a full Unicode-confusable detector. Mc escapes can make some multilingual source lines more technical: reviewers must be able to inspect the originals.

## Synthetic evidence and test scope

- Narrow local isolated reproduction of prior renderer: Bengali U+09BE previously rendered as a glyph.
- Narrow local post-change renderer reconstruction, CPython 3.13.5:
  - \`python -W error isolated_mc_tests.py -q\`: **5/5 PASS**.
  - \`python -OO -W error isolated_mc_tests.py -q\`: **5/5 PASS**.
  - Enumerates **452 Mc codepoints on the local Python Unicode database** for escape expectations, plus nonspacing/enclosing marks, literal escape distinctness, multilingual compatibility and existing control escapes.
- The isolated harness is a **manually reconstructed function**, *not* the exact repository module or six-app checkout. Its 10/10 executions are **not** evidence that 15 committed end-to-end tests have passed.
- **15 committed real-file/application regression methods** in \`products/desktop/tests/test_policy_spacing_mark_evidence_r402.py\` require execution against the exact repository. These cover Bengali/Odia/Tamil canonical pairs; Devanagari, Myanmar, Malayalam; the full Mc category; physical hunk citations and NFC review; literal escapes; context lines; source SHA-256 and immutability; failed-source/no-overwrite paths; ordinary text; CRLF handling; disclaimers; and staged-file cleanup.
- The new test file's Git blob is checked against the locally authored test file with \`git hash-object\`. The complete integration suite was **not** executed locally.
- Independent Windows/Ubuntu source workflow now requires new R402 tests and inherited Policy R76/R78/R178 diff regressions in both normal and \`-OO -W error\` Python **when runners are available**.

## Required acceptance before release

1. Restore GitHub-hosted runner allocation; inspect job annotations, billing/spending and runner eligibility. Prior R401 source and build runs ended in failure with zero recorded test steps. This is an infrastructure observation, **not** a diagnosis.
2. Run the R402 exact-commit source jobs on Ubuntu and genuine Windows; confirm all 15 new integration tests and inherited R76/R78/R178, 6-engine financial/provenance, AES-GCM, Ed25519/SQLite and source smoke gates.
3. Run Windows x64 portable executables for *all six distinct launchers*, Defender checks and keyboard/screen-reader tests; validate gated premium distribution and owner QA. No binaries or premium links should be published before verification.
4. Obtain independent **QD review** and explicit **founder approval** before merging, deploying, publishing, licensing or making WordPress changes.

No executable or download was produced/published; all six apps remain unreleased.
