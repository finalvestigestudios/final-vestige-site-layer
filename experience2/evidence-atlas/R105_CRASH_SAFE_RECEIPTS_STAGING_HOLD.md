# Apollo R105 — crash-safe genuine WordPress evidence receipts (STAGING HOLD)

Project: Issue #150. Parent: draft R104 PR #866 at `ba8ed9e854c91e732c326b947bfa9c5f97848c0e`; separate from Research Desk PR #158 and frozen homepage PR #49.

## Finding and corrective implementation

R104 originally wrote its authoritative browser QA JSON **only after all test cases passed**. Its workflow uploads the evidence directory with `if: always()`, but a Playwright timeout, axe violation, third-selection mismatch, failed LCP gate or PDF integrity error would leave no structured partial evidence. Combined with GitHub Actions' observed pre-runner failures (no steps, logs or artifacts on runs 41749195374 and 41749195469), this is a reproducibility and incident-triage gap.

R105 adds `qa_receipt_r105.py`, a compact atomic evidence journal, and hooks it into the real-WordPress `browser_real_wp_gallery_r104.py` acceptance harness. It creates `R105_QA_PROGRESS.json` at the start and advances stage checkpoints for each of 10 responsive/no-JS browser cases, two selected-state axe scans, and six repeated WordPress-core LCP/CLS trials. Numerical performance observations are written **before** their thresholds are asserted. If the browser run fails, the journal preserves the last checkpoint and a **type-only** exception marker; it does not serialize raw Playwright exception text or browser secrets. A temporary file is fsynced and atomically renamed into place so partial JSON is never treated as evidence.

The `completed` status is only written after R104's full matrix and new evidence validation pass: 10 browser cases, 2 zero-violation axe scans, six performance trials with unchanged LCP <=2500ms / CLS <=0.1 budgets and a recorded LCP at each tested viewport, four screenshot checksums and one PDF checksum verified against actual files. Regardless of status, `release` remains `STAGING_HOLD`. Individual NASA photo usage remains **0/6 cleared**; no photos, inferred geo pins, or unsupported edges are added.

## Verification and limitations

Eleven hermetic unit tests cover interrupted runs, failed states, tampered receipts, missing LCP, performance gate violations, stage sanitization, crash-safe writes and completed-status integrity. The equivalent locally prepared module/tests executed successfully on Python 3.11 on 2026-11-03; the exact GitHub branch must still pass its own unit and real WordPress CI. The workflow now checks compilation and runs the new adversarial tests **before** expensive WordPress provisioning. The workflow retains `if: always()` artifact upload and uses the same disposable WordPress 6.8.3 infrastructure.

**Known CI blocker:** Last R104 attempts returned pre-runner GitHub Actions failures with zero executed steps/artifacts and 404 absent logs. R105 cannot make a never-started runner produce evidence. Re-run exact-head CI when the runner dispatch service is restored; do not report either R104 or R105 real WordPress acceptance as passed until a genuine workflow finishes and artifacts are inspected.

## Explicit hold

This is QA infrastructure only. No WordPress content/settings writes, production/hosted CMS contact, merge, deployment, plugin activation outside CI, paid services, photo embed, speculative geography, or homepage branch modifications are authorized. Hosted WordPress.com/Assembler, manual screen reader and physical device checks, source rights, provisional S67-19766 identity, QD/editorial and founder approval remain outstanding.
