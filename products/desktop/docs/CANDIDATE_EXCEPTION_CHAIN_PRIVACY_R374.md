# R374 — Candidate verification exception-chain privacy

**Scope:** Shared local-first release-candidate custody guard for LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. This is a draft engineering change, **not** a release or compliance approval.

## Defect and correction

The shared \`candidate_guard.py\` used \`raise CandidateGuardError(...) from None\` *inside* catch handlers for filesystem and stream exceptions. Although ordinary exception display concealed the underlying error, Python retained it as \`__context__\`. A caller or error collector traversing the exception chain could recover synthetic stand-ins for private customer paths, local account names, or repository/workflow secrets.

R374 raises the public, generic \`CandidateGuardError\` **after** the original handler has ended. For the stream, the context manager owns descriptor cleanup but no longer translates exceptions; \`_inspect\` translates them only after the stream context has unwound. The fix also covers path \`lstat\`, directory enumeration, \`os.open\`, \`os.fdopen\`, and inner file/hash/metadata operations. Expected validation errors remain distinct; \`KeyboardInterrupt\`/\`SystemExit\` still propagate, and a failed \`fdopen\` closes its raw descriptor.

This does **not** relax the exact-seven-file staging inventory, hardlink/symlink checks, maximum payload sizes, race-related signatures, SHA-256 byte custody, or no-execution policy. No customer data, telemetry, premium links, or site files change.

## Evidence, November 12, 2026

- Before-fix source independently reconstructed byte-for-byte, verified as Git blob \`cc92c58246196f284ea12659621a347bd96e4fe9\`; **16/23 R374 cases failed** on Linux Python 3.13.5 as expected, exposing retained exception context.
- Patched source Git blob \`a7d8fe2c37282fd3b88c8ff0b9443ee473255ed5\`; exact 23-case module Git blob \`b0c3c76002f238d968aac546c9f68df02bf7e07d\`; both matched the files used for local execution.
- \`PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_candidate_exception_chains_r374.py'\`: **23/23 pass**.
- Same command with \`python -OO -W error\`: **23/23 pass**.
- Exact existing R241 stream privacy module Git blob \`eef21f558957409d21351d485781a6f50c5a2f52\`: **18/18 pass** under both normal and \`-OO\` runs. Combined **82 passing focused method executions** (41 per interpreter mode).
- Test bytes represent inert synthetic EXE-named fixtures only. Checks include all six names, checksum inventory, preserved SHA-256 digests, descriptor closure, no source modification, exception chains, size guard, reject-stray-file, and interruption semantics.

The desktop GitHub Actions workflow is extended with four explicit R374 invocations (Ubuntu + Windows, normal + optimized). **No claim of Windows pass, actual packaged EXE validation, or complete exact-head regression is made until hosted runners execute.**

## Hold and next acceptance gate

The preceding R373 exact-head [Actions run #43179735422](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43179735422) failed with \`steps=null\` on both Ubuntu and Windows; the cause was not confirmed. Restore hosted-runner dispatch (inspect check annotations, Actions billing/spend and runner eligibility), rerun the new draft PR exact head, then execute full inherited six-app tests including **22 genuine AES-GCM integration cases**. Continue native Windows 11 x64 PyInstaller/package tests, Defender scanning, accessibility/keyboard paths, checksum verification and premium entitlement/distribution audits.

Do **not** release executable artifacts or publish premium URLs before independent QD review and founder approval. This patch does not grant any payment or compliance authority.
