# R71 — Pin the premium human-review journal while a report is selected

**Pre-release engineering only.** GrantAudit Studio Pro and ProcureGuard Studio Pro remain unreleased; this work does not approve payments, grant eligibility or procurement compliance.

## Defect
The R70 queue verified that the opened exception report had not changed and that the current journal was valid. It did **not** require the validated journal's byte identity to be the same journal the reviewer opened. A second operator could add a legitimate review event, or a local file could be replaced with a different valid journal, while the first review window remained actionable.

## Change
- A private, descriptor-verified, bounded SHA-256 identity covers the **complete journal bytes**; `absent` differs from an existing empty journal. A symlink, hardlink, directory, observed swap or in-flight edit is refused by the established `journal_io.read_regular_bytes` guard.
- `ReviewQueue.load` pins the journal identity before and after full chain validation, committing no selection if it changes.
- Before each human review, export or encrypted backup action, `verify_current` checks the opened report, the pinned journal identity, complete history and the closing journal identity. It clears every actionable reference on an observed change and asks the operator to reopen and inspect.
- After **the same human** successfully appends a review, the GUI reopens and revalidates the selected batch/journal before displaying the new state. A failed post-append refresh clears the queue and **must not claim the action was unrecorded**; inspect the local journal to determine whether it was committed.
- This never edits the input report or journal while verifying and never sends customer data over a network. Only local SHA-256 identities are retained in memory.

## Independent test evidence
The new `tests/test_review_journal_r71.py` contains 19 synthetic tests covering absent/empty distinction, byte-stable reuse, append/removal, same-length rewrite, substitution, validation-time races, symlinks, hardlinks, directories, privacy-safe errors, own-review refresh and intact read-only checks. On 2026-10-30 Linux Python 3.13.5, a **reconstructed isolated source harness** with the proposed queue/identity logic and established descriptor IO passed **19/19 normally and 19/19 under `-OO`**, compilation PASS. The committed 19-test file matches the locally tested Git blob SHA; complete private-repository and Windows GUI integration **were not executed**.

## Boundary and release procedure
This is an *observed-change detector*, not an authenticated reviewer signature, filesystem lock, protection against an adversary who can alter and restore an entire journal between checks, or proof of historical origin. A journal may still change after the final preaction check. R70 export and evidence-vault APIs independently revalidate the complete source/journal during their operations; the cooperating append path retains its exclusive writer lock and complete history checks. Independent QD/founder approval and Windows x64 packaging/clean-machine GUI, source suite, malware and entitlement checks remain required.

**Release status: BLOCKED.** GitHub-hosted Linux and Windows jobs on R70 PR #211 failed before any recorded step (Actions #41141915055), tracked in #75. No executable or premium distribution was produced.
