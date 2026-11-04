# R181 — Policy Delta Desk spoken Unicode character names (DRAFT / RELEASE HOLD)

**Scope:** Improve source-cited cross-script character review cues for screen-reader users, without broadening R180 detection or determining legal/compliance meaning.

Previously: "Look-alike hunk 001: before L1; after L1; column 2 U+0041->U+0410; human review."

Now: "Look-alike hunk 001: before L1; after L1; column 2 U+0041->U+0410 [LATIN CAPITAL LETTER A -> CYRILLIC CAPITAL LETTER A]; human review."

The local Python standard library Unicode names disclose a character's script and identity without asking the reviewer to decode U+0410 and without repeating confidential source text.

## Preserved invariants

- Names are public assigned Unicode metadata, not copied policy content. No telemetry, network access, external dependencies, changes to original files, or premium file exposure.
- The original source bytes/SHA-256, source-owned hunk and physical-line citations, escaped diff, and mandatory human-review caveats remain authoritative.
- Existing upper bounds of 16 unique line-pairs, eight displayed substitutions per pair, 4096 source characters per line and ambiguous-duplicate suppression are unchanged.
- Limited ASCII Latin/Cyrillic/Greek mapping only. This is not a comprehensive Unicode scanner, language classifier, fraud indicator, legal advice, or a compliance decision.

## Exact-file local test evidence — 2026-11-04

The local test mirror reconstructed R180's source and original 27 tests with Git blob hashes matching the existing GitHub files, then applied the R181 patch. Committed R181 source blob: 44264ae891bff252c1712ac1d355f26f459790c7; new 25-test blob: fd60003a5e9bd4fd3530ac8278620bcc72eb8054; strict runner blob: 67867e449cc4f43ae28f5dda06e59df11d44d852.

- R181 strict 25-case unit suite: 25/25 PASS normal Python and 25/25 PASS optimized Python (-OO), with zero skips or errors.
- R180 existing 27-case unit suite: 27/27 PASS normal and 27/27 PASS optimized (-OO) on the R181 module.
- Total: 104/104 focused local Linux method executions; Python compilation PASS. This is not the full repository test suite, the seven inherited R180 real-file integrations, real Windows builds, or physical accessibility acceptance.
- Source workflow now schedules four R181 25-method executions (Ubuntu/Windows, normal/-OO), 100 method executions once GitHub runners allocate. These are not yet verified CI results.

## Required acceptance / explicit HOLD

Run inherited suites and R180 integration against the exact branch on Ubuntu and Windows; internally package and smoke-test all six Windows x64 programs. Before publication require physical Win11 46-observation keyboard/screen-reader evidence, genuine EDR/Defender checks, code signing, secure premium delivery, independent QD review and founder authorization.

Do not merge into production, publish downloads, expose premium executables, or assert release until verified. Owner should inspect the GitHub Actions pre-runner failure banner, billing/usage and runner provisioning, restore allocation, and rerun the unchanged commit.
