# R69 — authentic WordPress admission: complete REST index and safe diagnostics

**Review scope:** Apollo 1 Research Desk + Evidence Atlas + adapter, #150. **STAGING_HOLD**. R69 is based on R68 draft #634, which is stacked on R67 draft #627. No homepage files, PR #49, PR #158, production WordPress or CMS settings are changed.

## Observed, not assumed

GitHub Actions run [41468630703](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41468630703) executed the first R68 real-WordPress gate on 2026-11-02. The `source-contracts` job succeeded. The `authentic-ephemeral-wordpress` job failed after about nine minutes; the visible CI log records `APOLLO_R68_HOLD RuntimeError`, but the original runner intentionally withheld the cause and the private Playground CLI logs. **No authentic WordPress/axe pass is established.**

Independent code inspection identified a concrete admission-test defect: the runner read only the first 8192 bytes of `/wp-json/`, then demanded both `"namespaces"` and `"routes"` inside that truncated prefix. WordPress REST indices can be larger; the two markers need not appear together in the first 8192 bytes. This defect can falsely reject a healthy local installation. The CI failure's exact underlying cause was not proven by the redacted R68 log.

## Changes in R69

- Read and parse **complete bounded** (2 MB maximum) JSON REST indices rather than testing an arbitrary 8192-byte prefix.
- Support normal `/wp-json/` and plain-permalink `/?rest_route=%2F` local WordPress REST forms.
- Contact **only** a fixed literal loopback address using `http.client.HTTPConnection('127.0.0.1',9438)`; never follow HTTP redirects. No public WordPress or third-party HTTP probe is introduced.
- Check shape, not textual key order: `namespaces` must be an array and `routes` must be an object.
- **R69 first exact-head CI run 41479889976:** source contracts 126/126 passed; authentic gate failed before Playwright because direct loopback probe received `HTTP_302/HTTP_302` on 75 attempts, `HTTP_502/HTTP_502` on 12, and port unavailable once (sanitized GitHub Actions artifact 13158907536). This disproves the assumption that index truncation was the only bootstrap problem. The subsequent patch now permits only *same-loopback* redirects as a provisional HTTP-responsive signal, never follows them, and immediately requires the real authenticated WordPress/browser gate to verify actual CMS and evidence markup. Off-host/other-port redirects are rejected. Redirects are **not counted as a REST-index pass**.
- Preserve `R69_PARTIAL_BROWSER_RECEIPT.json` on every browser stage (including failures), with an explicit `acceptance_complete=false` until every Playwright/axe case passes. This prevents another uninformative, silently discarded browser failure.
- Cap readiness attempts to 180 seconds measured by a monotonic clock. Save a sanitized `R69_LOCAL_STARTUP_RECEIPT.json` on success and failure, including the local-only decision, elapsed time, attempt count and enumerated error codes. Keep Playground CLI stdout/stderr private and outside uploaded artifacts.
- Seven socket-free deterministic tests cover a valid index with `routes` beyond byte 8192, fallback routing, malformed JSON/schema, redirects, index-size cap and unavailable local ports.
- CI runs the R69 tests before the existing real WordPress/Assembler/axe/320–1920px gate and retains the new diagnostic receipt on failure. If the genuine gate continues to fail, inspect its **sanitized** receipt before making additional changes.

## Evidence hierarchy and release gates

Local test fixtures only prove the probe contract; a passing CI browser job is required to claim authentic WordPress integration. A source-contract pass does **not** count as authentic CMS, screen-reader or axe acceptance.

Rights review remains pending for six individual NASA photographs. The `S67-19766` catalog-to-photo association is provisional. No image usage rights, geographic pins, hosted performance values, production deployment or publishing are asserted. The existing sources, printable custody and no-JS path remain unchanged.

Do not merge the stacked drafts or modify the frozen homepage work. Track exact final head, CI conclusion, browser receipts and outstanding blockers in Issue #150.
