# R28 — complete, private Policy Delta and grant hash-manifest publication

**Development-only source change, issue #73. No Windows executable is approved.**

## Failure addressed

R27 made financial CSV outputs non-overwriting, but two text evidence paths
still wrote straight to final filenames: Policy Delta Desk's source-fingerprinted
unified diff and GrantAudit Studio Pro's final SHA-256 inventory. A disk-full
or interrupted write could leave an incomplete .txt file with a plausible
finished-evidence name. The legacy inventory also used raw filenames in
tab-separated records, enabling names with tabs or line breaks to forge
additional displayed inventory entries on filesystems permitting those names.

## New behavior

- atomic_text.publish_text writes UTF-8 (no BOM), preserves exact line endings,
  flushes and fsyncs private same-directory temporary bytes, and then publishes
  exclusively: non-replacing rename on Windows and hard-link creation on POSIX.
  Errors normally remove staging files without exposing partial evidence.
  No overwrite/symlink replacement fallback is allowed.
- Policy diff validates both source files, calculates existing raw-byte SHA-256
  digests and produces the same unified diff content before atomic publication.
- GrantAudit hashes every specified source and output before creating its
  final manifest. Manifest names are escaped with JSON string escaping, without
  surrounding quotes: tabs, newlines, backslashes, Unicode bidi controls and
  other non-ASCII text can no longer forge separate physical manifest records.
  Ordinary ASCII filenames preserve existing filename<TAB>sha256 output.
- All apps remain strictly local-first. Hashes do not authenticate claim
  eligibility, legal accuracy or human approval.

## Testing and remaining risks

12 real helper regression methods test exact bytes, UTF-8, non-overwrite,
symlink safety, simulated fsync/publication/encoding failure, cleanup,
POSIX 0600 permissions and missing paths. Eight integrated regression methods
cover existing policy SHA-256/hunks, manifest digests, collisions, failures and
control-character filename escaping. A non-Windows helper test run is not a
native Windows release verification; see issue #73 for exact run evidence.

Multi-file grant evidence bundles are not transactional: separate CSV
files may already exist if a subsequent output/manifest fails. An abrupt
process/power failure can leave a private staging file. Directory fsync
durability after power loss and Windows ACL privacy remain unverified. Source
files changing while being hashed or between reconciliation and fingerprinting
could invalidate provenance; no signature is produced. Filenames with equal
basenames from different directories still need explicit disambiguation.
Premium review register/journal and entitlement controls are unchanged.

Require complete connected-checkout regression tests, native six-app Windows
builds, executable smoke, file checksum/AV tests, protected premium fulfillment
and independent QD approval before any release.
