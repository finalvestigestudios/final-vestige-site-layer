# R329 — Detect prior review-journal history rewrites during a valid append

**Status:** DRAFT / issue #73. Independent QD and founder approval **HARD HOLD**. No executable, premium distribution, production, license entitlement, or automated compliance decision is authorized by this patch.

## Reproduced failure mode

R328 checked the *newly appended event* byte-for-byte and compared the post-write file size / current path descriptor. It did not compare the **already verified earlier journal bytes** before versus after the write. A concurrent writer (or an injected `os.write` fault) could overwrite an older same-length event at byte zero while the legitimate new event was correctly appended. R328's append returned success: its appended-event witness and post-write size/path check both passed.

This is a point-in-time integrity gap, **not** an assertion that all local filesystem mutation is preventable, or that other source authentication mechanisms have failed.

## Implementation

1. After `verify()` validates the previous journal chain, but before appending, `journal_io.append_verified_event` takes a **SHA-256 fingerprint of exactly the existing `st_size` prefix** through a duplicated, pinned `O_RDWR|O_APPEND` descriptor. It immediately checks the descriptor metadata again.
2. After `fsync` and R328's exact appended-event readback, it recomputes the same bounded, streaming prefix hash and **fails closed** if it changed. It checks the descriptor metadata again after both reads and checks the pathname against that final descriptor state.
3. The prefix utility reads in at most 1 MiB blocks and holds only a digest and one block in memory. It never reopens a pathname, makes a network call, silently rewrites evidence, or rolls back uncertain appended bytes.
4. Existing R328 current-event readback, prior-chain verification callback, cooperating writer lock, symlink/hardlink/FIFO checks, private-path OS-error redaction, and human-reviewed decision flow remain required.

**Threat boundary:** A hash is not independent authentication; a privileged writer could mutate evidence after verification or exploit sophisticated concurrent mutation. This detects the observed interleaving only. Using `os.dup` shares an offset but `O_APPEND` remains mandatory; native Windows CRT semantics are not yet accepted. A successful append now entails additional bounded file reads, proportionate to the existing journal size.

## Executed regression evidence, 2026-11-10

- Runtime: Linux CPython 3.13.5, ephemeral synthetic local financial-looking files, no network or real customer data.
- Exact remote-matched edited code: `journal_io.py` Git blob `36565d7aa5c81aeddbeddd3521e90788c7c5d6cb`; `journal_write_receipt.py` blob `06ec7187c9d883e4a3e5910ebf8b512a83008087`.
- Exact remote-matched new regression files: `test_journal_prefix_r329.py` blob `97aca985b6839d4e57c2f8ceb26d3503ea0cc61b` (10 tests), `test_journal_prefix_integration_r329.py` blob `4f0878e13c53cbf311323e884a6424939b4e43ef` (6 tests).
- Replayed R328's exact committed 14-test module, blob `bb67741ac593c5a3347a5d31dfdfdb65344f242d`.
- **30/30 passing standard Python; 30/30 passing `-OO`; 60/60 test-method executions passing, zero skips**. Python compilation passed.
- Against a locally reconstructed R328 predecessor (without the new SHA-256 check), the new integration assertion **failed because a same-size historical journal rewrite was accepted as a successful append**. Two additional new tests could not execute on the predecessor, which lacked the new helper; neither is presented as a predecessor functional failure.
- Local test harness reconstructs the precise `_same_path_descriptor_signature` dependency from `csv_snapshot.py`, but **is not a full authenticated checkout**. Hosted full-suite, actual AES-GCM integration, actual Windows EXEs, SmartScreen/Defender/keyboard/assistive-tech verification have **not** passed.

## Reproduce on an authorized full checkout

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_prefix_r329.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_prefix_integration_r329.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_write_receipt_r328.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_prefix*.py'
python products/desktop/scripts/offline_source_gate.py
```

The existing internal Ubuntu and Windows source-discovery steps discover both new `test_*.py` modules; **no CI gate was bypassed or weakened**. Hosted Actions currently fails before jobs execute (as of R328 run #42812614260); the root cause remains unconfirmed.

## Release blockers / next highest-impact step

Unblock GitHub Actions jobs by inspecting billing/spending caps, workflow permissions, and runner eligibility. On a trusted complete checkout, run the whole suite in standard and optimized mode, all **22 mandatory genuine AES-GCM integration cases with zero skips**, then native private Windows 11 x64 six-EXE acceptance, SHA-256/Defender/accessibility checks and premium entitlement isolation. Require independent QD and founder authorization before merging or distributing. All six apps remain **UNRELEASED**.
