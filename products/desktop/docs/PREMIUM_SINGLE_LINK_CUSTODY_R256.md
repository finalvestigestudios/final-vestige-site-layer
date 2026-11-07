# R256 — premium evidence hardlink isolation and manifest FD handoff

**DRAFT; QD and founder release HOLD.** Scope: GrantAudit Studio Pro and ProcureGuard Studio Pro only; no release or merge authorization.

## Risk and change

A correct SHA-256 inventory is not evidence that a published file has no alternate writable filesystem name. R255 checked pathname snapshots but accepted a hardlinked evidence manifest or report, including a link outside the package: an external editor could modify the same inode without replacing the bundle pathname. R256 rejects `st_nlink != 1` at manifest pathname/descriptor pre-read, descriptor post-read, pathname post-read, report pre-hash and report final review snapshots. It does **not** prevent privileged writers changing a single-linked file after verification and is not a durable filesystem lock.

The bounded manifest reader formerly transferred a raw `os.open` descriptor directly into `os.fdopen` without a cleanup path when adoption raised. New `premium_link_custody.open_inventory_stream` closes that descriptor on all adoption failures, including unexpected exceptions and interrupts. The caller still uses `with` to close successful streams and retains strict size, regular-file, identity and content verification. No customer filenames are added to error messages or logs.

## Test contract

Run from `products/desktop` on Python 3.11+ in **both** regular and optimized modes:

```sh
python -W error -m unittest -v tests.test_premium_link_custody_r256
python -OO -W error -m unittest -v tests.test_premium_link_custody_r256
```

The test file has **18 methods** (13 helper and 5 integration); stable synthetic bundles exercise both premium products, ordinary FD ownership and injected `fdopen` failures, manifest/report external aliases and aliases introduced while hashing, and safe user-facing inventory errors. If filesystem hardlinks cannot be created, related tests explicitly skip. Run the full repository's six-app source suites on actual Ubuntu and Windows runners; do not extrapolate isolated local helper tests to native Win11.

## Open gates

No app is released. Source integration and full suite, genuine Windows 11 x64 GUI/keyboard/NVDA, private six-EXE builds, actual Defender/EDR scan, SHA-256 reproducibility, signing when available, protected premium delivery, independent QD review and founder signoff all remain required. GitHub Actions has recently failed before reported job steps; restore runner execution and rerun the unchanged reviewed commit. No automated compliance decisions, network uploads, automatic evidence deletion, premium license bypass or direct site changes are introduced.
