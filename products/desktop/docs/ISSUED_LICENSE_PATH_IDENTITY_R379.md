# R379 — premium entitlement pathname-to-descriptor binding (DRAFT / release HOLD)

**Scope:** GitHub issue #73; operator-side offline licensing shared by **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. Stacked on the R378 draft (#2197), not `main`. The four free apps, licensing policy, signed payload bytes, financial engines, payment and site publication are unchanged.

## Reproduced gap in R378

The R378 fingerprint reader called `Path.is_symlink()` before opening and compared the opened file descriptor to itself after reading. That could reject a symlink present *at the instant of inspection*, but it did not establish that the pathname still named the descriptor. A path could be replaced by a **different, valid single-link regular file** just before open (not stopped by `O_NOFOLLOW`), or after reading but before the return. Even a same-byte replacement has a different file identity. The signed-payload digest check protects finalization, but hashing an unrelated file and losing evidence-path provenance are still unacceptable.

Using only disposable synthetic files, R379 regression tests were run against the original, exact R378 helper (Git blob `7f4c63e21bc28aba4da206ef29cafc42de222414`). **9 of 11 methods failed** on the prior helper, including pre-open swap, same-content alternate inode, post-read swap, synthetic Windows reparse point, and private-path `lstat` fault cases. The pre-existing descriptor-mutation and unlink checks still provided partial protections; R379 does not claim every failure was previously exploitable.

## Change

- `os.lstat(path)` before opening validates a normal single-link file and bounded size **without following the final link**. When the platform exposes `st_file_attributes`, reject `FILE_ATTRIBUTE_REPARSE_POINT` (not just Python symlink classification).
- Match **path metadata to the opened descriptor** before any file bytes are read: device, inode, mode, link count, size, mtime and ctime. Reject mismatches even if the content bytes are identical.
- After the bounded descriptor read, compare the original descriptor with its current metadata **and** the current `os.lstat(path)` witness. Any alias change, replacement, deletion or reparse attribute becomes a manual-review failure.
- Preserve read-only flags, 8,192-byte maximum signed entitlement, deterministic SHA-256, no output writes, raw descriptor ownership/cleanup and sanitized public `RegistryError` chains. No approval, entitlement issuance or compliance decision is automated.
- Require the 11 regression tests in **normal and optimized Python** on both Ubuntu source-tests and Windows packaging jobs, before executable packaging.

## Executed evidence and limits

Linux Python 3.13.5, isolated **exact source files**:
- R378 inherited 18 tests + R379 new 11 tests = **29/29 passing** under `python -W error -m unittest discover`.
- Same 29 under `python -OO -W error -m unittest discover` = **58 passing focused executions** (29 unique test methods), `compileall` passed.
- Updated helper source Git blob `e3b5a22f3191bbafd583275779e33157604686ca`; new test source Git blob `b62e3d41300f7ca304b4a9b83379ada4ca541611` were matched against the executed local files. Previous R378 test source blob `a6cb0bae51cc597c92806994f48436f920e8d256` also matched.
- The source files were tested in a small temporary working tree, **not** the complete exact-HEAD repository checkout. No native Windows executions, full six-app regressions, 22 real AES-GCM cases or genuine Ed25519 issuer-to-registry integration have been executed here.
- Windows reparse coverage is **synthetic mocked metadata only**: do not assert Windows junctions/ACLs are validated. File identity checks are best effort on filesystems exposing stable IDs; a privileged/same-user parent-directory change after the final witness, race between last witness and return, or deliberate filesystem identity spoofing remains outside this test's guarantee. The registry and fulfillment directory still require operator access controls. No disk write to original entitlement was made.

## Release gate / smallest unblock

No production branch write, site publication, binary upload, unrestricted premium distribution, or QD approval change. **Draft PR must remain HOLD.** The prior R378 hosted Actions run #43223280163 failed with both jobs reporting `steps=null`; cause unconfirmed. Repository owner should inspect Actions failed-check annotations, GitHub billing/spending limits and hosted-runner eligibility, restore runner dispatch, then rerun R379 exact head.

**Next highest-impact:** Full six-app exact-head source suite plus 22 genuine AES-GCM cases and R13 real Ed25519 offline issuance integration; native Windows 11 x64 PyInstaller output, six EXE smoke/Defender checks, keyboard/accessibility acceptance, and gated premium fulfillment. Independent QD review and founder approval remain mandatory before release.
