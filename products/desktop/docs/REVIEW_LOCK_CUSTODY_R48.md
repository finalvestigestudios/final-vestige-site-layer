# R48 — Descriptor-owned writer-lock custody for premium review journals

**Pre-release; no distribution authorization.** Applies to GrantAudit Studio Pro and ProcureGuard Studio Pro. The four free engines, all financial matching/Decimal rules, original CSV records, human decision authority, premium entitlements, and WordPress production are unchanged.

## Why this is necessary

R47 pinned the review journal descriptor during append, but its separate `<journal>.lock` file was created using a path-based text writer and later unlinked by path without checking whether the lock still belonged to that writer. A local actor could remove/replace the lock mid-review, causing a reviewer to silently release another writer's new lock. Stale competing writers would undermine the exclusive-writer assumption of the append-only, hash-linked audit journal.

## R48 behavior

- `fvs_suite.review_lock.exclusive_review_lock` opens the lock with exclusive-create semantics (`O_CREAT|O_EXCL`), and `O_NOFOLLOW` where the OS provides it. Existing regular files, stale locks and symlink locks are never overwritten or automatically broken.
- Uses `0600` at creation on POSIX (subject to stricter umask), writes only the current process ID, and fsyncs before admitting a reviewer; no financial content is stored in the lock.
- Holds the lock file descriptor for the entire premium review write and checks the live pathname against its device/inode, length, link count, mtime, ctime and descriptor metadata. Checks run before revalidating evidence, after revalidation, immediately before journal append, immediately after append and at context exit.
- If a lock is observed missing, replaced, hardlinked or edited, the human-review operation fails closed. Cleanup unlinks only a lock still matching the original descriptor identity/metadata. Substituted or stale locks remain in place **for human investigation**.
- An OS write/fsync failure before lock acquisition leaves an indeterminate lock requiring inspection instead of pretending another writer may safely proceed.

**Scope of guarantee:** These are cooperative, observed checks and cannot prevent a privileged or deliberately racing local adversary from changing filesystem state between checks. Windows ACL access must be independently validated. A failed journal fsync can still produce a torn JSONL record; never auto-repair or claim a review committed without verifying its complete hash chain. Hash-linked journals are not digitally signed or encrypted at rest.

## Verification

Run from a trusted complete checkout:

```sh
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p test_review_lock_r48.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p test_review_lock_integration_r48.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p test_review_lock_r48.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p test_review_lock_integration_r48.py -v
```

Thirteen filesystem lock regressions cover clean issuance/release, POSIX privacy, nested writer rejection, preexisting locks, links, disappearance, replacement, metadata alteration, fsync failure and source integrity. Four integration tests exercise both actual premium journal and register export workflows, preexisting-lock protection and lock loss during revalidation. Full six-engine suite, real Windows x64 binaries, premium-access controls and human QD acceptance remain mandatory release gates.

## Manual incident procedure

If `<journal>.jsonl.lock` remains after an error, **do not delete it automatically**. Close all review applications, preserve the original report/journal/lock bytes and SHA-256 evidence in an access-controlled local location, verify the complete journal hash chain against the exact source report, identify whether a writer is active, and have a human owner document the resolution. An empty or altered lock is not proof that a review was committed. Only restart after independent review; never treat the journal's `reviewed` label as approval to pay or certify compliance.
