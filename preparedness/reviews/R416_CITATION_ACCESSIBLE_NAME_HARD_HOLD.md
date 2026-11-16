# R416 — Preparedness citation accessible-name provenance (DRAFT / HARD HOLD)

**Owner scope:** Final Vestige Preparedness Archive source/citation safety gates, Issue #136. Commercial attribution decision Issue #820, charter #818. **No public release or automatic qualification.**

## Evidence gap and remedy

The predecessor R415 binds original inline source IDs, URLs, labels and source positions to paired WordPress-ready/private-preview draft HTML, but does not inspect overrides to accessible source names or keyboard/navigation behavior. An otherwise unchanged source anchor can acquire `aria-label="Federal agency certifies this as safe"` and remain structurally acceptable under R415 while announcing a different link name to assistive technology. That is particularly misleading for emergency/food guidance and creates a source-identity trust gap.

R416 adds a read-only parser that rejects conflicting `aria-label` or `title`, unvalidated `aria-labelledby`/`aria-describedby`, misleading `role`, arbitrary positive/negative `tabindex`, named `target`, `aria-current`, editable/draggable source links, unsafe `referrerpolicy`, duplicated attributes and unisolated new-window links. It checks BOTH export streams and maintains original R415 HOLD, manuscript candidates and all source graph invariants. Identical normal names are allowed; context-dependent external labels require human adjudication rather than silent approval.

## Local test receipts (execution scope)

- **74/74 new tests passed**: `python -I -m unittest discover -s preparedness/tests -p 'test_r416*.py' -q`.
- **560/560 combined tests passed** (74 new + 486 inherited): `python -I -m unittest discover -s preparedness/tests -p 'test_r4*.py' -q` (29.289 sec, exit 0).
- Python compilation PASS.
- Source blob SHA `2a1eefa3ed1caf8720b4877aa811a7f31470bdc9`; test blob SHA `99a2b15dd0a243166523face3075fdafa5e43a39`, independently recomputed locally, remotely compared after branch write.
- R415 accepts a synthetic visually unchanged `aria-label` with a fabricated agency safety-approval message; R416 rejects it.
- Tests are local synthetic 35-article fixtures, **NOT** authenticated original 35 manuscripts, native build, genuine paired WP/preview exports, browser/assistive-device test, safety adjudication, QD or production CI.

## Coordination and release boundaries

Original R397 docket: 35 article identities, 77 original paths, 203 source IDs, 280 source occurrences, 17 duplicate exact-URL review groups, 5 unresolved source-scope decisions, 9 unselected Shelter forks. Its seven Claude + two Shelter pinned refs were independently compared 2026-11-16 and each is identical (0 ahead / 0 behind). QA #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture QA #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, dependent #2205 at `bbcf1859768624c611df4abadc564c18247cf32a`: inspected without mutation. #169's separate duplicate-source fixture correction in #2205 stays draft.

**Commercial HOLD:** A genuine FV-owned or licensed payable Preparedness pack, rights, seller acceptance, checkout, delivery, refunds and fees have not been authenticated. Only the already-public free agency-linked /preparedness/ route is a *proposed* destination for a currently unauthenticated published family-contact social asset. Neither Tool #104 nor any retired water download is approved. No identified paid orders, net revenue or 7/30-day attributed cohorts. Grok produces/posts; Praxxis independently checks assets/TASK-008; Claude owns site/analytics; founder releases/spends.

**No merge, WordPress/CMS/navigation write, social post, affiliate or merchant activation, analytics script, email, spending, QD PASS or medical/food/emergency advice clearance.**
