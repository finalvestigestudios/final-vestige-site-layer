# R29 — bounded, unambiguous GrantAudit SHA-256 inventories

**Source-only development change for issue #73. All six Windows x64 executables
remain unreleased; this is not a compliance or payment-approval control.**

## Correctness risk

The R28 manifest safely published its complete text, but hashed arbitrary
files through an unrestricted streaming read and identified each file only by
its basename. Different directories can contain distinct files with the same
basename, making two inventory records indistinguishable. A file can also be
replaced or modified during hashing, so the manifest could record a digest for
evidence that no longer exists at the originally selected pathname. Symlink
changes could redirect reads outside the selected source set.

## Conservative R29 behavior

- The standalone manifest_guard.inventory_text(inputs, outputs) builds the
  same ASCII basename<TAB>sha256 rows for ordinary distinct filenames, in
  selected input/output order; it preserves R28 JSON escaping for potentially
  misleading control/bidi characters.
- **Fail closed on ambiguous basenames**, including Unicode-normalized, case-insensitive collisions
  across input/output directories, instead of guessing which file an entry
  means. The user must supply distinctly named files before an inventory can
  be published. Existing package outputs are not rolled back.
- Reject symlinks, directories, nonregular files, duplicated hard-linked file
  identities, unreadable sources, and files whose descriptor metadata does not
  match their pathname or whose identity/size/timestamps change while hashing.
- Check each opened descriptor before and after bounded SHA-256 streaming, then
  recheck every pathname after hashing all selected files and before staging
  the manifest. On platforms supporting it, use O_NOFOLLOW when opening.
- Source input is capped at **64 MiB** (matching the CSV importer), and
  completed report evidence at **256 MiB** per file. A streaming cap also
  rejects files that grow beyond their limit after the initial stat check.
- Generic errors avoid echoing private source filenames or raw financial
  content. The manifest contains basenames, never absolute directories.
- R28 atomic_text.publish_text still stages/fsyncs private UTF-8 and refuses
  to overwrite any existing report or symlink. No changes to Decimal arithmetic,
  human review, offline entitlements, premium access, or QD approval.

## Verification and caveats

Sixteen real I/O helper regressions exercise exact byte hashes and order,
baseline compatibility, collisions, aliases, symlinks, directories, missing
files, sparse oversized files, differentiated limits, Unicode escaping,
metadata mutation simulation, final-sweep detection, and optimized Python.
Five integrated GrantAudit engine tests additionally cover successful
publication and rejection of ambiguous, oversized or symlinked evidence plus
non-overwrite. See issue #73 for which tests actually executed.

This is **best-effort mutation detection**, not an immutable filesystem
snapshot, a signed evidence package, or a guarantee that records were unchanged
between the earlier financial reconciliation and this final hash. Timestamps
can have coarse resolution; an adversarial writer can race the final check.
Files changed after the check may differ from the manifest. A successful hash
does not establish claim eligibility or policy compliance. GrantAudit's CSV
outputs and manifest are still **not a multi-file transaction**; failures in
later stages can leave previously completed CSVs. Human verification remains
mandatory.

The native Windows filesystem semantics, full repository suite, native x64
build/smoke, AV scanning, SHA-256 binary certification, protected premium
fulfillment and independent QD approval are still release gates.
