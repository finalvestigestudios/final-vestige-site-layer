# R180 — Policy Delta cross-script look-alike evidence (draft; release HOLD)

## Scope
Policy Delta Desk can expose visually near-identical **Latin/Cyrillic/Greek single-codepoint substitutions** that ordinary diff viewers may miss. It uses an explicit, conservative list of glyphs; it is **not** a comprehensive Unicode spoofing/confusables scanner or a claim about language, fraud, legal meaning, equivalence, or compliance.

A reviewer comparing a local policy where ASCII "PAYMENT" became "PАYMENT" (second letter Cyrillic U+0410) sees source-owned evidence:
Look-alike hunk 001: before L1; after L1; column 2 U+0041->U+0410; human review.

The original escaped diff, physical source lines, filenames, and exact SHA-256 hashes remain authoritative. This metadata contains only line numbers, 1-based columns, and numeric codepoints; **never private line text**. There are no network requests, telemetry, AI classification, or source rewrites.

## Determinism / boundedness / conservative pairing
- A candidate is formed only for changed lines in the **same existing unified diff hunk** with identical explicit look-alike skeletons but different raw codepoints.
- Require a unique source-line match on both sides. Ambiguous duplicate skeletons are omitted (not guessed); unrelated substantive changes are not labeled look-alikes.
- Only first 16 uniquely paired changed lines are shown, with a count for the rest. Only first 8 changed codepoint positions are shown per pair, with a count for the remainder. Lines exceeding 4,096 characters are ignored by this supplemental detector; the ordinary diff still carries their exact content and coordinates.
- The allowlist is intentionally incomplete and has no external Unicode database dependency; a missing alert **never** establishes absence of look-alike risk.
- The engine never declares intent, identity, equivalence, legal status, or approval. Compliance review remains human-controlled.

## Verification and release gates
- 27 synthetic adversarial unit methods; executed in an isolated Linux/Python environment, both normal and optimized -OO (54 focused executions). Verify copied local files against connected GitHub blob hashes before attributing that result to a commit.
- Seven additional synthetic real-file integration tests are committed for source hashes, before/after coordinates, mixed changes, no-clobber outputs, and rejected unsafe input. **These seven remain unexecuted** until exact-repository CI/Windows execution can be obtained.
- Strict runner products/desktop/scripts/safe_unittest_r180.py requires all **34** tests with no skips, twice on Ubuntu and twice on Windows in .github/workflows/desktop-build.yml. Do not describe CI as passing without an allocated runner.
- Manual Windows 11 accessibility observation is still required: keyboard/screen reader should surface the full numeric before/after codepoint cue and human-review disclaimer; contrast and navigation checks are independent of unit tests.
- No changed permission to distribute: all six EXEs remain internal candidates. Defender/EDR, native build/smoke, code signing, protected premium access, independent QD review and explicit founder authorization remain mandatory.

## Review checklist
1. Confirm the list is conservative, case-sensitive and narrow; examine Cyrillic and Greek look-alikes separately with human language context.
2. Confirm no original policy text enters the cue, and no canonical/NFKC changes are mislabeled as cross-script substitution.
3. Verify seven real-file integrations and all inherited tests on the exact branch once Actions runner allocation resumes.
4. Ensure WordPress/public Labs and unrestricted premium URLs remain untouched.
