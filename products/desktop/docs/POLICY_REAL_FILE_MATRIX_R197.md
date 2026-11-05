# Final Vestige Labs R197 — Policy Delta real-file acceptance matrix

**Issue:** #73 · **Parent:** R196 draft PR #1010 at immutable `748a21f03cafe87bf60e4b0e2f463bc71de5f7fd` · **Release:** HARD HOLD (not production).

## Deliverable

Added `products/desktop/tests/test_policy_real_file_matrix_r197.py` with **21 synthetic, actual temporary-file integration tests** against the real `compare_policy_files` entry point. Each successful case writes a new report, checks raw input SHA-256 digests and original-byte preservation, and checks no temporary report residue. Error tests verify no misleading or half-published artifact.

The matrix checks:
- exact before/after physical line citations, two disjoint hunks, mixed Markdown/CSV file types;
- BOM-only differences, CRLF/LF differences, missing final newline and source hash continuity;
- Cyrillic/Greek look-alike candidates with deterministic physical citations; ambiguity suppression; NFC and NFKC human-review cues;
- invalid UTF-8, NUL, bidi/terminal-control text, embedded BOM, over-limit input bytes and line counts, symlinks;
- atomic publication fault cleanup, refusal to overwrite operator evidence, and display escaping for literal backslash versus invisible Unicode.

**No production algorithm changed in R197.** These tests put the previously repeated Policy Delta real-file acceptance blocker under automated regression. The cases use only synthetic sample data, never customer policy or financial records.

## Locally executed verification

- **Host:** Linux CPython 3.13.5, temporary isolated source tree. The six dependency files were copied byte-for-byte from the R196 GitHub commit and **their Git blob SHA-1 hashes were checked**:
  - `fvs_suite/policy_diff.py`: `cdd8df14782228548c42ae9e3534575179575036`
  - `fvs_suite/policy_confusables.py`: `0f89919bd07d48d1694e06f1035f501d1761eb08`
  - `fvs_suite/policy_canonical.py`: `1e1b047bb3b8a2bb8b77652892e4753b8e2b72a4`
  - `fvs_suite/csv_snapshot.py`: `108f330c46c536debff0b0303c5f7dc8f8c3f88d`
  - `fvs_suite/atomic_text.py`: `05513accbc7f76ddc9481b8644402aacbd7d8cec`
  - `fvs_suite/unicode_hazards.py`: `50801b3f168396b0e2c75e95352e435f7c936588`
  - `fvs_suite/__init__.py`: `a3e3f9fdeaf0f74f10077a7299f29f505dbe991f`
- **New test file Git blob:** `4120cf59a7485f6eb2f8c4073e4a8c01373f90dd`, matched GitHub after the commit.
- **Normal Python:** 21/21 PASS; no skips (0.039 s).
- **Optimized `python -OO`:** 21/21 PASS; no skips (0.031 s).
- **Total:** 42/42 focused local executions, with real temporary disk files and atomic publication. Compilation PASS.
- Red/green: initial test assertion for the legitimate diff header was corrected (test expectation only); no product code defects were claimed or modified.

To rerun after checking out this exact branch:

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_policy_real_file_matrix_r197.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_policy_real_file_matrix_r197.py' -q
```

## Holds / follow-on

**Not verified:** full inherited repository suite; hosted Ubuntu and Windows Actions; physical Windows 11 keyboard/screen-reader accessibility; Windows x64 packaged executables; Defender/EDR; signing; premium authentication and access gates. Prior R196 hosted run [#41938619026](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41938619026) reported two failed jobs with no recorded steps, so root cause is not established.

Keep this branch stacked on R196 draft PR #1010. Preserve the independent QD approval workflow and founder sign-off. No change to the live site, public links, release artifacts, compliance approval decisions, financial Decimal processing, telemetry, or premium access. **Next highest-impact step:** restore Actions runner allocation; run all inherited tests and this new 21-case matrix on Windows and Ubuntu; then build, checksum, scan and smoke-test six private x64 candidates before release review.
