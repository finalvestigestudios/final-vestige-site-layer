# Labs R170 — One review classification per invoice source pair

**DRAFT / RELEASE HARD HOLD.** This source-only change is not an executable
release, a fraud/compliance finding, or an authorization to pay an invoice.

## Defect / threat model

The R169 report API \`attach_invoice_provenance\` stored its duplicate key as
\`(status, frozenset((row_a, row_b)))\`. Consequently a direct caller could
submit the same two **physical CSV rows** once with
\`exact_invoice_key\` and again with \`review_possible_duplicate\`.
Both candidates obtained distinct, SHA-bound, plausible-looking locator IDs.
A report consumer could double-count or draw contradictory conclusions about
one pair. The normal \`candidate_pairs\` engine does not intentionally generate
both statuses for one pair; a direct report caller, retry/merge bug, or tampered
intermediate object can nevertheless create that contradictory input.

## Implemented invariant

* For a given report, each **unordered physical-row pair** occurs at most once,
  regardless of orientation **or** review status.
* Both same-status duplicates and cross-status conflicts now fail with a
  generic, privacy-safe ValueError **before any report is returned**. No
  partial audit report is accepted.
* Different pairs may legitimately share one source row and have different
  statuses; those are still preserved as separate review candidates.
* Candidate references for valid rows keep the exact prior SHA-256 domain,
  locator format, source digest binding, orientation and status sensitivity.
  Source rows are copied from native dict storage as in R169; original input
  records are never mutated. Other report fields remain unchanged.
* This is **human review evidence only**; a locator hash is not a signature,
  proof of source authenticity, a payment approval, or a fraud finding.

## Automated verification

Source tests: \`products/desktop/tests/test_invoice_conflicting_pair_r170.py\`
(22 exact synthetic test methods). A strict redacted test-inventory gate at
\`products/desktop/scripts/safe_unittest_r170.py\` fails on missing/skipped,
failing or unexpected-success tests.

Run from the repository root:

\`\`\`sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r170.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r170.py
\`\`\`

\`.github/workflows/desktop-build.yml\` requires both modes on Ubuntu and native
Windows. **Planned** focused executions: 22 × 2 modes × 2 operating systems
= 88. Do not claim they passed without the exact-head CI result. Existing
six-engine full regression suites and six internal Windows x64 candidate
smokes remain required. The CI uploads only source/evidence metadata, not
executables or premium packages.

## Review and release boundary

This branch is stacked on draft R169, never directly on \`main\` or production.
No premium unlock, telemetry, source upload, balance mutation, new payment
decision, WordPress change, public link, or site release is introduced.
Independent *physical* Windows 11 46-observation accessibility review,
actual Defender/EDR evidence, code signing, authenticated premium delivery,
independent QD exact-head review, and founder authorization remain HARD HOLD.
