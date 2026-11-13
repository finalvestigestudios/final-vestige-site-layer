# R330 — Apollo Evidence Atlas CSP failure paths (staging only)

**Parent:** [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150) · **Commercial governance:** [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

**Scope:** Independent Apollo QA. No changes to frozen homepage [PR #49](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/49), Research Desk [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), Grok's content queue, WordPress, merchants, or production analytics. Base is R329 #2309. Source PHP/CSS/JS unchanged.

## Objective / threat model

A restrictive Content-Security-Policy (or disabled JavaScript) must not erase NASA-source records, chronology, native source-return navigation, or the existing **one** editorial continuation. The evidence may be read with no scripts, and it must never turn photo catalogue IDs into accident-cause proof, inferred image rights, map coordinates, or merchant conversions.

The R330 gate runs **real Playwright Chromium** on a bounded PHP mock-WordPress shortcode render. It enforces four browser meta-CSP cases: inline scripts permitted; scripts explicitly blocked; scripts **and** styles blocked; JavaScript disabled. It checks seven widths from 320 to 1920 pixels; styled cases use 400% root text, reduced motion, native Chromium hit regions, and a 40px minimum for documentary receipt links. The CSS-blocked case checks legible native markup at normal text; its default browser touch-target dimensions are **not** represented as 400%-zoom/WCAG compliance. Chromium rejection of injected inline scripts is asserted, not assumed.

It also verifies 17 official NASA links, exactly 3 documentary catalogue entries versus 4 *context-only, not-cleared-for-reuse* photo accessions, no unsolicited requests or unreviewed external merchants, and one editorial continuation to [The Hatch Opened Inward](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). Browser-print hyperlink annotations are audited for merchant and campaign-identifier leaks. Four deliberate corruptions must fail: fabricated geographic pin; unauthorized checkout; fabricated photograph clearance; and documentary-source reclassification.

## Reproduction

```bash
python experience2/apollo-r330/qa/csp_release_replay.py
```

Requires PHP, Node.js, `/usr/bin/chromium`, Python Playwright and pypdf. The script pins actual Git blob SHA-1 of R329's reviewed runtime sources:

| Source | Git blob |
| --- | --- |
| `apollo-source-experience.php` | `0048781b3dbea5f1fa44b688d9ca5053313fbf01` |
| `apollo-source-experience.css` | `b9441b73ba810af23e59e72f862f2e1f7ea81ccc` |
| `apollo-cache-continuation.js` | `f85617e5f12ba747908ac507261f69c377369de7` |

**Local test receipt:** 28/28 Chromium CSP fixtures, 4/4 unsafe mutations rejected; PHP lint and Node syntax passed. Extended local runner `csp_failopen_gate.py` (included in independent evidence archive, not as a second committed QA gate) produced 28/28 contexts, four screenshots, a browser-generated PDF and JSON receipt. The committed replay was run independently against the identical runtime file blobs.

**Boundary:** Chromium CSP is enforced via an offline `<meta http-equiv>` on `about:blank`. **This is not native HTTP response-header CSP** and does not establish installed WordPress/Assembler/CDN compatibility, cache behavior, real network performance, or deployment readiness. Local HTTP navigation is administrator-blocked. Genuine axe-core was not available in the isolated environment; no axe pass is claimed. Independent NVDA/VoiceOver, Firefox/Safari, installed WordPress, hosted CI and real production LCP/CLS remain blocked. Never confuse fixture measurements with field p75 CWV.

## Research and rights custody

- [Original NASA Apollo 204 Review Board findings](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html): probable electrical arc; **no single ignition source conclusively identified**.
- [NASA Apollo 204 report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): the historical report is primary investigative evidence, not a media-usage license.
- [NASA S67-15717 photograph catalogue](https://www.nasa.gov/image-detail/amf-s67-15717/) and [S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/): photo accessions are contextual metadata, **not** Review Board documentary conclusions. Research Desk PR #158's overlapping labels still need its owner's editorial adjudication. NASA does not endorse FV.

## Controlled conversion hypothesis — no live activation

Grok-owned *future* Apollo documentary (publication/asset ID not authenticated) → NASA-grounded Atlas → **one free Apollo investigation** → separately founder-approved, original-pedagogy educational evidence kit **only after** an actual rights-cleared, payable SKU and checkout are verified. This is an educator-intent hypothesis, not a sale or proof of demand. No unsolicited commerce is inserted into the investigation. Source proof is freely accessible and is never gated by purchase.

| Offer → funnel step | Blocker | Proposed change / experiment | Evidence / owner |
| --- | --- | --- | --- |
| Apollo teacher case kit → paid order | Verified SKU, license, checkout unknown | Inventory currently sellable, rights-cleared assets before CTA | **HOLD** · Founder/Claude |
| Grok Apollo video → Atlas | No authenticated published asset ID and exact destination | Review existing TASK-008 source-of-truth inventory, do not post | **UNVERIFIED** · Grok/Praxxis |
| NASA proof → free investigation | Browser script may be denied by CSP | Keep native content/navigation and one stable CTA | **LOCAL PASS** · Apollo |
| Merchant-paid order → net realized revenue | Qualified-human sessions, confirmed orders, refunds and fees missing | Claude/Commerce reconcile 7/30-day confirmed records | **NOT COMPUTABLE** · Claude |

**Success metric:** verified realized net revenue per 1,000 qualified human sessions = `1,000 × (paid gross revenue − refunds − merchant fees − attributable costs) / qualified human sessions`. Only compute when denominator and reconciled payment ledger exist; attribution gaps and tiny samples remain explicit. A visitor click, emailed lead or PDF print is never a sale.

**Release decision:** HARD HOLD for genuine axe-core, independent assistive technology, native HTTP/CSP, actual installed WordPress/CDN, exact-HEAD hosted CI, rights/editorial review, verified offer and Grok asset, and founder signoff. No paid services, CMS changes or production release authorized.
