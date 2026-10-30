# R69 — Fail-closed premium review report switching (unreleased)

## Customer-facing failure mode
The two premium tools let a reviewer load a generated exceptions CSV from the review workbench. Previously, a failed attempt to load a different report (invalid CSV, corrupt journal, or expired entitlement) displayed an error but **retained the previous report's actionable exceptions and journal**. A reviewer might then click Record or Export without realizing that the attempted switch failed. No decision was automatic, but the visible queue and evidence context could be mistaken.

## Source-level fix
`ReviewQueue` keeps report, validated batch, and associated journal as a single in-memory selection. Each attempt clears that selection **before** validation. New references become available only after `read_cases` and `latest_states` both succeed. `review_ui.open_review_window` also clears the report field and Treeview on attempted switches, including denied authorization, and never dispatches a review/export/seal operation against stale stored evidence after a failed load. Explicit Browse of old reports remains possible when their report and journal pass fresh validation. This change does not alter the signed entitlement, decision semantics, local JSONL review format, encryption contract, or payment approvals.

## Testing and release boundaries
Headless synthetic tests exercise successful replacement; failed CSV, journal and product checks; no partial state; recovery; and no disk writes. GUI integration must be verified on Windows 11 x64 with keyboard and screen-reader access. Follow the full original repository regression suite in normal Python and `-OO`, the six-executable release candidate gate and independent QD review. This is source code only, **not a released or independently Windows-tested app**.
