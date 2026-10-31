# R17 — Deterministic shared-source custody and provenance truth

**Issue #136 | 2026-10-31 UTC | DRAFT / HOLD | may_publish=false**

## Material finding: the food source-head pointer is not the food contributor head

The current unpublished source crosswalk at the R16 baseline identifies:

- food source_head_commits pointer: \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`;
- actual **Claude food contributor branch** \`claude/prep-food-ccdc55\`: \`4b009361277ea1d4617b368f5d45104c7318b284\`;
- pointer \`e9cd7766...\` is the **separate draft synthetic-fixture test PR #169 head**, not the original contributor head.

Authenticated GitHub reads independently confirmed that \`preparedness/sources/fragments/food.json\` has the **same Git blob** \`a1f73c8170932d6b3192e9cd506686d516d23d30\` at the contributor head, QA #169 head and integrated R16 head. Thus the source content is byte-preserved **but the provenance label is misleading**. Do not silently rewrite the frozen crosswalk, silently merge QA #169, or claim that a fixture branch is the original contributor. The R17 checker explicitly surfaces this known non-author alias as **PENDING PROVENANCE RECONCILIATION**; any other unexpected source-head mismatch fails closed.

## Authenticated full-source read audit (not a native checkout execution)

At exact R17 draft commit \`559f987b48a04d21ac5ea8b468243963950baf7c\` (content unchanged from R16), retrieved \`preparedness/sources/crosswalk.json\`, \`register.json\`, and each of seven source-fragment files using the authenticated GitHub connector, checking repository-reported Git blobs against the crosswalk's 8 file manifests. All 8 match. Compared all 30 shared-URL groups against source-row identities, per-variant notes and reading limitations, with no drift detected:

| Structural inventory | Observed |
| --- | ---: |
| Physical contributor/base source rows | 224 |
| Distinct literal source URLs | 186 |
| Shared-URL groups (unresolved) | 30 |
| Source IDs with multiple physical variants | 15 |
| Unread source placeholders | 15 |
| Source-file SHA disagreements | 0 |
| Shared-group row/identity discrepancies | 0 |
| Source groups with documented human review | 0 |
| Known non-author source HEAD pointer | 1 (food / QA #169) |

This is a **structural custody audit**. It does not verify that a live source link works, that a source actually supports a specific claim, that a medical or emergency action is safe, or that a human reviewed it. The 1,959 citation occurrences remain separately gated.

The most frequently shared exact URL belongs to FEMA's power-outage PDF (four independently attributed source records). A match in URL alone must not collapse differences in reading depth or contributor-specific source-use explanations.

## Engineering

- \`tools/source_crosswalk_truth_gate.py\`: read-only, deterministic crosswalk auditor. Recomputes the physical 224-row inventory and literal 186-URL/30-group/15-duplicate-ID/15-unread-placeholder invariants; checks all 8 exact Git file blobs and row indices; verifies the original per-variant notes/reading limitations byte-for-byte by JSON semantics; rejects dropped or added group identities, source-URL redirection, collisions where one source ID is assigned different URLs, unexpected provenance head drift, forged approval flags, unexpected source fragments, symlink/out-of-tree inputs, HTTPS URL authority/whitespace/credential/port hazards, and false human-link checks. Builds a sorted, SHA-256-bound **30-group human-review queue** without granting review approval.
- \`tests/test_source_crosswalk_truth_gate.py\`: **67** isolated Python tests, including extensive deliberate adversarial mutations. In the complete repository they import the tool from \`preparedness/tools\`.
- Fix a discovered inherited R14 test defect: \`tests/test_outbound_link_custody.py\` previously loaded its tool from the **tests** directory while the real module resides in **tools**. This causes native discovery to error even when the isolated flat-folder tests pass. Corrected via a precise one-line path change; no production validator behavior weakened.
- No article, metadata, taxonomy, source-fragment, original crosswalk, homepage, WordPress, CMS, or navigation changes.

## Verification and required runbook

Locally executed from isolated copies of the previously developed R10–R16 modules plus the new R17 module:
\`\`\`bash
python -I -m unittest discover -s /mnt/data/fv-r17-dev/suite/preparedness/tests -p 'test_*.py' -v
# 655 tests, all passed — synthetic/adversarial engineering tests
\`\`\`

This **is not** the repository's complete native suite. The trusted private Git checkout remains blocked by local DNS resolution for \`github.com\` and \`api.github.com\`, and so the R17 CLI was not executed against the actual source files on disk. The authenticated connector full-source comparison above is a separate read-only check.

Required on a trusted checkout of this *exact* draft branch:
\`\`\`bash
python -I preparedness/tools/source_crosswalk_truth_gate.py --repo-root . > /tmp/preparedness-r17-source-custody.json
python -I preparedness/tools/qa_current_copy_concordance.py --repo-root .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

Review the R17 JSON for exactly one clearly disclosed food provenance alias and 30 unresolved groups; require independent human evidence review. A successful R17 exit code means **structural integrity only**, never publish permission.

## Coordination and release boundary

Frozen seven contributor heads independently rechecked and unchanged: START \`2122d856\`, SHELTER \`5daeaf2d\`, FOOD \`4b009361\`, HEALTH \`d2212d0\`, HIST-FOOD \`2acf65c\`, HIST-HOME \`f654e60\`, HIST-FIELD \`a5ce8a6\`. Independent QA #157 (\`7d1ae6b8\`) and synthetic-fixture #169 (\`e9cd7766\`) remain draft/unmerged; neither should be transplanted blindly. Homepage flagship PR #254 (\`8fa6fc52\`) remains out of scope and untouched.

**Release HOLD** until the complete trusted native validation, true citation/source-claim verification, 30-group human reconciliation, qualified safety review of consequential advice, hosted CI and independent QD review are complete. No public publishing, WordPress/CMS API writes, navigation changes, unsanctioned branch merges or false claims of medical/emergency safety.
