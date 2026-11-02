# Labs R125 — preserve replaced private Windows 11 witness evidence

**DRAFT / RELEASE HOLD** · Issue #73 · stacked on R124 draft PR #534, never production.

## Specific defect closed

The R124 one-check writer deleted a newly created witness during error
rollback when the bytes currently at the path matched its own SHA-256.
A different actor could replace that path with an independently created,
byte-identical file before cleanup. Equal bytes did not establish that
the writer still owned the physical file, so a failure could delete
another reviewer's evidence. Similarly, another actor could substitute
a byte-identical review matrix before the writer committed its update,
evading the existing digest-only concurrency check.

## Implementation

The writer captures the witness's **open file-handle** device/inode identity.
On failure it removes a new note only if the current path is still an
ordinary single-linked, non-symlink, non-junction, non-reparse file whose
identity matches the original handle and whose bytes match the original
SHA-256. It rechecks identity after reading the note. A substituted
witness, *even byte-identical*, remains intact for human investigation,
and the review matrix is not promoted to PASS.

The review matrix must also be an ordinary single-linked file. Its
device/inode identity is captured before reading and checked again
before atomic replacement, in addition to the SHA-256 concurrency
comparison. A separately created identical matrix fails closed.

These are **cooperative local custody controls**, not a cryptographic
identity proof, hostile-filesystem TOCTOU solution, or reviewer
authentication. An attacker can still exploit the narrow check-to-unlink
window with directory write access, and inode reuse is possible. Use
exclusive OS-level filesystem permissions for human reviewer custody.
Never remove suspicious files or bypass HOLD to force a green review.

## Test evidence and operational procedure

Ten synthetic adversarial regression methods cover normal recording,
own-note cleanup, substituted identical/different notes, same-byte
matrix substitution, symlink and hardlink matrix rejection, missing and
directory matrix paths, and absence of production asserts. A
source-owned, zero-skip, redacted runner is mandatory in both normal and
optimized `python -OO` on Linux and Windows CI. The tests simulate
custody and a fake Win11 build; they are **not** real physical review.

If R122 returns HOLD, preserve the matrix, any unexplained witness,
and existing lock for authorized human review, except where the tool
safely removes its own proven original note/lock. Keep observation
text, payment data, keys, external pin and premium files private.
Nothing here changes Decimal-safe financial engines or grants
compliance approval.

**Release remains HOLD:** physical independent Win11 x64 reviewer,
out-of-band authenticated R9 pin and actual six private EXEs, all 46
accessibility checks, real Defender/EDR findings, code signing,
authenticated premium distribution, QD and founder approval.
No public executables or production changes.
