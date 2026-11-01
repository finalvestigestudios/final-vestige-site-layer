# R97 — Visible original-source label rendering for LedgerDiff and GrantAudit

**DRAFT ENGINEERING ONLY. No desktop binary, paid entitlement, website download,
payment approval or compliance determination is authorized.**

## Evidence presentation defect

The shared `review.labels_for_report` previously concatenated raw imported
source labels using the same semicolon-space delimiter used to separate distinct
labels. A source identifier containing `; ` could masquerade as two labels.
A bidirectional override, embedded CR/LF, blank Unicode glyph, or visually hidden
Unicode character could also make the report appear different from its original
input. Examples:

- One source ID `INV; 4` appeared as `INV; 4` (indistinguishable from two IDs).
- An actual U+202E inside `INV\u202E4` was invisible/reordered in some viewers.
- A literal typed `\\u202E` could be confused with an escaped control if
  literal backslashes were not encoded.

This was **human-facing report ambiguity**, not established fraud, wrong money
calculations, incorrect matching, or source tampering. The byte-accurate SHA-256
snapshots and physical CSV row citations remain the authoritative evidence.

## Change

`products/desktop/fvs_suite/review.py` reuses the existing offline
`audit_display.visible_source_text` for each label and encodes literal
semicolon characters as the four-digit `\\u003B` display token. The
rendered labels still have the original `raw_values` casefold-sort order:
**plain ASCII source labels remain byte-for-byte compatible**. Literal source
backslashes are doubled, distinguishing a typed escape from an actual Unicode
character. Hidden/bidirectional/blank Unicode is displayed visibly. No source
content is overwritten.

Only **display** columns change: LedgerDiff `left_ids`/`right_ids`;
GrantAudit legacy `claim_ids`, `ledger_ids`, `claim_programs`,
`ledger_programs`, `source_programs`; linked GrantAudit also includes
`ledger_reference_labels` and `related_claim_ids`. Normalization, matching,
grouping, human-review flags, precision, the publication boundary, source hashes,
physical row references and premium journal evidence are unchanged.

The report is **not a reversible serialization of source identifiers**:
ordinary leading/trailing whitespace is already trimmed by the current CSV
importer and `raw_values`. Investigate provenance-sensitive mismatches using
the original verified CSV snapshots and SHA-256, not the display text. Full
source-spacing custody is a separate future change and release-review item.

## Tests and verification gates

- `products/desktop/tests/test_source_label_visibility_r97.py` contains
  28 newly committed unittest methods, including 25 helper-level contracts and
  three repository-facing checks (LedgerDiff CSV-to-report and GrantAudit legacy
  bundle integration plus linked-label contract).
- Synthetic tests cover semicolon spoofing, bidirectional overrides, U+2800
  blank filler, literal escaped source strings, CR/LF/tab, variation selectors,
  raw source conservation, pre-existing sort order and unchanged collision /
  human review rules, plus 10,000 deterministic labels.
- Run **from full repository checkout**, in normal and optimized `-OO` Python:

  ```bash
  PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_source_label_visibility_r97.py' -v
  PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
  PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -v
  ```


- Actions run linked from issue #73 still fails **before any job steps**.
  Focused preflight outside Actions cannot establish complete integration.
- Native Windows 11 x64 six-executable startup, keyboard/screen-reader
  accessibility, signing/AV, checksums, offline privacy, premium authorization,
  clean-machine testing, and independent QD/founder approval remain mandatory.
  Do not merge or publish to work around Actions failures.

## Next highest-impact step

Owner: resolve Actions job-start issue #75, prove a real Linux source step
executes with logs, run all R97 tests and complete suite in normal and `-OO`.
Then test the six actual Windows executables and premium download gating.
