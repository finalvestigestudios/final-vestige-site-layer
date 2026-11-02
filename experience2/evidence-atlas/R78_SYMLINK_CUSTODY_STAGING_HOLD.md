# Apollo R78 — physical source-custody boundaries (STAGING_HOLD)

**Issue:** #150. **Base:** R77 draft PR #690, `c4e922453a6fe69785f4c1d28d6bd799530b2079`. No production merge, WordPress content/settings write, paid service, deployment or changes to frozen homepage PR #49 or original Research Desk PR #158.

## Reproduced provenance weakness

The R77 source-custody gate correctly required literal Git blob identities for the exact original Research Desk profile and the Atlas PHP/CSS/JS. But `is_file()` and `file_get_contents()` follow symlinks: a pinned asset pointing to an *external path containing identical bytes* previously passed. The Atlas's independent SHA-256 HTML template check also followed symlinks. A content digest verifies bytes, not the self-contained plugin installation path. This is a staging provenance weakness, not evidence of actual malicious changes.

## Implementation

`fv_ex2_apollo_pinned_file()` rejects missing/unsafe/dot/parent paths, symbolic links on the plugin root, intermediate directory and pinned file, and resolved files outside the plugin root. Both plugin origin checks, the complete immutable Research Desk profile, Atlas PHP/CSS/JS runtime and Atlas HTML template now use the same boundary. No NASA records, source statements, rights statuses, HTML, CSS, JS, photographs, geographic pins or chronology were changed.

The 20 adversarial PHP assertions create only temporary OS-level fixtures, verify ordinary approved paths and exact profile hashes still pass, reproduce a linked file with *matching approved Git blob bytes*, and prove symlinked file/directory/root and incomplete profiles fail closed. R77's 11 nested Gutenberg assertions remain. R78 also packages 13 allowlisted source files as byte-identical, exact-clean-head, deterministic ZIPs with SHA-256 and Git-blob manifest checks, never as a deployment package.

**Compatibility caveat:** Deliberately symlinked plugin deployments will be rejected. Hosted WordPress.com must be assessed independently; this is a provenance gate, not a hostile-server security guarantee or TOCTOU proof. Hardlinks are out of scope.

## Evidence and release gates

Genuine local WordPress/Assembler Playwright/axe tests, including 320–1920px, keyboard/touch, no-JS, reduced motion, original 12 records / 84 custody fields, native printing, LCP/CLS and published Gutenberg synced patterns, remain in the existing independent exact-head CI workflow. CI results for R78 must be verified **on its own exact head**; a configured workflow is not a successful result. Local laboratory CWV is not field telemetry.

**HOLD:** hosted WP.com compatibility, manual NVDA/VoiceOver and physical devices, QD review, NASA photo-by-photo reuse assessments (all six pending), provisional `S67-19766` catalog association, and founder release approval. No NASA photos, invented geo edges, or unsupported historical claims introduced.
