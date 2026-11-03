# Apollo R81 — genuine WordPress synced-pattern failure forensics

**STAGING_HOLD** · Issue #150 · stacked on R80 draft PR #707 at
`e7b5efe65a24a53a973fc9d5630f1be7540cf88e`.

## Verified defect / why this change

At the exact R79/R80 heads, the inherited **genuine WordPress/Assembler**
workflow fails after all fourteen ordinary WP browser cases complete. The
exception is `AssertionError` inside `accept_synced_patterns` called
from `wordpress_r68.py:390`. The R78 base passed the same extension,
and the R78→R80 diff adds **only source-only NASA page gallery files,
new gallery tests and workflow**, not the R77 WordPress implementation.
Thus the exact subassertion is unknown and cannot responsibly be attributed
to the NASA chronology. Do **not** bypass the failing acceptance gate.

## R81 scope

The original `wp_reusable_r77.py` runs the same five configurations,
checks all 12 source records, 84 custody values, on-time stylesheet discovery,
no-JS, touch, filtering, axe, LCP/CLS and native 20-page PDF requirements.
R81 inserts a precise phase checkpoint and writes an additional
`R81_SYNCED_PATTERN_HOLD.json` **only when the genuine WP extension fails**.
The record contains one known assertion code (or an unspecified code), a
known phase, width, JS state, expectation, bounded completed-case count, and
source-controlled function/line numbers only. It contains **no** raw exception,
page URL, cookies, DOM, WordPress access information, source text or private CLI
logs. The original `AssertionError` or browser failure is re-raised: CI
stays **RED** until the underlying implementation actually passes.

Five adversarial unit tests verify label allowlisting, secret redaction,
timeout secrecy and bounded diagnostics. Both source/WordPress jobs in
`.github/workflows/ex2-apollo-real-wp.yml` are unchanged and will execute
on the exact-head draft PR. The CI job's existing `if: always()` upload
retains the new redacted receipt for independent failure triage.

## Release gate

Do not claim an R81 WordPress pass until checking the **exact** draft PR
head and its new artifacts. If still red, use the exact allowlisted code,
phase and source location to fix the underlying WordPress incompatibility
in a new isolated patch. Never lower accessibility, source custody, LCP/CLS
or no-JS assertions to make CI green. All photograph-specific NASA image
rights remain pending; portrait `S67-19766` catalog association is
provisional. No images, speculative coordinates, or remote requests added.

This branch does not modify frozen homepage PR #49, the homepage lead's
branches, Research Desk PR #158, production WordPress, source rights data,
or the R80 NASA chronology. No merge, activation, publish or deployment.
