# R303 — Atomic private premium vault sealing (draft / QD hold)

**Scope:** GrantAudit Studio Pro and ProcureGuard Studio Pro share
'fvs_suite.evidence_vault.seal_evidence'. This change affects ciphertext
**output** only; it does not alter AES-256-GCM, Scrypt parameters, stored
payload/schema, source-file imports, entitlement checks or review decisions.

## Defect and correction

Previously 'seal_evidence' opened the final '.fvault' path using 'open("xb")'
**before** writing its bytes and calling 'fsync'. Other processes could
observe an incomplete archive while the operation was ongoing or if the
process terminated during writing. Filesystem failures were re-raised with
customer destination paths still attached to OS exceptions and hidden
exception chains.

'vault_publish.publish_vault' now stages raw ciphertext in an exclusive,
randomly named '0600' temporary file in the same directory. It validates a
strict 120 MiB maximum; retries valid partial writes; checks the final byte
count; re-reads **exact bytes through the staging file descriptor**; and
fsyncs *before* publishing. Publication uses 'os.link' (POSIX) or
'os.rename' (Windows, where an existing destination is refused). Temporary
files are removed after success or ordinary failure. The final name is
never overwritten; an existing file or dangling symlink fails closed.

The helper constructs allowlisted errors from OS errnos and raises **after**
leaving the original exception handler: normal failed 'mkstemp', lstat,
write, fsync, link/rename and close operations do not retain confidential
customer paths in '__context__', '__cause__', or 'filename'. KeyboardInterrupt
is preserved. Original report/journal sources are not edited.

## Evidence actually obtained

On **Linux** with synthetic ciphertext and injected faults:
- cd products/desktop
- python -W error -m unittest discover -s tests -p 'test_vault_publish_r303.py' — **24/24 pass**
- python -OO -W error -m unittest discover -s tests -p 'test_vault_publish_r303.py' — **24/24 pass**
- python -m py_compile fvs_suite/vault_publish.py tests/test_vault_publish_r303.py — **pass**

The tested file Git blobs are 'b325f1b1362a4ad15f380efdee111dfceaacaa57'
(helper) and '2defb8fb10d0c523c5448d26744d4c9afed66dda' (24 tests);
these are byte-identical to the locally executed files.

**Not executed:** full-checkout 'test_vault_publication_integration_r303.py',
inherited R302/R301 regressions, full Ubuntu/Windows suite, native Windows
build, SHA-256 release inventory, Defender/EDR, accessibility and protected
premium download checks. Private GitHub checkout was not available to the
isolated Linux test runner; hosted Actions previously ended before steps.

## Limits and release hold

This is an **ordinary I/O failure and no-clobber atomicity** guarantee, not
a proof of durability after loss of power; the containing directory is not
fsynced. Windows rename and portable filesystems require **genuine native
Windows 11 x64 tests**. A hostile process that can mutate the destination
directory, exotic Windows filesystem semantics, catastrophic process failure,
or failed temporary cleanup can exceed this threat model. Do not advertise
the apps as ready for release.

No public upload, site change, premium entitlement bypass, automated payment
approval or QD/founder sign-off. Source remains on a stacked **draft** branch.

## Highest-impact next gate

Restore GitHub Actions runner execution (inspect billing/spend limits,
workflow permission and runner provisioning), then execute the entire suite,
particularly R298–R303 integrations on Ubuntu and Windows. Next obtain private,
genuine Windows 11 x64 executable candidates and repeatable six-app smoke,
SHA-256/Defender, keyboard/screen-reader and authenticated premium-delivery
evidence. Independent QD review and founder authorization are mandatory.
