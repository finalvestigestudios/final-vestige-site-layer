# Labs R129 — Windows 11 reviewer parent-path custody

**Issue #73 · DRAFT / HARD RELEASE HOLD · stacked only on draft R128 PR #560, never production.**

## Defect, scope and correction

The R109 private Windows 11 verifier checked whether each **leaf evidence file** was an ordinary, single-linked file. However, an ordinary file can still be reached through a linked ancestor directory, including a Windows junction or a reparse point. The R122 writer and R123 progress tool already checked reviewer directory ancestry, but direct R109 `template`/`verify` entry points, standalone source reads, and `validate_review` did not apply the same boundary consistently.

The R129 `_directory_chain` guard checks the full absolute parent chain of every private evidence-file read (R9 source report, review matrix and witness notes). It fails closed on nonexistent/nondirectory components, symbolic links, junctions and reparse point attributes. It captures the ordinary directory device/inode identity chain, then rechecks it after reading from the file descriptor. The private `validate_review` path additionally checks its witness-directory chain **even when zero checks have been recorded**, then verifies the chain did not change after validating the matrix.

This prevents accidental redirected private evidence intake and detects some directory substitutions during verification. It does **not** defeat a malicious administrator with raw filesystem access, a hostile operating system, an attacker who swaps and restores a directory inside the read interval, forged timestamps, or a separately untrusted R9 digest. Windows reparse-point rejection may also exclude some conveniences such as OneDrive, redirected profiles, junction-backed folders and symlinked workspaces: move **copies** of the approved private reviewer materials into a locally owned ordinary directory without modifying original signed custody evidence.

## Test evidence contract

`tests/test_windows11_parent_path_custody_r129.py` defines **16 source-owned synthetic regression methods**: normal nested-directory reads, full-six-app pending status, free/premium witness parity, leaf/parent/ancestor link rejection, empty and populated witness-directory rejection, simulated Win32 junction and reparse flags without platform skips, post-read directory-identity drift rejection, nonsensical directory rejection, no `assert` bypass, and redacted CLI failures.

`scripts/safe_unittest_r129.py` enforces an exact method inventory, zero skips and privacy-redacted results. Linux and Windows CI must each run it in normal and optimized `-OO` Python: **64 focused method executions** if all four gates complete. Existing six native Windows x64 candidate builds, actual-executable smoke, encrypted transfer, GUI/keyboard/scaling, four free / two premium locked interfaces and artifact allowlist remain inherited. Only exact-head completed GitHub Actions establish CI status. The tests are **synthetic**, not independent human Windows 11 acceptance.

## Independent release gates still mandatory

An approved independent reviewer must privately receive the exact six x64 candidates with an independently authenticated **out-of-band R9 SHA-256**; physically perform all **46 Windows 11 accessibility checks**; obtain actual Defender/EDR results and remediation history; complete code signing and authenticated premium distribution; and obtain independent QD review and founder approval. No customer records, private observation text, executables, keys, premium packages or unverifiable download links should enter public CI artifacts. **All six programs remain UNRELEASED.**
