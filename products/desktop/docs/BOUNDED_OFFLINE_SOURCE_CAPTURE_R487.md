# Final Vestige Labs R487 — hard-bounded offline source-check output (DRAFT / QD HOLD)

## Verified change
Stacked on R486 draft PR #2814 at `0824728380cebfff981b5c6e8f7b19ba081db6a9`, **not `main`**. Applies to the operator-only source regression fallback used to review all six standalone Windows x64 utilities (four free and two premium). No financial engine, premium entitlement, executable or WordPress content is modified.

The R486 gate discarded logs over 1 MiB **only after** `subprocess.run` finished. A noisy or hung test could write an unbounded disk-backed temporary log for up to its 600-second default timeout, including sensitive failure messages. The gate could deny PASS but not cap the resource use during a run.

R487 replaces the disk spool with a bounded parent-side pipe reader. It buffers **at most 1,048,576 bytes** in memory and kills the child on the first over-budget chunk; all captured bytes from an overflowing child are discarded. A dedicated reader drains stdout and merged stderr while the process runs, avoiding normal pipe backpressure deadlocks. Silent child timeouts are killed and reaped. Failure outcomes are still limited to fixed labels, count and mode. The existing R486 terminal unittest receipt checks, skipped-test rejection, linked-file custody and fail-closed `release_authorized=false` are preserved.

**Limits:** This bounds the parent-side captured stdout/stderr, **not** arbitrary file writes, descendant processes or subprocess resource usage, and is not a sandbox. A malicious trusted-checkout fixture can still forge its own unittest text. A descendant retaining a pipe open can cause a BLOCKED result; native Windows runner behavior has not been verified.

## Local regression evidence (Linux, Python; exact committed file contents)
- **R485 + R486 inherited suites:** 18/18 methods normal, 18/18 `-OO` optimized, using synthetic tests and live child processes.
- **R487 new stream-budget tests:** 8/8 methods normal, 8/8 optimized. Real subprocesses test exact 1 MiB acceptance, >1 MiB flood-and-sleep termination, timeout reaping, merged stderr, a plausible success trailer after oversized output, nonzero exit and private-path suppression.
- **Total:** **26/26 normal + 26/26 optimized = 52/52 passing method executions**; Python compilation PASS.
- Locally tested/committed Git blob IDs: source `9ade79bf8c84159406aa8c5c4c3d7a1c96746722`; R485 adjusted tests `277598ec626fbfdd36d9dcab348697e6b691649e`; R486 adjusted tests `58e26e0cfc61f338c2aa5f4b94b6dfd625658d5c`; R487 new tests `bcbf0b675fb85326704e15ec6f4d49bb640c6306`.
- Command, from `products/desktop`, with `PYTHONPATH=.`: `python -B -W error -m unittest discover -s tests -p 'test_offline_source_gate*.py' -q` and the same for `test_offline_source_stream_budget_r487.py`; rerun both with `-OO`. No full checkout source suite or native Windows x64 test was run.

## Release and next gate
Restore GitHub Actions runner execution first; exact R486 [source workflow #44000591892](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44000591892) and [Windows build #44000592074](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44000592074) failed with job `steps=null`, so no hosted test step executed. Run both source-gate modes against a **complete trusted checkout**, and then the six-app regression matrix, Windows x64 executable packaging and launch smoke, Defender, SHA-256 inventory, accessibility, entitlement-protected premium delivery, independent QD review and founder approval.

**HARD HOLD:** No merge to `main`, no public EXEs, premium downloads, site deployment or automated compliance approvals.
