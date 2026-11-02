# Apollo R72 — authentic WordPress/Assembler case-ledger admission (STAGING_HOLD)

**Isolation:** This work is based only on Apollo R69 PR #640, itself stacked on
Apollo R68 #634 and R67 #627. It does not edit, merge, or deploy homepage PR
#49, the lead homepage branches, or Research Desk PR #158. Nothing writes to
the public WordPress installation. The WordPress Blueprint creates a single
private page only in a fresh disposable `127.0.0.1:9438` Playground VM.

## Reproducible defect being addressed

R68's original authentic-WordPress CI failed after startup without an
actionable artifact. R69 correctly introduced localhost readiness and
allowlisted failure categories, but the actual 14-case viewport×JavaScript
loop still only wrote its success receipt *after* every test finished. If the
first later assertion failed (an image, a WordPress theme request, a filter,
a late LCP sample), later cases were invisible. A generic end-of-run exception
cannot establish which previously executed cases passed.

R72 adds an **atomic, per-case, allowlisted progress receipt**
`R72_CASE_LEDGER.json` that survives partial failure. The committed
`wp_case_ledger_r72.py` only records predeclared widths, Boolean JS mode,
named milestones, failure class, and totals. It will not serialize raw URLs,
NASA excerpts, command lines, exceptions, cookies, Playwright storage state,
WordPress auth, or private HTML. It cannot claim 14/14 success without all 14
cases and all required per-case milestones. Progress output is written in the
ephemeral runner's artifact directory, never into the site repository.

## Substantive actual-CMS gates

The original source-pinned R38 Research Desk + Evidence Atlas + integration
adapter still supply six + six records with 30 + 54 custody values. R72 also
requires, **inside the actual WordPress browser**, that:

1. A top-level browser viewport is exactly the requested CSS width, rejecting
   misleading nested WordPress editor iframe captures.
2. All six original NASA catalog links match the R70 independently tested
   ordered whitelist, with no Apollo image embeds or hypothetical geo fields.
3. Native SourceDrawer `<summary>` toggles with keyboard Enter in both
   directions; the original **provisional** evidence filter activates with
   physical touch on small viewport cases or click on larger cases, resolves
   to one record, and resets to all six.
4. No-JavaScript printing exposes all 30 original Research Desk and 54 Atlas
   custody fields, in addition to all records.
5. LCP is awaited using a bounded real `PerformanceObserver` delivery window
   instead of reading an asynchronous metric immediately. Missing data
   remains a **failure**, never a fabricated zero or pass. CLS remains gated.
6. Every completed case persists a durable checkpoint; native axe-core still
   runs at 390/1440 and the complete admission remains fail-closed.

## Test and release rules

Local source-contract tests:
```sh
python -m unittest discover -s experience2/evidence-atlas/tests -p test_wp_case_ledger_r72.py -v
```

The `ex2-apollo-real-wp.yml` workflow adds these regressions while retaining
existing R68/R69 source-contracts, the genuine WordPress/Assembler browser
job, Playwright Chromium, and axe-core 4.14.0. Evidence must be evaluated
on **the exact PR head**, including the new receipt and the original
`R69_FAIL_CLOSED_RECEIPT.json` if the browser fails. For non-green exact
head, record the first incomplete milestone and named failure class; never
report installed CMS acceptance, axe, screenshots, or performance as passed.

**Release: HOLD.** This is disposable WordPress Playground rather than
WordPress.com Personal host parity. Six individual NASA image reuse rights
decisions remain pending, `S67-19766` remains provisional, NASA image
binaries are not included, and publication still requires independent QD,
manual NVDA/VoiceOver, real-device/zoom/forced-colors review, hosted p75
CWV/INP, editorial media review, and explicit founder authorization.
No speculative pins, fabricated map edges, paid services, production CMS
content/settings changes, merge, or deployment.
