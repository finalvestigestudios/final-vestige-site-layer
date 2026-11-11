# Apollo R288 — NASA Date-Source Reconciliation (STAGING / HARD HOLD)

Isolated continuation of R287 draft PR #2059 at parent `1d207e9ab02d83eb37967a24c57513ee24cf6dbe`; PR #158, homepage PR #49 and live WordPress are untouched. Shortcode remains `[fv_apollo_source_experience]`.

## Historical finding

NASA's original Review Board narrative dates its *oral establishment* to **January 27, 1967**, and the Board's first Kennedy meeting to **January 28**. NASA's later safety summary calls **January 28** the establishment date. R288 preserves and labels both institutional accounts rather than concealing the discrepancy or presenting them as independent witnesses. The main three-record chronology still calls January 28 the first meeting/site visit. Editorial reconciliation remains pending.

Sources: [Board narrative](https://www.nasa.gov/history/Apollo204/narr.html); [1967 proceedings](https://www.nasa.gov/history/Apollo204/proceed.html); [later NASA safety summary](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1); [Apollo Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). NASA's [Brand Center](https://www.nasa.gov/nasa-brand-center/) and [advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) prohibit implied commercial endorsement. No NASA imagery, insignia, likenesses or coordinates are embedded.

## Source-controlled changes and tests

The source reconciliation uses an allowlist and SHA-256 digest; a mismatch returns the prior no-JS NASA report/free investigation fallback. The separate panel uses native links and printable full source URLs. Run `php experience2/apollo-r288/qa/committed_php_gate.php` (23/23 local PASS) and `python experience2/apollo-r288/qa/committed_browser_gate.py /tmp/r288-qa` (10/10 local Chromium PASS: widths 320–1920, JS on/off, keyboard, touch, reduced motion, forced colors and native source-focus round-trip). Independent local browser checks also produced two accessible-source printable PDFs and byte-stable screenshots across two runs after PDF metadata normalization. Inherited PHP/Chrome preflight gates passed locally. Run `python experience2/apollo-r288/build_archive.py /tmp/r288.zip /tmp/r288-qa` to produce a deterministic source/QA ZIP from fixed inputs.

**NOT TESTED:** installed WordPress/Assembler, HTTP/CSP Chromium navigation (blocked with `net::ERR_BLOCKED_BY_ADMINISTRATOR`), genuine axe-core, independent screen readers, real zoom, hosted CI, or production LCP/CLS. Synthetic paint/layout observations are NOT field Core Web Vitals. Editorial approval, source-rights review, independent QA, green hosted CI and founder release authorization are outstanding. No deployment, live writes, paid tooling or commercial activation.

## Commercial bridge (Issue #820 / charter #818)

Verified Grok Apollo asset **UNVERIFIED** → Evidence Atlas source trail → one free-investigation CTA → separate disclosed optional relevant offer **HOLD** → source-confirmed paid order **UNVERIFIED**. Mini Museum payable terms, acquisition asset IDs, purchaser evidence, fees/refunds and 7/30-day qualified-human-session attribution remain unknown. Grok owns publication, Praxxis creator QA, Claude production analytics and the founder release decisions. No sales or realized revenue are claimed.
