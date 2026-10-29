# R39 — Offline release-report consistency and independent SHA-256 pin

**Development-only, not release authorization.** The six Windows x64 desktop products remain unreleased. The four free programs and two premium programs are all covered by the same six-file release gate; this verifier neither reveals licensed payloads nor exercises payment or compliance decisions.

## Threat and mechanism

A R38 offline-gate JSON report can be altered after its initial production. A report alone is *not* evidence that Windows smoke tests really ran or that the binary was safe. R39 adds report_attestation.py to independently compare a previously saved report against the **current seven-file candidate folder** (six executable SHA-256 digests, exact names/order, PE metadata as rechecked by release_gate.verify(smoke=False), and the checksum-inventory fingerprint). This process is read-only: no binary is run, no report is modified and no customer content is transmitted.

A **trusted, separately retained SHA-256 digest of the original JSON report** optionally prevents later coordinated rewriting of the report (assuming the independently retained digest is protected). An UNPINNED result only establishes consistency with today's candidate, not historical authenticity. Both statuses explicitly set historical_smoke_proven and release_authorized to false.

The report reader limits input to **64 KiB**, requires a distinct ordinary non-symlink file outside dist, checks identity and metadata before/after descriptor reading, disallows duplicate JSON keys/nonfinite numbers, enforces the exact R38 schema, rejects unapproved release flags and contradictory smoke records, and sanitizes filesystem failure messages. Filesystem races and malicious administrators cannot be completely eliminated; inspect any anomalies. There is no signature or trusted timestamp service.

## Operator steps

1. On a trusted workstation, run the R38 release gate against **six candidate Windows EXEs**, keeping the new JSON report outside the candidate dist directory. The real smoke gate requires Windows x64. Do not distribute the executables.
2. At report creation time, independently calculate its lowercase SHA-256 and preserve that digest in a protected, separately controlled audit register. **Never derive an allegedly trusted pin from a report you are checking later.**
3. Later, with the original exact candidate files still present, run:

   ~~~powershell
   python products/desktop/report_attestation.py build/candidate-evidence/offline-gate.json dist --expected-report-sha256 <independently-saved-64-hex-digest>
   ~~~

4. CONSISTENT (PINNED) means the report bytes match the independently saved fingerprint and current candidate bytes match the recorded inventory; CONSISTENT (UNPINNED) means only current self-consistency. Any REJECTED result requires operator investigation. The command returns 0 for consistency, 1 on any rejected evidence. Neither result authorizes distribution, authenticates a smoke-test execution, verifies antivirus results or licenses, or replaces QD review.

## Verification scope and release hold

R39 adds 28 synthetic filesystem/schema/CLI regressions; locally executed under Python 3.13.5 on Linux with a **stubbed underlying release-gate dependency**. All new R39 logic is exercised, but the true integrated full-repository release-gate suite, Windows native EXE tests, AV/signing, gated premium distribution and independent QD review remain outstanding. Hosted Actions is still failing before its first recorded step and cannot be counted as passing.
