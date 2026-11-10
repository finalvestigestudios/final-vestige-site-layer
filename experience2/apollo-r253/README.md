# Apollo Experience 2.0 — R253 NASA source-action targets

**STAGING HOLD / NOT LIVE.** Additive, independently owned Apollo Atlas CSS overlay and executable acceptance runner, stacked on R252. No edits to frozen homepage PR #49, original Research Desk PR #158, original sealed R238 evidence, WordPress settings/content, paid offers, analytics, social channels or Grok's queue.

## Proven source and defect

The exact SHA-pinned R238 Apollo Atlas PHP adapter renders **20 NASA source actions** across evidence plates, photo catalog cards, source custody and SourceDrawer. Before this change, at least one action in each tested responsive context had a **22px-tall** rendered target. R253's source-only overlay gives these 20 actions **44px minimum height** and retains focus styling in forced-colors mode. Links, chronology and the sole free investigation CTA are unchanged. The CSS is NOT wired into production.

Protected R238 manifest SHA-256: f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68.

## Reproduce

Requires Python Playwright, PyMuPDF, PHP CLI, local /usr/bin/chromium, and existing external sealed-r238/ fixture in the previous Apollo R252 evidence package. No NASA image downloaded.

python experience2/apollo-r253/qa/r253_gate.py --atlas /path/to/sealed-r238 --css experience2/apollo-r253/atlas-source-actions.css --out /tmp/apollo-r253-A

Run again with /tmp/apollo-r253-B and compare receipt SHA-256. Test refuses edited manifest/assets; verifies PHP-rendered HTML byte identity; measures before/after 20 action targets at 320,390,768,1440,1920 CSS px, JS enabled/disabled; native SourceDrawer Enter/Space, keyboard activation, mobile tap, source URLs, chronology, single free CTA, no paid CTA, unexpected requests, IDs and overflow. It checks forced-colors and narrow-reflow proxies, Chromium print source URLs, four screenshot hashes and a negative control removing the 44px rule.

Two independent exact-source Chromium passes: **10 contexts each**, byte-identical receipts and screenshots. Baseline minimum **22px**, overlay minimum **44px**, printable NASA URLs **22** occurrences in each checked print context. Offline performance diagnostics were observed separately in an exploratory runner; not production LCP/CLS.

## Release boundary

This isolated CSS must be reviewed for integration by Claude, then tested on installed staging WordPress/Assembler with actual CSP, touch devices, screen readers, browser-interface zoom and genuine axe-core. Hosted CI, independent QA, imagery rights, inherited R198 discrepancy and founder approval remain outstanding. Browser set_content does NOT establish HTTP acceptance. Mini Museum merchant approval and purchases are unverified.

**Single editorial next action:** free Apollo 1 investigation, https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . NASA source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and commercial rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .

**Commercial hypothesis, not an achieved outcome:** easier NASA evidence access may improve trust and free-investigation progression before eventual consented paid conversion. Do not insert unapproved paid offers into the narrative. Founder/Claude must verify a rights-cleared available offer and checkout first. Grok owns published asset IDs/distribution; Praxxis independent creator QA; Apollo owns source experience. Attribution contract: qualified human sessions by asset_id/UTM → relevant CTA → authenticated purchases/partner-confirmed sales → refunds/fees → realized net revenue. No confirmed sales or denominator evidenced here, so net revenue per 1,000 qualified sessions is NOT COMPUTABLE. Maintain 7/30-day cohorts and small-sample warnings. Cross-reference #150, #820, #818 and Grok/Praxxis TASK-008 without changing their queues.
