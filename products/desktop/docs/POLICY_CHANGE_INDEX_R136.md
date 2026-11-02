# R136 — Policy Delta Desk exact-line change index (DRAFT / RELEASE HOLD)

## Reviewer problem

Policy Delta already preserves raw source SHA-256 and a Unicode-visible unified diff, but a long policy comparison requires manually scanning diff hunks to locate each physical before/after edit. The new **Change index** adds a deterministic, human-readable navigation line for every diff hunk, including exact physical source lines touched by removal and addition.

**Illustrative report (synthetic):**

```text
Change index: 1 diff hunk(s); 1 removed source line(s); 2 added source line(s).
Line citations identify changed physical source lines, not legal clauses. A touched range can contain unchanged lines between edits.
Hunk 001: before L2; after L2-L3; -1 +2; mixed removal/addition; human review.

--- before "before.txt"
+++ after "after.txt"
@@ -1,3 +1,4 @@
 Context
-Old clause
+Revised clause
+Additional clause
 Footer
```

## Exact rules

- **One diff pass:** The index and display are built from the same `difflib.unified_diff` stream, not separate algorithms that might disagree.
- **Physical coordinates:** Counters start from the source's hunk header. A `-` fragment consumes one before line, `+` consumes one after line, unchanged context consumes one on each. The index cites first and last *changed* line on each side. A range can include unchanged lines *between* separate edits inside the same hunk.
- **Pure insertion/deletion:** The side with no changed source line reads `none`. The index does not invent a corresponding changed line.
- **Zero-change cases:** Identical bytes and BOM-only differences produce zero hunks, while existing distinct human-review notices remain.
- **Display privacy and integrity:** Exact raw-byte SHA-256, JSON-escaped filenames, safe Unicode visibility (bidi controls rejected; invisible glyphs escaped), original source bytes, raw diff hunk headers, CR/EOF notices, atomic no-overwrite output, and existing 10 MiB/50,000-line limits are retained.
- **Interpretation:** Mixed removal/addition is a **textual** classification, *not* a conclusion about an obligation, legal effect, payment eligibility, compliance, or fraud. Users must review both original documents. No premium entitlement, network, analytics, telemetry, or AI operation is added.

## Source and tests

- `products/desktop/fvs_suite/policy_diff.py` — diff-stream change indexing, zero/multi-hunk rendering, source-header line tracking.
- `products/desktop/tests/test_policy_change_index_r136.py` — **20** local synthetic real-file tests: replacement, insert/delete at boundaries, grouped/multiple hunks, unchanged context, empty source, BOM, CRLF, EOF, hidden Unicode, hashes, repeatability, validation, no-overwrite, and public engine integration.
- `products/desktop/scripts/safe_unittest_r136.py` — exact method inventory, zero-skips, privacy-redacted result. No source document text in CI diagnostics.
- `.github/workflows/desktop-build.yml` — mandatory **normal and optimized `-OO`** runs on both Ubuntu and Windows (target **80 named executions** at the exact candidate commit), plus all inherited source/native x64, sealed transfer, premium lock and accessibility gates.

## Limits and release custody

A hunk groups nearby text changes; it is not necessarily one regulatory section or one substantive revision. Coordinates refer to decoded physical lines in each immutable source snapshot, not to a document's printed pagination. A citation covers original input text; the report is a navigational aid, not a legal opinion or a canonical patch for reapplication.

**All six Windows x64 products remain UNRELEASED** until exact-commit CI succeeds, approved protected custody of real executables, 46 independent physical Windows 11 accessibility observations, real Defender/EDR assessment, signing, authenticated premium distribution, independent QD approval and founder release authorization. This code must remain in a draft feature PR stacked on R135. Do not publish binaries or alter production.
