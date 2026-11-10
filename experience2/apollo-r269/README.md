# Apollo R269 — source/rights/chronology and conversion custody (DRAFT; HARD HOLD)

This is an **additive staging admission test**, not a new Apollo component or a public product. It extends R268's Chromium accessibility-tree work by pinning the **ordered source-link labels and destinations**, chronology, gallery claims, SourceDrawer text, media-rights warning, and separate post-investigation commercial disclosure. Counting 55 NASA links alone would not detect a same-domain source substitution; this test does. It also rejects invented geo pins and a merchant link inserted into the historical narrative.

The exact R238 Apollo manifest is SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`. The pinned canonical browser snapshot is SHA-256 `96bf09ce7e543e32744eacb14e7cd340043eb398c71690a140ddc234c21c3dd8`. Source custody has **55 NASA links to 10 distinct NASA destinations**, six chronology date elements, four NASA photo/aftermath/exhibition records, and no invented geospatial pins. The source snapshot is not proof that NASA granted commercial rights. The original Apollo 204 Board report identifies an electrical arc as most probable but no conclusively identified ignition source. NASA advertising guidance prohibits implied endorsements; links to NASA records are not commercial licenses.

## Local reproducibility

From the repository root, with Python Playwright, PHP 8+, and local Chromium installed:

```sh
python experience2/apollo-r269/qa/committed_smoke.py \
  /path/to/sealed-r238 \
  experience2/apollo-r262 \
  experience2/apollo-r266 \
  experience2/apollo-r267 \
  experience2/apollo-r263/qa/wp-real-source-sequence.php \
  experience2/apollo-r269/qa/source-contract.json \
  /tmp/apollo-r269-qa
```

The sealed R238 fixture must be separately supplied and independently SHA-verified. The executable invokes **actual R224/R262 PHP logic inside the R263 WordPress API simulation**, not installed WordPress. It runs 10 browser contexts across 320, 390, 768, 1440 and 1920px with JS enabled/disabled; checks native disclosure, SourceDrawer keyboard focus, touch at mobile widths, 400% root-text reflow, print exclusion of the commercial preview and no unsolicited network requests. Ten negative mutations must each fail: wrong NASA destination on the same host, false date, fabricated photo claim, removed rights warning, invented geo coordinate, merchant insertion, hidden affiliate disclosure, redirected free CTA, remote tracking pixel, and false NASA-endorsed sales copy. It outputs deterministic screenshots and JSON receipt; observe two separate executions before claiming reproducibility.

The only current editorial action is the free investigation: `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`. The separate optional Mini Museum guide is a **REVIEW-ONLY, nonactivating preview**; no merchant eligibility, affiliate payout, acquisition asset ID, authenticated paid order, refund, fee or net revenue is verified. Existing Grok/Praxxis TASK-008 ownership is unaffected.

## Release blockers

No deployment, merge, WordPress change, new commerce/analytics script, social post or paid service is authorized. Genuine axe-core, independent screen-reader QA, installed WordPress/Assembler acceptance, actual browser-interface zoom, local HTTP/CSP (navigation blocked by environment policy), production LCP/CLS, hosted CI on the exact HEAD, independent QD, merchant/publisher rights and founder release approval remain **HARD HOLD**. This test is intentionally **not** an axe certification or a production performance measurement. Preserve homepage PR #49 and Research Desk PR #158 unchanged. References: engineering Issue #150, business Issue #820, charter #818.
