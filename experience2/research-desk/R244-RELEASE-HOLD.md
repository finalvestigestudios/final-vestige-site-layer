# Apollo 1 Research Desk R244 — archival print custody (STAGING HOLD)

**Scope:** isolated print CSS and reproducible PDF acceptance test on the R243 Research Desk shortcode branch. This is a staged proposal: no production WordPress write, merchant activation, analytics script, social post, or homepage change. Branch parent: R243 PR #1783 `1849609c657c50f86a039c0ee89837d382014a90`. Related source PR #158 and governing Issues #150 / #820. Frozen homepage PR #49 untouched.

## Why this matters

Screen-only proof is not preservation. In the prior CSS, a visitor who filtered source records could print an incomplete set; black-on-dark styling also made the ledger unsuitable for economical paper printouts, and closed native `<details>` omitted underlying findings. The source records' visible link text alone did not preserve actual URLs on paper.

This change is tightly scoped to `@media print`. It exposes all six records, including those hidden by optional JS filtering; provides white paper / dark text; uses Chromium's supported `::details-content` pseudo-element to print closed native disclosure findings; and appends actual original archive URLs next to every link. Source URLs, card data, NASA photographs, interactive behavior and the one original-investigation link are unchanged.

## QA reproducibility and limitations

From a checkout of this *exact draft branch*, with local PHP, Python Playwright, Chromium and PyMuPDF available:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium \
  python experience2/research-desk/qa/r244_print_custody.py \
  --source experience2/research-desk --out /tmp/apollo-r244-exact
```

That is the **exact-template mode**, and it aborts if historical `templates/ledger.html` differs from Git blob `403d128c57b9bc82dac7c619651689070edef86c`. For isolated local reproduction without the full repo, use `--fixture`; it generates a synthetic six-record stand-in and **must not be represented as exact historical template acceptance**.

The runner invokes the actual R243 PHP shortcode adapter using its checked-in WordPress-function shim, tests 320/390/768/1440/1920 widths × JS on/off, forces a filtered record in the JS case, measures rendered print DOM and actual PDF source text, and saves screenshots. It strips Chromium's variable PDF creation timestamps and compares stable PDF SHA-256 checksums.

**Observed independent local fixture executions 2026-11-09:** two × 10 Chromium contexts passed; six records and six archive-link text hits survive each PDF; six expanded findings are printable; 4/4 reproducibility screenshots and 10/10 PDF SHA-256 checksums match between independent executions; every print page has white-background/economical styling.

**Important limits:** print disclosure visibility uses Chromium's `::details-content`; cross-browser Safari/Firefox behavior is not established. No genuine axe-core, NVDA/VoiceOver, installed WordPress/Assembler, hosted CI, field CWV or original NASA-template browser result is claimed. Browser test ran via offline `set_content` of PHP-rendered synthetic fixtures, not public HTTP. Validity of historical source URLs and constraints is independently governed by the original source manifest; print changes do not grant commercial media rights.

## Source rights and commercial boundaries

Technical source: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) — most probable electrical arc initiator, **not a conclusively identified ignition source**. NASA's [advertising guidelines](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) prohibit implied NASA endorsement and distinguish historical source links from commercial permissions.

Grok retains creator/publishing ownership; Praxxis retains creator review; Claude retains production and measurement engineering; founder retains live release and spending approvals. Conversion hypothesis: source-verifiable Apollo documentary audience → trusted Research Desk/Atlas → original free investigation → *only if separately approved and verified* a relevant space-history product. **Mini Museum is still merchant-acceptance/rights/attribution HOLD, not a counted sale or activated offer.**

OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:
- Mini Museum → paid checkout: merchant acceptance and attribution unverified → verify approvals, disclosures and receipts → **HOLD** → founder/affiliate/Claude.
- Grok video → verified landing session: actual published Apollo asset ID/UTM unverified → reconcile TASK-008, do not post → **UNKNOWN** → Grok/Praxxis.
- Research Desk → source trust/free investigation: incomplete print copies → R244 print custody → **LOCAL SYNTHETIC PASS, WP HOLD** → Apollo.
- Verified sale → net revenue per 1,000 qualified-human sessions: verified orders, fees/refunds and denominators unavailable → 7/30-day privacy-safe reconciliation → **NOT COMPUTABLE** → Commerce/Claude.

**Release decision: STAGING HOLD.** No merge, release, WordPress content/settings modification, paid service, social post, affiliate activation or change to homepage PR #49 is authorized.
