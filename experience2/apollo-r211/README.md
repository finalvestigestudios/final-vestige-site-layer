# Apollo Experience 2.0 R211 — photo-date precision and source custody (DRAFT / STAGING HOLD)

**Scope:** isolated `experience2/apollo-r211/`, stacked on the **exact** R210 commit `c417f6063a5ba480fc7783bd62f021c6b3e5c1a8` (draft PR #1559). Do not alter homepage PR #49, original Research Desk PR #158, WordPress content/settings, social posts, emails, checkout, analytics or paid services. This code does not deploy.

## Actual historical defect corrected

The R210 source ledger and chronology repeatedly presented NASA archival photo **S67-15717 as a photo dated 3 January 1967**. NASA's Apollo 1 gallery catalogs S67-15717 only as **"(1967)"**, without a day. NASA's **separate Review Board narrative** dates the command module's removal from the altitude chamber to **3 January 1967**. The two facts must not be silently merged.

Primary records:
- NASA photo: https://www.nasa.gov/image-detail/amf-s67-15717/
- NASA image gallery (shows **S67-15717 (1967)**): https://www.nasa.gov/gallery/apollo-1/
- NASA Review Board, pre-accident test history (states chamber removal Jan 3): https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA advertising guidelines / promotion restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

R211 preserves the **Jan 3 dated preparation milestone**, replaces its misleading photo-day evidence link with a **Board record link**, provides the year-only photo link separately, adds an explicit document/photo-date distinction, corrects the gallery and custody explanations, and corrects BOTH machine-readable source-record and custody-ledger dates to year precision. No archival image is copied or commercially licensed by this change. No speculative map pins or relationship edges.

## Exact-source reproduction

R210 staging assets must be supplied from the independent R210 source package or reproducibly built equivalent. The builder hard-fails if **R210 `manifest.json` SHA-256 differs from `ff13886f46237b08e71d6b68cb13f8d712941cea6e99b1130c7e8de9736a3e7b`** or if any manifest-pinned file differs. The parent is **not** the public main branch: don't suggest a clean main-to-production merge.

```sh
export FV_APOLLO_R210_DIST=/absolute/path/to/R210/dist
python3 experience2/apollo-r211/build_r211.py
php -l experience2/apollo-r211/dist/fv-ex2-apollo-r211.php
python3 experience2/apollo-r211/qa/gate_r211.py /tmp/apollo-r211-evidence-A
python3 experience2/apollo-r211/qa/gate_r211.py /tmp/apollo-r211-evidence-B
```

All files under R211 `dist/` are generated and deliberately **not committed**. Each output is hash-pinned in its deterministic manifest. The real browser tests use Chromium/Playwright with the PHP shortcode shim, 11 contexts per run (320/360/390/768/1440/1920, no JS, touch, reduced-motion, forced colors and simulated CSS zoom). Capture is taken **before** touch interactions so touch hover state does not contaminate deterministic screenshot evidence. Tests include keyboard link/disclosure activation, print-visible closed answer guide and date note, fail-open late shortcode, six adversarial mutations, no overflow or browser errors, and buffered PerformanceObserver LCP/CLS (fixture only).

**Limits:** browser `set_content` is **not** installed WordPress/Assembler, an actual live or staging URL, an external link browser test, or production Core Web Vitals. Simulated CSS zoom is not OS/browser zoom. Genuine axe-core, NVDA/VoiceOver, installed WordPress staging acceptance, GitHub-hosted exact-head CI, independent QA and founder approval are **NOT VERIFIED**. The known inherited R198 canonical source-chain discrepancy remains **NOT RECONCILED**. These are release HOLD gates, not implicit PASSES.

## One aligned source-to-revenue hypothesis

Grok's *future confirmed* Apollo long-form documentary → Apollo Evidence Atlas → accurate source custody / source-comparison lesson → **Read original investigation** (one nonintrusive free CTA) → **proposed** teacher-ready evidence dossier ONLY AFTER buyer demand, NASA-commercial-rights review, verified SKU, price, merchant checkout/fulfillment and founder approval.

The educator dossier remains a hypothesis, **not a purchasable product**. No UTM campaign/asset ID or proven social link, confirmed subscriber, paid checkout, merchant-confirmed order, affiliate commission, refund data or realized net revenue is established here. Preserve Claude analytics ownership (#820), Grok distribution and Praxxis creator QA (TASK-008). Do not add or duplicate measurement scripts. Core KPI, **net revenue per 1,000 qualified human sessions**, is currently **not computable**. Only merchant-verified orders less refunds/fees count as net revenue.

**Release gate: STAGING HOLD.** Never deploy or approve use of NASA media commercially based on this source correction alone.
