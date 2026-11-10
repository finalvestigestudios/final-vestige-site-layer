# Apollo R271 — authentic original Research Desk acceptance (STAGING HARD HOLD)

Scope: Issue #150, PR #158, commercial coordination #820, business charter #818. Additive successor to Apollo R270 PR #1952. Frozen homepage PR #49 and Research Desk PR #158 are **not edited**. Not installed, merged or deployed.

## Change

R270 browser QA used a synthetic ledger shape rather than the actual original PR #158 source. R271 snapshots the four actual PR #158 files, byte-for-byte, and the existing R270 PHP filter into **isolated staging fixtures**. The committed PHP shim executes the original `fv_ex2_rd_shortcode()` and R270 `fv_ex2_r270_scope_desk()` over **three full ledger instances**. The committed Playwright suite runs the actual original CSS/JS, not a facsimile.

Exact original Git blobs:
- `ledger.html` `403d128c57b9bc82dac7c619651689070edef86c`
- `source-ledger.css` `b8cf00afeceba115a9e9d19044fc11dcf2890cbe`
- `source-ledger.js` `32e757cc4dc8708397ff65ac21e89dd319781d78`
- `final-vestige-ex2-research-desk.php` `d1879a90101b5475990132369178f42743f4b57c`
- R270 PHP filter `a3d470c8867ec4111bcdbbc956ee952a866ac8e7`

## Executed QA

From this directory, with PHP, Python Playwright and Chromium at `/usr/bin/chromium`:
`php -l qa/source_gate.php`
`python qa/smoke.py /tmp/r271-a`
`python qa/smoke.py /tmp/r271-b`

**Actual local executions**: committed smoke **10/10 × 2 PASS**, 320/390/768/1440/1920px × JS enabled/disabled, 27 unique IDs for 3 original Research Desks, 39 source links, native keyboard no-JS disclosure, independent search behavior, valid label/ARIA references, no unexpected requests, no horizontal overflow. Four screenshot pairs and JSON receipts matched exactly; SHA-256 `2ae868ef54aa7f5c709dc0c31257695df7f8d42336d10e8b725a96a26bb6553f`.

Supplemental, uncommitted extended original-source browser regression: **30/30** at 100/200/400% root-font-size settings; root-font change is **not actual browser zoom**. Receipt `ce7d292ee8840f2981fb48b3c26be7e77efc0a55ce9001c9f899ca732ad596c2`. Two deliberately tampered source mutations rejected. Offline local observer reported LCP entries 44–124ms and CLS=0 in five `set_content` contexts; **NOT real HTTP/page-load, field metrics or p75 CWV**. LCP timing is nondeterministic and excluded from deterministic receipts.

## HARD HOLD / conversion plan

This is a WordPress API **shim**, not an installed WordPress or Assembler test. Genuine axe-core, independent screen reader acceptance, native zoom, HTTP/CSP, field LCP/CLS, QD, exact-HEAD CI, NASA media-rights clearance, and founder approval remain open.

**One intent-matched route only:** Grok verified Apollo long-form post (asset_id and attribution UNVERIFIED) → Apollo Evidence Atlas/Research Desk → free original *The Hatch Opened Inward* investigation → separate, disclosed optional Mini Museum guide (review only) → merchant-confirmed paid order if publisher eligibility and payable settlement verified. No merchant links added to history and no NASA endorsement claimed.

| OFFER | FUNNEL | BLOCKER | EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Mini Museum | authenticated purchase | Publisher eligibility and actual settlements unknown | Verify merchant account and paid-order reporting | COMMERCIAL HOLD | Founder/Claude |
| Grok Apollo documentary | human acquisition to Atlas | Asset ID, published URL and permitted placement unknown | TASK-008 source review | UNVERIFIED | Grok/Praxxis |
| Research Desk | free Apollo investigation | Original-template QA gap | R271 authentic-source browser suite | LOCAL PASS / WP HOLD | Apollo |
| Realized net revenue | paid 7/30-day cohort | Qualified sessions, confirmed orders, refunds and fees missing | Consent-safe first-party + merchant reconciliation | NOT COMPUTABLE | Analytics/Commerce |

No merge, WordPress write, affiliate activation, tracking script, social post, email, paid service or production release.
