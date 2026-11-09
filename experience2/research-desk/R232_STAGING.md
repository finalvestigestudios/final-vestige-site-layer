# Apollo Experience 2.0 — R232 Research Desk source-search bridge

**Status:** Draft / staging only. Not merged, installed, released or commercially activated. Parent: R231 draft PR #1699 at `8519f3b9fe60d51bc9a8e3d92e4117f6ee4cfd2f`. Homepage PR #49, Research Desk PR #158 and other Experience Atlas branches are unmodified. Never activate the R232 adapter alongside another `fv_ex2_research_desk` shortcode plugin.

## User-facing change

The optional Research Desk search now supports multiple search terms, case/accent normalization and finds contextual wording inside otherwise collapsed native `<details>`. For matching records, only disclosures containing *all* terms open automatically, and those opened by search close when a new search is run or cleared. The live count/empty state remains accessible (`role=status` / `aria-live` in the unchanged R231 template). No JS leaves all six records readable, source links and the existing original investigation CTA visible. No external scripts, storage, tracking, new geographic claims, merchant offer or paid service.

**Source custody:** R232 PHP adapter reuses the **unchanged, exact R231 NASA six-record template** (`templates/ledger-r231-source-scope.html`, Git blob `0fd4f9ddadb3473110d2709a52332a78fa4ac04a`) and **unchanged R231 CSS** (`assets/source-ledger-r231.css`, Git blob `c16b460a642640c9efef5d519b0d171b7a30b2f3`). Only the optional search JS changes. Source warnings for 1966 altitude-chamber and 2017 tribute photographs remain; their images are not telemetric evidence, and the Review Board carries technical conclusions. Historical/advertising reproduction rights remain a separate approval gate; no new imagery is embedded.

## Reproduction

```sh
node --check experience2/research-desk/assets/source-ledger-r232.js
php -l experience2/research-desk/fv-ex2-r232-runtime.php
php experience2/research-desk/qa/r232_failopen.php
python experience2/research-desk/qa/r232_search_browser.py --js experience2/research-desk/assets/source-ledger-r232.js --out /tmp/r232-A
python experience2/research-desk/qa/r232_search_browser.py --js experience2/research-desk/assets/source-ledger-r232.js --out /tmp/r232-B
```

The browser gate uses installed Playwright + Chromium and a **synthetic contract fixture**, not the actual NASA HTML or WordPress. Two independent local runs passed ten Chromium cases each: 320/390/768/1440/1920 px, JS on/off, keyboard/touch native details, reduced motion, forced colors, multi-token finding, auto-disclosed source context, reset/no matches, one original CTA, no external network, no horizontal overflow and 10/10 reproducible screenshots. Their `receipt.json` SHA-256 was `6d2eb1c207f7b83082a519201b874463c1ec4f091152c787c6d11f6330cdc689`. Local PHP syntax and missing reviewed-template fallback passed. The synthetic fixture must NOT be represented as exact R231 NASA component, installed WordPress or production QA.

**Still not tested:** complete exact NASA HTML/CSS/JS in a browser, actual WordPress/Assembler lifecycle, genuine axe-core/WCAG audit, screen readers, browser 200%/400% zoom, usable LCP/CLS field data, hosted CI, independent QA, canonical R198 source ancestry, media-commercial rights, founder approval. No live release permitted.

## Conversion-first path and experiment

**Grok Apollo creator asset (published ID not verified) → source-traced Apollo Research Desk → single free original investigation CTA → possible future classroom evidence dossier**. Search improvement hypothesis: visitors looking for a specific fact (hatch/pressure/telemetry) can reach and understand the correct NASA evidence without overlooking disclosure-only context, improving qualified visits to the original investigation. This is a **hypothesis, not measured conversion lift**. The educator dossier remains not yet a rights-cleared, purchasable offer. No commercial CTA is permitted. Grok owns the original post and distribution, Praxxis its independent review; no new Grok task was created. Follow TASK-008 and cross-reference #820.

**Measurement contract:** Grok unique `asset_id` / standard permitted UTM → verified qualified-human landing session → original-investigation CTA → optional consent-based lead → independently authenticated purchase/affiliate settlement → refunds/fees → realized net revenue/1,000 qualified sessions in 7/30-day cohorts, with small-N warnings. No session-to-order join or verified paid order is currently available. Do not count outbound clicks or test inputs as revenue.

## Priority plan

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Educator Apollo evidence dossier (not sellable) | Paid checkout | Rights-cleared SKU/merchant fulfillment absent | Validate product/demand before activation | BLOCKED; no orders | Founder / Claude commerce |
| Existing Grok Apollo asset (unverified) | Creator → Desk | No authenticated asset ID, live post or allowable link | Read-only TASK-008 crosswalk | UNVERIFIED | Grok / Praxxis |
| Free original Apollo investigation | Desk → investigation | Search concealed matching source details | R232 auto-disclosed context in optional search | 2 × 10 local Chromium synthetic fixtures PASS; no installed site | Apollo |
| Verified net revenue | Purchase + refunds | Qualified-human attribution/merchant settlement absent | Read-only 7/30-day ledger | NOT COMPUTABLE | Commerce / analytics |

No production WP/settings writes, new pages, email, posting, affiliate activation, spending, or changes to homepage PR #49.
