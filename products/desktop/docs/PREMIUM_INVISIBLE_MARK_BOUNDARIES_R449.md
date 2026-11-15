# R449 — premium evidence display-ignorable combining marks

**Status: DRAFT / NOT APPROVED FOR RELEASE** · Issue #73 · parent R448 draft #2612.

## Defect, change, and tradeoff

`canonical_evidence_label` previously refused Unicode `Cf` formatting controls, but permitted certain **invisible `Mn` combining marks**. A pathname such as `report\\ufe0f.csv` (variation selector-16) and `report.csv` can appear similar to a reviewer while encoding different manifest labels. The existing SHA-256 checksums remain correct, so this is an *evidence-label clarity* issue, not a demonstrated hash bypass.

The shared label validator now refuses U+034F (combining grapheme joiner), U+180B–U+180F (Mongolian variation selectors), U+FE00–U+FE0F (BMP variation selectors), and U+E0100–U+E01EF (supplementary variation selectors). Do **not** reject all `Mn`: visible combining accents like `e\\u0301` are supported. GrantAudit Studio Pro and ProcureGuard Studio Pro both use the helper for inventory pre-hash writer validation and post-publication verification. No source files are renamed, edited, uploaded, or rewritten. Money logic, SHA-256 semantics, report review policy and approvals are unchanged.

These are explicit narrow Unicode exclusions rather than a claim of complete Unicode spoofing resistance. Existing files/inventories with excluded characters require **human-reviewed copy/rename and regenerated evidence**; never silently rewrite a financial report or deem it noncompliant on this basis.

## Test plan and evidence boundaries

- Focused standard Python: `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_premium_invisible_marks_r449.py`
- Focused optimized Python: same command with `python -OO -W error`.
- End-to-end synthetic writer/verifier: `python -W error -m unittest discover -s products/desktop/tests -p test_premium_invisible_marks_integration_r449.py` (repeat with `-OO`).
- Inherited evidence custody: `test_evidence_labels_r446.py`, `test_windows_evidence_basename_r447.py`, `test_premium_manifest_link_custody_r448.py`, `test_premium_manifest_completion_r254.py` and `test_premium_inventory_stability_r255.py`.

Focused tests exercised locally against a Git-blob-matched baseline helper plus the proposed updated file (record exact totals in issue and PR). **End-to-end/inherited full repository tests remain unexecuted** until CI/repository execution is available. The GitHub Actions runner-assignment failure must be diagnosed from annotations, billing/spending and runner policy; no passing hosted CI or native Windows binary is implied by focused local checks.

**Release hold:** No EXE, license, download URL, payment flow, WordPress publication, public artifact, CI bypass, QD self-approval or production merge. Require complete six-app source tests, genuine Windows x64 build and Defender/smoke/accessibility checks, SHA-256 release hashes, private premium delivery/access verification, independent QD review and explicit founder approval.
