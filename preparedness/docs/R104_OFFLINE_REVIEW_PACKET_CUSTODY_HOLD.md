# R104 — Byte-exact offline source/citation reviewer packet custody (HOLD)

**Issue #136. PRIVATE ENGINEERING ONLY.** R104 follows R103 without merging or editing a single article, tool, author source, author reading-scope, taxonomy, review flag, WordPress body, homepage or navigation component. This stage is NOT QD approval or an emergency/medical-safety assessment.

## Why this additional gate exists

R102 provides the original 30 shared-URL groups and author-specific citation scope. R103 provides a printable static HTML dossier, separate CSVs of original source variants and citation occurrences, and an unapproved summary. A CSV or printed packet can subsequently be altered, truncated, reordered, copied with line-ending normalization, or presented as approved while still looking plausible. R104 independently reconstructs the authoritative source workorder from **two separate Library loads** and checks the complete exported bundle **byte for byte**. This includes warning language, all original citation ordering, unchanged quoted CSV fields, and a mechanically generated inventory manifest. A modified manifest with a freshly calculated SHA-256 value is still rejected.

SHA-256 is for accidental/tampering-detection **relative to the exact current independently replayed repository content**. It is not a digital signature, a trust anchor by itself, or proof that the underlying source/claim is true. An attacker with repository write permission can alter upstream sources and tests. Qualified human review and independently supervised release controls are still mandatory.

## Generated private packet

R104 generates five files in a pre-existing EMPTY directory **outside the repository**: the R103 printable static HTML, the R103 source-variant CSV, the R103 citation-occurrence CSV, the R103 summary JSON, and an R104 custody manifest describing all four artifact byte lengths, SHA-256 hashes, the 30 original group fingerprints, 35 complete articles, 1 complete water-planner tool, and 5 uncompleted planned tools.

All export names include HOLD or NOT-VERIFIED. No links, scripts, forms, public uploads, telemetry, network requests, CMS actions, sign-off controls or source edits are introduced. The script refuses to overwrite evidence, rejects symlink export files and directories, refuses output inside the repository, enforces a file-size ceiling, and verifies everything after creation. A strict verifier rejects extra/missing/renamed entries, truncation, rewritten CSV line endings, modified HTML warnings, altered citation data and forged manifest review status.

### Run on an exact checkout

Run only after confirming that the current seven contributor branches, release candidate, parent PR and QA PRs match the expected exact SHAs; never silently force an integration.

    python -I preparedness/tools/r104_review_export_custody.py --dry-check
    temp_dir="$(mktemp -d)"
    python -I preparedness/tools/r104_review_export_custody.py --emit-dir "$temp_dir"
    python -I preparedness/tools/r104_review_export_custody.py --verify-dir "$temp_dir"
    python -I -m unittest discover -s preparedness/tests -p 'test_r104_*.py' -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Remove the private temporary reviewer directory under your own secure file-retention policy. Do not move or copy these drafts to the WordPress CMS or website. Do not present an export hash as human factual review.

## Required human review and release HOLD

All **30** literal shared-URL collision groups remain independently unreviewed for current URL, exact edition/section/date, author-specific source applicability and each cited claim. Do not deduplicate them on URL or source ID. Preserve existing original safety states without promoting historic founder records to new independent qualified safety approvals. Five historical contributor-provenance discrepancies, 15 safety exceptions, 22 editorial choices, five unfinished tools, actual browser/print QA, relevant qualified medical/emergency review, independent QD and the complete mandatory 13-stage release pipeline remain open until verified otherwise on their own exact heads.

QA PR #157 and synthetic-fixture PR #169 remain independent, unmerged draft work; #169's other shared-repository fixture requires isolation before merge. Keep homepage PRs #49 and #604 unchanged. No release or public publishing is authorized by R104, even if its private CI and full regression suite pass.
