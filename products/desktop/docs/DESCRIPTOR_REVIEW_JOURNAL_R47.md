# R47 — Descriptor-bound premium review source and journal custody

**Engineering-only / RELEASE HOLD.** Applies to the local, human-only
exception-review workflow used by **GrantAudit Studio Pro** and
**ProcureGuard Studio Pro**. No production site, licensed premium download,
payment/eligibility authorization, customer-data upload or QD approval changes.

## Failure fixed

Before R47, review CSV and JSONL intake used a pathname symlink/stat check
followed by a separate `Path.open`. The file could be replaced between those
operations. Likewise, after validating the journal chain, `append_review`
reopened its path with `"ab"`; a replaced symlink, hardlink or regular file
could redirect new human review records or silently extend unvalidated history.

## New behavior

- `journal_io.read_regular_bytes` bounds every read (64 MiB report or 16 MiB
  journal), verifies a *single* regular-file descriptor and pathname identity,
  rejects symlinks, hardlink aliases, irregular objects and observed stat/data
  changes, including identical-byte inode swaps.
- `journal_io.append_verified_event` opens the destination once, preserves
  append-only JSONL records, checks previous events and source report via the
  caller's revalidation callback **while the destination descriptor is held**,
  and rejects observed substitutions or changes before any write.
- The existing exclusive cooperating-writer `.lock` and SHA-256-linked human
  event validation stay in force. New journal files use exclusive creation and
  mode 0600 on POSIX; existing files are not overwritten. Failed pre-write
  creation attempts remove only an unchanged empty file created by this call.
- A successful event is flushed and fsynced. If a write or sync fails **after
  any bytes were written**, a partial final JSONL line may exist and a human
  must investigate. Subsequent readers refuse incomplete/unverifiable history:
  the writer **must not** silently truncate or reconstruct it.
- The original source CSV, reviewer rationale and human decisions remain
  local. No telemetry, auto-approval, external API, issuer, entitlement,
  Decimal financial rules, or product pricing has changed.

## Security boundary and expected operations

This blocks *observed* pathname/descriptor substitution and routine accidental
or noncooperating modifications. It is **not** a kernel-level filesystem lock,
full Windows reparse-point protection, protection from privileged administrators,
an independent signature, tamper-proof history, a guarantee against edits
after return, or encryption at rest. All operators must store review files in
access-controlled directories and protect original inputs. Source/journal
parents themselves are not pinned recursively; do not work in a directory
another account can replace.

Existing symlinked or hardlinked reports/journals now fail closed by design.
Copy a legitimate source into a distinct private regular file for review
rather than bypassing the check. If a sync/write fails, preserve all original
files, quarantine the journal, and investigate before any new append.
Never claim a human review means a payment or procurement action is approved.

## Testing on a trusted checkout

```bash
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p test_journal_io_r47.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p test_journal_io_r47.py -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_human_review_r7.py -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_premium_review_csv_r20.py -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

R47's **17 focused synthetic tests** cover verified reads, journal creation,
existing append, permissions, hardlinks, symlinks, directory inputs, bounded
size, identical-byte swaps, ordinary-file swaps before open, changes during
validation, incomplete event rejection, and fsync failure. Focused tests were
executed on Linux x86_64 / Python 3.13.5 under normal and `-OO` execution
before opening this draft; their two source files were compared against the
committed Git blobs. **Full actual `exception_review` integration, the entire
repository suite, native Windows x64 GUI/binaries and Windows reparse/symlink
behavior have not been verified in this sprint.**

If Actions again fails before step 1, check account/runner provisioning and
billing, inspect the workflow run and job steps, and escalate with the run/job
identifiers to GitHub Support. Such an infrastructure failure is **neither
a passing nor failing application test**.

Keep all six Windows applications unreleased until a trusted Windows workstation
has independently built/executed their binaries, completed AV/security checks,
verified SHA-256 inventories and premium access controls, followed by separate
human QD approval. Never upload a premium EXE or customer data to public CI.
