# Apollo Experience 2.0 R235 — source-trace heading outline (STAGING ONLY)

**Decision:** BUILT and locally Chromium/PHP tested; NOT LIVE. This is a new, isolated Apollo branch stacked on draft R234 PR #1719 at `ec41e726854a44a632d4652ffd9fd8819a2e51f8`. Do not touch the frozen homepage PR #49, Research Desk PR #158, Claude's production branches, or WordPress.

## Identified defect and minimal remedy
The primary source-proof section `section.fv-apollo-trace` is a peer of the method/source section, but its accessible label was an `h3` rather than an `h2`. The R235 pin-verified builder promotes that exact heading to h2, retargets only the corresponding scoped CSS selector, and updates the verified fragment and stylesheet SHA-256 checks in the PHP adapter and its CSS cache version. No NASA URLs, text claims, photo assets, dates, chronology milestones, CTA destination or commercial actions change. The original archive remains freely accessible, including without JS.

## Deterministic reproduction
Retrieve the R234 exact generated output from the established R234 evidence archive, inside `generated-r234-A/` (R234 manifest SHA-256 `bde3b3595c88f230ec0ffdeb978080c6d3c9f7ab638dbabe481b470ff540ff9f`). Requires Python 3, BeautifulSoup, Playwright with Chromium installed, and PHP CLI. The browser script points to system Chromium `/usr/bin/chromium`; adjust only the browser executable location for a different supported machine.

```sh
python experience2/apollo-r235/qa/r235_outline.py \
  --parent /path/to/generated-r234-A \
  --out /tmp/apollo-r235-A --qa /tmp/apollo-r235-qa-A
python experience2/apollo-r235/qa/r235_outline.py \
  --parent /path/to/generated-r234-A \
  --out /tmp/apollo-r235-B --qa /tmp/apollo-r235-qa-B
cmp /tmp/apollo-r235-A/manifest.json /tmp/apollo-r235-B/manifest.json
cmp /tmp/apollo-r235-qa-A/receipt.json /tmp/apollo-r235-qa-B/receipt.json
```

**Local output on 2026-11-09 (two independent runs):**
- Generated manifest SHA-256 `eccfee83d2856185f216345c58ad83fb85224da41047de7b6b2d6fbefd526082`
- Generated fragment SHA-256 `463ec4dfe6100a5b7a9233e9d8113efd8e94647549fc22fe57b3e716221eead7`
- CSS SHA-256 `44fa7ac23a12efc68bba9b7ae74c910751469818f66d872a36942c19e0c19acd`
- PHP adapter SHA-256 `d798d4ce5392e879c7572fc0d7800cef83c1826693a7863f6678d5b1f196e224`
- Browser QA receipt SHA-256 `0686698811916a8c5670a323eea10de827c7b56beffb9f410dbd87fdedb087d4`
- Two runs × 10 Chromium contexts (320, 390, 768, 1440, 1920, both JS enabled/disabled). **10/10 screenshots matched**, receipts and manifests matched. Chrome native accessibility tree verifies one named level-2 heading. Native keyboard Enter and mobile tap expand the source drawer; 87 links, 55 NASA links, 31 local anchor references, 13 disclosures, and one free-investigation CTA preserved. No overflow, duplicate IDs, unauthorized script/geo elements or unexpected HTTP requests in the offline fixture.
- PHP syntax and shim modes: normal and already-printed styles render; late missing stylesheet falls back to free investigation. This is a WordPress-function simulation, not installed WordPress acceptance.

## Commercial pathway and consent boundaries
One proposed high-intent visitor journey: Grok's **authenticated** Apollo documentary asset (not yet verified) → free, NASA-source-led Atlas → one original free Apollo investigation link → **possible** rights-cleared educator evidence dossier, only after founder approves an actual SKU, fulfillment, rights, checkout and audience testing. Do not insert a hypothetical product CTA into the narrative. Retain existing #820 UTM convention; no additional analytics script. Qualified-human sessions, confirmed leads, merchant-confirmed transactions, fees and refunds remain unverified; net revenue per 1,000 qualified sessions and 7/30-day paid cohorts are NOT COMPUTABLE.

| Offer | Funnel step | Blocker | Experiment/change | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Future educator dossier | Paid conversion | SKU/rights/checkout unverified | Validate demand and seller rights before pricing or public CTA | COMMERCIAL HOLD | Founder / Claude |
| Grok Apollo documentary | Social → Atlas | Published URL/asset_id unverified | Reconcile existing TASK-008 without changing Grok queue | UNVERIFIED | Grok / Praxxis |
| Free original investigation | Atlas evidence → investigation | Named source-proof section at wrong outline level | Promote section heading h3→h2; preserve scoped CSS and safety hash checks | LOCAL CHROMIUM PASS | Apollo |
| Confirmed purchase | Sale → net revenue | Qualified traffic and merchant transactions unavailable | 7/30-day reconciliation under existing measurement contract | NOT COMPUTABLE | Commerce / Analytics |

## Release gate (BLOCKED)
The inherited R198 canonical-source ancestry discrepancy, fully installed WordPress/Assembler acceptance, genuine axe-core (not run), screen-reader acceptance, actual browser UI zoom, hosted exact-head CI, independent QA, NASA rights review and founder authorization remain unresolved. Local Chromium `page.set_content` is a fixture, **not** successful real HTTP navigation and **not** field LCP/CLS. No PR merge, website write, affiliate activation, social post, newsletter, checkout, new vendor, paid service or spending is permitted. Cross-reference issue #150 and business gate #820. 
