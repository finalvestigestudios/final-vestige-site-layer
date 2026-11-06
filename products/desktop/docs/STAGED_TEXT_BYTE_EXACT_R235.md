# Labs R235 — byte-exact staged text evidence (DRAFT / QD HOLD)

**Scope:** Issue #73; source-only safety hardening shared by Policy Delta Desk TXT change reports and GrantAudit Studio Pro evidence manifests. Branch \`feature/labs-r235-byte-exact-staged-evidence-20261106\` is stacked exclusively on R234 head \`7974521eba625111d818478ba0ca2c6c76cd1f96\`, **not** on production \`main\`.

## Reproduced defect and correction

R234 verified \`stream.write()\` count and \`os.fstat().st_size\`, but **neither comparison verifies actual bytes**. A simulated fault that alters the same number of bytes in staged output (including a financial figure, Unicode symbol, LF/CRLF or evidence label) could pass both tests and publish a wrong audit record. This is not a claim of observed disk corruption at a customer.

R235 adds \`_verify_staged_bytes\` between \`flush + fstat\` and \`fsync + exclusive publish\`. It uses the *original* \`tempfile.mkstemp\` read/write descriptor on Windows/POSIX via \`os.lseek\` and bounded \`os.read\` calls (256 KiB chunks), checks each byte against the validated UTF-8 payload, and rejects EOF/extra bytes. No separate pathname is reopened. An altered or unreadable stage raises redacted \`EIO\` and is removed without creating a final output. The existing 64 MiB UTF-8 cap, deterministic bytes, exclusive non-overwrite finalization, POSIX owner-only mode, private temp name and no-telemetry behavior remain. Policy/legal/grant interpretation still requires a human; no auto-approval.

**Limits:** This is a prepublication check, not a complete anti-tamper system against a malicious actor with write access to the output directory or post-publication mutations. It does not prove power-loss-safe multi-file commit, Windows native filesystem behavior, cryptographic chain-of-custody, or any distribution readiness. Readback adds one sequential local pass over at most 64 MiB of report data; no network access.

## Exact local reproducibility evidence

- Linux x64, Python 3.13.x, real \`mkstemp\`/FDs, synthetic temporary documents and deterministic fstat-time same-length corruption. The *control* copy with the new verification call removed gave **11 failing test methods of 17**, including same-byte-count mutation cases; this is a control modeled on R234, not a byte-identical reconstruction of the entire old repository.
- After the fix, \`PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_atomic_text_bytes_r235.py\`: **17/17 PASS**.
- Same exact test with \`python -OO -W error\`: **17/17 PASS**. **34/34 local test executions**, no skips. \`python -m compileall\` PASS.
- Both exact Git blobs were verified byte-for-byte with \`git hash-object\` on executed local files: \`fvs_suite/atomic_text.py\` blob **805f5a5bfa9c9c0024edca5b300b53633c846c62**, \`tests/test_atomic_text_bytes_r235.py\` blob **ff2f342e62199a8e93f8899162fd6e859b03d1b0**.
- Tests cover five independent same-length content changes, UTF-8 preservation, large multi-chunk readback, empty documents, unexpected read/seek/EOF/bytes, no-fsync-on-failure, redacted exceptions, cleanup, direct FD readback, immutable existing reports.
- The dedicated 17-case suite is registered as **mandatory normal and optimized prepackaging gate in *both* Ubuntu \`source-tests\` and Windows \`windows-build\` jobs**. These workflow checks are configured but have **not yet executed on GitHub**; Ubuntu/Windows hosted CI remains blocked upstream of the first step.

## Required QD and release gates

1. Restore GitHub Actions scheduling; rerun the unchanged R235 PR head. Independent QD must verify configured prepackaging gates actually ran and review privacy/error semantics.
2. Execute **full inherited six-app regression suite** on both runner OSes and Windows 11 real-filesystem fault/integrity testing. A Linux \`os.read\` success is not a Windows binary acceptance test.
3. Privately build all six Windows x64 executables, verify SHA-256, scan (Defender/EDR), run offline smoke, NVDA/high-DPI acceptance, and confirm genuine premium entitlement/access-controlled delivery.
4. Obtain **independent QD approval + explicit founder release authorization** before merge, production catalog changes or distribution. No EXEs or unrestricted Pro URLs were produced.

**Next highest-impact step:** recover Actions runner assignment and complete the existing full offline source matrix on the *exact* R235 commit; do not respond to CI failures with unverified public binaries.
