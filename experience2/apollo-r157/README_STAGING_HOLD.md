# Apollo R157 — chronology rail, source drawer, exact-source browser acceptance

**Status: BUILT / OFFLINE CHROMIUM TESTED / STAGING HOLD. Not installed in WordPress.** Governed by #150 and conversion #820, founder charter #818. Based on R156 at `71342a6e1299960c1265b5610c9d1a01134846d8`, not homepage PR #49 or Research Desk PR #158. Neither branch is modified.

## Source-custody contract

* `ledger_with_chronology_review.html`: complete source-bound staging template. Base R156 HTML SHA-256: `7aea496f2a88a7d1eec8bb12e0161d6b34fdfe1797822f6fda333463a7f85ee4`; new combined HTML SHA-256: `67b612be3dfb385fd03e952a59e9ec5088c25a89821a3420a5f199326da57c83`.
* `chronology_rail_fragment.html`: four sourced chronological checkpoints with visible distinction between October 1966 / January 1967 photographs, January 27 Board reconstruction, and January 2017 museum tribute. Every anchor resolves to a preserved record; dates are not guessed from photograph-adjacent claims.
* `chronology_rail.css`: responsive 320–1920, keyboard-focus, forced-colors and reduced-motion treatment. Static lists and a native keyboard-operable HTML `details` SourceDrawer function without JavaScript.
* Six existing evidence records, six evidence limitations, twelve NASA record-reference links, and one `Read original investigation` CTA preserved. No map pins, fabricated relationships, duplicate analytics, checkout links, remote runtime assets or images. NASA photographs remain **NOT CLEARED** for paid-product packaging / advertising.

## Reproduction — exact staged source

From repository root, with Python Playwright, BeautifulSoup and an available local Chromium:

```bash
python experience2/apollo-r157/test_chronology_source_browser.py \
 --base experience2/apollo-r156/ledger_source_custody_review.html \
 --fragment experience2/apollo-r157/chronology_rail_fragment.html \
 --review experience2/apollo-r157/ledger_with_chronology_review.html \
 --css experience2/research-desk/assets/source-ledger.css \
 --css experience2/apollo-r156/source_custody_review.css \
 --css experience2/apollo-r154/r153_source_ledger_compat.css \
 --css experience2/apollo-r157/chronology_rail.css \
 --js experience2/apollo-r154/r153_source_ledger_compat.js \
 --out /tmp/fv-apollo-r157-smoke-1
```

Repeat in a different output folder and compare `SHA256SUMS`. Optional `--axe /absolute/path/to/reviewed/axe.min.js` is required for axe evaluation; missing axe means no accessibility certification. The exact-source test has no network or analytics calls. The chronology fragment's links are native anchors: R153 compatibility enhancement restores filtered targets, but without JavaScript all cards remain visible.

## Browser observations, November 5–6, 2026 (Pacific)

* Tested **84/84 committed-source Chromium smoke assertions**, six widths 320, 360, 390, 768, 1440, 1920; no-JS, keyboard SourceDrawer, touch at 390, search→chronology hash recovery, native focus, reduced motion, no horizontal overflow and no runtime errors. Screenshot hashes reproduced exactly in separate runs.
* Supporting independent, broader local R157 runner: **126/126** assertions passed with same combined HTML source identity; screenshots also reproduced. This broader runner is provided in the supplemental evidence ZIP but is not committed under this PR. Do not confuse its checks with the 84 source-controlled checks.
* `r157_lab_cwv_probe.py`: actual browser PerformanceObserver for **offline-document** LCP/CLS, six widths. In one exact-source lab execution, last LCP markers roughly 152–288ms and CLS without recent input 0. These are **not production Core Web Vitals**, not field p75 metrics, and not acceptance of live WordPress/Assembler assets/network.
* axe-core **NOT EXECUTED** because a reviewed local JS library was unavailable. Actual WordPress/staging/Assembler acceptance **NOT EXECUTED**; hosted exact-head CI **UNVERIFIED**. Rights clearance **NOT GRANTED**.

## Conversion governance

Flagship: **Apollo 1: Fourteen Seconds, More Than One Failure**. The high-intent segment is history and secondary science educators seeking primary-source material. Approved relevant path in this staging experience: **Grok historical video (publication unverified) → research desk → Read original investigation**. A potential Apollo educator evidence dossier is **NOT AN EXISTING VERIFIED SELLABLE SKU**; no purchase CTA is warranted. Grok owns scripts, distribution, and link IDs; Praxxis owns independent creator QA; Claude/Growth validates offers and merchant outcomes. Follow #820's 7/30-day qualified-human sessions → CTA → verified sale → refunds/fees → net revenue measurement, with unknown values marked unknown. No sales or attributed Grok visitors verified here.

## Blocked release gate

QD/founder independent review; source and rights review; real WordPress staging with original shortcode/theme; axe-core (zero violations AND zero incomplete); keyboard/screen reader/mobile zoom/touch; real-page LCP/CLS/INP and media delivery; checkout/product verification before **any commercial** CTA; exact-head CI, then explicit governed merge/deploy approval. **No production writes or spending.**
