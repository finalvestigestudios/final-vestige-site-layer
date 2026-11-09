# R307 — Final-name ciphertext custody and failure rollback

**Scope:** Shared premium `fvs_suite.vault_publish` used by **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** (issue #73). DRAFT / independent QD and founder **HARD HOLD**. Stacked on R306 feature branch, not production `main`. No executables or site/download changes.

## Reproduced R306 gap

R306 verifies the private staged ciphertext, then publishes it by pathname using POSIX hard-link or Windows rename. A separate actor can replace the stage **between the final reread and the exclusive pathname operation**. The operation could then publish a *different regular file* or (on POSIX) a *symlink*, while `publish_vault` returns success. Verification of a pathname before linking is not verification of the *final name*.

Four targeted synthetic negative controls, executed against the **exact R306 source blob `cc5d5c9f51bb477ea504d3c178e2cb8674675fb9`**, failed as expected (**4/4 fails**): equal-length altered replacement, same-byte replacement on a different inode, symlink replacement, and oversized replacement. The fixture writes an attacker file **before** `os.replace` to avoid accidental inode reuse in the test. This is a local same-directory race and not an AES-GCM cryptographic break.

## Concrete code change

* After successful exclusive `os.link` / `os.rename`, open the **final destination name** read-only (using `O_NOFOLLOW` when supported and `O_BINARY` on Windows); verify its descriptor is a regular file with the original stage's device/inode and exact expected length.
* Compare **every published ciphertext byte** to the original in bounded blocks with the R304 short-read-safe primitive; demand EOF. Recheck descriptor mtime, ctime, size and identity, then final pathname identity and metadata.
* On failed final verification or interruption, attempt rollback of the just-published name **only if the current name still matches the observed published inode/type**. Do not erase a detectably unrelated replacement. Retain existing no-overwrite, owner-aware staging cleanup, redacted OS errors without retained exception chains, and noninterference with source files.
* This adds one further sequential verification read (up to the existing 120 MiB limit) after publication. That is an explicit performance/privacy tradeoff; do not claim constant-time postpublication attestation.

## Actually executed

Isolated Linux **CPython 3.13.5**, real temporary files, synthetic ciphertext only, source and test bytes verified identical to committed Git blobs:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_final_publication_r307.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_final_publication_r307.py'
python -m py_compile products/desktop/fvs_suite/vault_publish.py products/desktop/tests/test_vault_final_publication_r307.py
```

**16/16 PASS normal, 16/16 PASS optimized = 32 passing method executions**; Python compilation PASS. The 16 methods cover benign multiblock/empty payloads, final-name replacement by wrong bytes or wrong inode, symlink/size swap, legitimate short reads, final EOF/corruption/open/read errors, clean redacted exceptions, no-clobber, `O_NOFOLLOW`/`O_BINARY` flags, interrupts, and preserving an unrelated rollback replacement. Four POSIX-only attack fixtures intentionally skip on Windows; a native NTFS test matrix remains mandatory.

Git blob identities: implementation `74b6f87eea7ce97149e2ad70e9a942952b938acc`; tests `b612c65aac1e96cc0faff0fc3e9c18b4e3fcd498`. These match the executed local source and test files.

## Residual risk and release gates

The post-link check **does not eliminate the interval in which an unverified final name exists**, prevent further mutations after verification, guarantee rollback if the filesystem denies removal, or make directory metadata crash-durable. A hostile same-user directory owner remains out of the fully solved threat model. Do not advertise atomic security against a malicious local process; pursue OS-specific handle-based publication and private-directory ACL validation before making such a claim.

**Not executed:** full inherited integration suite, hosted Ubuntu/Windows CI, native NTFS file identity/rename tests, Windows 11 x64 portable EXE builds, Defender, keyboard accessibility, SHA-256 executable release inventory, and protected premium download/payment access. CI jobs have been failing before runner steps (root cause unconfirmed). Independent QD, genuine Windows executable acceptance, and founder approval are still required before any merge/release. No public downloads or changes to WordPress production.
