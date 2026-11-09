# R305 — Bind premium vault ciphertext to its private staging file identity

**Status:** DRAFT / QD + founder HARD HOLD. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R304, not `main`. No download, executable, release approval, or site change.

## Problem demonstrated

The shared `fvs_suite.vault_publish.publish_vault` seals evidence for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. R303/R304 verified ciphertext through an open file descriptor, then closed it and published the *pathname* with `os.link` (POSIX) or `os.rename` (Windows). That filename could be accidentally replaced between verification and publication. A same-user process manipulating that staging directory could substitute unverified bytes or a symlink. The earlier unconditional cleanup could also unlink a replacement it did not create. This is a **pathname ownership/custody issue**, not a failure of AES-GCM or Decimal accounting.

## Implemented behavior

- Capture the newly created private temporary file's device/inode identity. Require a regular file, meaningful inode, and single link.
- After byte-exact verification and fsync, compare the still-open descriptor's identity to the captured identity.
- After closing the descriptor, require the named stage to be the same regular file with exactly the expected size and one link immediately before exclusive publication.
- In cleanup, unlink only if the staging pathname still identifies that original file. Do not delete unrelated regular files or symlink replacements.
- Preserve the non-clobber destination rule, R304 short-read support, source immutability, exception-chain redaction, and interrupt propagation.
- Keep all data local. No customer data is logged, uploaded, or used in tests.

**Threat boundary:** These checks detect replacement present at validation time but do **not** eliminate an adversarial path swap between the final check and the OS link/rename operation. They do not protect against a hostile directory owner, malicious same-user filesystem races, crash-consistent directory metadata, or filesystems with unusable file identities. Fail closed on zero inode. A replacement can cause intentionally preserved/orphaned encrypted staging files (avoid deleting unknown files); operators must inspect such abnormal failures locally. No authentication, license, payment, or review-approval logic changed. Native Windows and other filesystem semantics remain unverified.

## Executed local evidence — isolated Linux, CPython 3.13.5

From a minimal test workspace containing the **byte-identical committed** `vault_publish.py` and `test_vault_stage_identity_r305.py`:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_stage_identity_r305.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_stage_identity_r305.py'
python -m py_compile products/desktop/fvs_suite/vault_publish.py products/desktop/tests/test_vault_stage_identity_r305.py
```

- **14/14 PASS** standard; **14/14 PASS** with `-OO`; **28/28 focused executions**; `py_compile` PASS.
- Baseline R304-style implementation tested with identical new tests: **7 failures reproduced**, covering path substitution, missing path, symlink/regular replacement, simulated multiple links, descriptor mismatch, and unsafe cleanup handling.
- Tests use synthetic ciphertext and temporary paths. Actual filesystem publication and failure injection, no original customer data.
- Exact Git blob IDs matching executed local copies: module `ee806cd488bf1c17fce5a5001e47d9389b3f6f13`; tests `d95130b3c3a5a78afdd00a073b09353995a26af0`.
- `test_staged_name_swapped_to_symlink_not_published_or_deleted` exercises a real symlink where permitted, and a replacement-file fallback where Windows symlink privileges are absent. Hard-link count testing is simulated to avoid privilege-dependent skips.
- **Not executed:** full repository suite, inherited R298–R304 tests, genuine Windows CI/native binary tests, Windows filesystem compatibility, Defender scan, accessibility, executable smoke, premium authenticated delivery.

In a real checked-out repository use the listed commands from its root. Its mandatory `products/desktop/scripts/offline_source_gate.py` discovers all `test_*.py` tests in both normal and `-OO` modes and validates all six source smokes when runner execution is restored. Focused test success is not full CI success.

## Release / review gate

Do not merge, distribute executables, publish premium file links, change WordPress, or make automated compliance approvals based on these focused passes. Independent QD review and founder approval are **still required**.

**Next highest-impact step:** Restore GitHub Actions runner allocation/execution (owner: billing/spending limits, workflow permissions, hosted runner availability), run the unchanged R305 SHA through both Ubuntu and Windows full source tests including inherited R298–R304 integrations, then perform genuine private Windows 11 x64 builds and independent six-app acceptance (SHA-256, Defender, accessibility, premium gated distribution). If native NTFS reports unusable file IDs, evaluate handle-based Windows publication and keep release on HOLD.
