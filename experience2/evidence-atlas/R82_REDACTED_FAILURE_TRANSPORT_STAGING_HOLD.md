# Apollo R82 — fail-closed browser exception transport

**STAGING_HOLD** · Issue #150 · isolated Apollo QA follow-up to draft R81 PR #709.
Base R81: `bd2713ecaa446fc05e0e50e5d82fc8b7868dba7b`.

## Defect in the prior diagnostic path

R81 made its *diagnostic JSON* safe, but the surrounding
`except Exception as exc` still ended with a bare `raise`. Python and
GitHub Actions print the original exception and traceback when a workflow
fails. A Playwright error can contain internal request paths, query strings,
and potentially sensitive private fixture details. Likewise, failing browser
context creation occurred outside the diagnostic `try`, and failing
`context.close()` occurred in an unguarded `finally`. R81's guarantee that
only allowlisted error descriptions would reach CI logs therefore did not
cover all failure paths. **Passing R81 CI cannot verify a failure-only path.**

## Source-controlled R82 correction

- Move browser-context construction inside the redacted exception boundary.
- Continue writing the existing R81 allowlisted failure artifact and
  structured, low-information CI diagnostic; suppress untrusted original
  exception text and chained traceback using a fixed, deliberately failing
  `RuntimeError('APOLLO_R82_SYNCED_PATTERN_HOLD') from None`.
- Guard context teardown similarly. An independent teardown-only error is
  classified as `CLEANUP`. If teardown fails after a prior browser failure,
  keep the first allowlisted receipt instead of overwriting it.
- Add five offline, hostile-lifecycle tests for failed browser construction,
  failed page creation, a known assert, teardown double-failure, and
  non-passing case accounting. These tests inspect both JSON and CI stderr
  and formatted Python traceback for secret strings, not just output files.
- Retain **every original** NASA identity, rights, source-custody, Gutenberg,
  axe, responsive, no-JS, keyboard/touch, print, local performance and
  fail-closed assertion. The 14 + 5 genuine WordPress browser configurations
  in `ex2-apollo-real-wp.yml` remain mandatory for an exact-head pass.

## Limitations and release gates

A local WordPress/Playwright pass does not establish hosted WordPress.com
compatibility or screen-reader acceptance. The historical cause of R79/R80
intermittent synced-pattern failure is still **unknown**; this sprint closes
a **diagnostic confidentiality gap**, not that root cause. Exception capture
elsewhere in the broader harness remains a separate review surface.

No WordPress content or settings writes, no production install or merge, no
photographic embedding, no speculative geography, no paid services, and no
change to frozen homepage PR #49 or original Research Desk PR #158.

All six NASA photograph-specific media assessments remain pending; the
`S67-19766` catalog association is provisional. Hosted compatibility,
independent QD, assistive technology/real-device QA, field CWV, and founder
approval remain release blockers.
