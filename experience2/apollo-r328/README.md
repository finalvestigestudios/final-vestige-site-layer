# Apollo R328 — 400%-text source receipt accessibility fix (staging only)

**BUILT / LOCAL PLAYWRIGHT TESTED / NOT INSTALLED / NOT LIVE / HARD RELEASE HOLD.**

## Reproduced defect and narrowly scoped correction

At 320 CSS px and 400% enlarged root text (16px → 64px), the NASA source receipt in the free-investigation panel overflowed horizontally by **46px** (and by 6px at 360px). The original `.fv-r281__next a` selector styled *every* link in the footer as a CTA, adding about 109 CSS px of horizontal padding per NASA evidence receipt link at 400%. Additional rem-based nested padding made source text harder to reach.

- Limit the emphasized button selector (including print rules) to the **existing one** `a[data-fv-cta]` editorial link.
- Preserve three keyboard/native-fragment evidence receipt links, each with at least a 44px source-link target, without CTA-sized side padding.
- Cap nested footer/gallery/media-index and receipt-list padding at narrow viewports (max-width 420px) using fixed CSS pixels to prevent rem magnification consuming the text area. **No clipping or hidden evidence.**
- Update the reviewed CSS cache version in `apollo-source-experience.php` to `r328-b0fb092c1686`.

Runtime Git blobs: PHP `0048781b3dbea5f1fa44b688d9ca5053313fbf01`; CSS `b9441b73ba810af23e59e72f862f2e1f7ea81ccc`; JS unchanged `f85617e5f12ba747908ac507261f69c377369de7`. The historical chronology, original NASA destinations, rights limitations, contextual photograph links and single free CTA remain the same.

## Reproducible browser gate

```sh
python experience2/apollo-r328/qa/reflow_replay.py
```

Requires PHP, Node, offline Python Playwright and installed Chromium `/usr/bin/chromium`. This **source-controlled executable** pins all three runtime blobs. Local run: **14/14 Chromium viewport contexts PASS**, covering 320, 360, 390, 768, 1024, 1440 and 1920 CSS px, JavaScript on/off, 400%-enlarged root text and reduced-motion setting. At 320px there was no horizontal overflow after the fix, and all three receipt links remained within the viewport with at least 40px height. The reconstructed original CSS failed as intended at +46px in a destructive negative control. PHP and Node syntax gates passed. This was an offline fixture, **not actual WordPress**.

Additional *locally executed* artifact gate (source and screenshot bundle, not included in this PR's 4-file diff): 34 viewport/font-size combinations, 2 forced-color keyboard tests, two actual shortcode instances, screenshots and a Chromium PDF. The PDF check uses a **simulated decorated anchor**, not a real published Grok UTM visit; print removes campaign fields. That evidence archive must not be described as a production browser result.

## Conversion contract and ownership

**Grok published Apollo asset (unverified)** → verified NASA Evidence Atlas → **one free investigation CTA** → founder/Claude-approved, actually payable, rights-cleared Apollo classroom evidence product (NOT authenticated or added).

| Offer | Funnel | Blocker | Change / experiment | Pass/fail | Owner |
|---|---|---|---|---|---|
| Apollo educational kit | Paid checkout | Payable SKU and licensing not verified | Validate inventory, fulfilment and checkout | HOLD | Founder / Claude |
| Grok long-form Apollo asset | Qualified social → Atlas | No authenticated published asset ID/URL | Reconcile within existing TASK-008; do not change Grok queue | UNKNOWN | Grok / Praxxis |
| Free Apollo investigation | Evidence receipt → continuation | 400%-font source-link overflow | Scope CTA styling and fix narrow nested padding | **LOCAL PASS** | Apollo |
| Confirmed paid orders | Attribution → net revenue / 1000 humans | Qualified sessions, fees/refunds, settled sales missing | Claude-owned consented first-party/merchant reconciliation | NOT COMPUTABLE | Claude / Commerce |

No paid services, production WordPress changes, analytics, merchant or affiliate activation, Grok posting, emails or homepage edits. PR #158 retains separate editorial review for photograph-versus-Review-Board source classification; PR #49 remains frozen.

### Release blockers

Genuine axe-core; independent screen readers; Firefox/Safari cross-browser printing; installed WordPress/Assembler/CDN; browser native HTTP/CSP (blocked in the local environment); hosted CI on exact SHA; NASA rights/editorial review; authenticated published Grok campaign; authenticated payable offer and QD/founder approvals. Offline fixture LCP/CLS (if any) are not field Web Vitals; **no paid conversion or revenue improvement is claimed**.

Official source references: [Apollo 1 NASA mission](https://www.nasa.gov/mission/apollo-1/), [Review Board proceedings](https://www.nasa.gov/history/Apollo204/proceed.html), [1967 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Board findings describe a most-probable electrical initiator, not a conclusively isolated ignition source. NASA links do not confer commercial photo rights or endorsement.
