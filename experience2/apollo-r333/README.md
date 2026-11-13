# Apollo R333 — cache custody, restrictive CSP and reader continuity (STAGING ONLY)

**2026-11-13. DRAFT / NOT DEPLOYED.** Isolated descendant of Apollo R332 PR #2325 at `c905cffd47588694946b3505800102c5f0bdc0f1`. Engineering owner: Apollo Evidence Studio. Tracks [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion contract #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Homepage PR #49 and Research Desk PR #158 remain unmodified; Grok/Praxxis TASK-008 is a separate production/distribution lane.

## Source-controlled executable

Run from repository root after installing local PHP, Node, Python Playwright + PyMuPDF, Chromium at `/usr/bin/chromium`:

```sh
python experience2/apollo-r333/qa/commit_gate.py
```

The gate pins and checks actual Git blobs of the Apollo runtime PHP `f59a083de8d0774ed7210bfe4e18726feea73f76`, CSS `577a5d33518baec6e1beff1517779264d342bc50`, JS `f85617e5f12ba747908ac507261f69c377369de7` and WordPress lifecycle render fixture `f8987327fd6b49afcf8996c695100e3e7471c831`; then runs PHP and JS syntax checks. It does not modify runtime code.

**What was actually tested:** (1) a real Python loopback HTTP server answered three campaign-query variants with byte-identical HTML and delivered four different CSP response headers received and checked by Python; (2) 24 real offline Chromium Playwright contexts used an equivalent **meta-CSP** on `about:blank?utm_...` at widths 320–1920, including 320/400% text, JS denied, CSS+JS denied, no-JS, reduced motion, mobile touch and forced colors; (3) all contexts verified 46 named HTML controls, three source-catalogue documentary roles, four photo records marked contextual/not cleared, 17 official-source links, zero geographic pin/edge markup, a single free-investigation CTA and noncollapsed targets where styled; (4) a trusted context menu on an approved campaign applied valid UTM labels only in the allowed-JS case, a mismatched asset ID was rejected, and the genuine printed eight-page PDF held 48 link annotations with **zero UTM leaks**.

**Non-negotiable scope distinction:** Chromium navigation to local or remote HTTP is blocked here by `ERR_BLOCKED_BY_ADMINISTRATOR`. The Python HTTP-header checks and Chromium meta-CSP checks are **separate**. This is NOT browser acceptance of HTTP response CSP, real installed WordPress/Assembler/CDN, or production performance. Genuine axe-core, Firefox/Safari and independent screen readers remain unrun. The generated local receipt and screenshots are evidence for this offline fixture only, not production LCP/CLS.

## Historical and media custody

The [original NASA Apollo 204 Review Board finding](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html) records electrical arcing as the probable initiator **without identifying a single conclusive ignition source**. NASA's [Brand Center](https://www.nasa.gov/nasa-brand-center/) prohibits false commercial endorsement. Photograph accession records are contextual metadata, not independent proof of Board findings nor blanket commercial clearance. No photographs or geolocations were imported. Research Desk PR #158 still needs editorial resolution of two photo-first documentary labels in its own ownership lane.

## Conversion-first decision record

| Offer → funnel step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Apollo educator kit → paid purchase | No authenticated payable rights-cleared SKU / checkout | Reconcile real product inventory and licenses, then independently test checkout *after approval* | HOLD; no orders asserted | Founder / Claude |
| Grok long-form → Apollo Atlas | Published immutable asset ID and allowed landing path unverified | Reconcile existing TASK-008 link inventory, do not create a post | UNKNOWN | Grok / Praxxis |
| NASA evidence → free investigation | Restrictive script/style policies and stale UTMs threaten continuity | Gate source roles, one editorial CTA, cached bytes, context-menu link and print privacy | LOCAL PASS (not HTTP browser/WordPress) | Apollo Studio |
| Verified orders → net revenue | Qualified-human sessions, settled orders, fees and refunds unavailable | 7/30-day cohort reconciliation, no duplicative measurement | NOT COMPUTABLE | Claude / Commerce |

Intended **unlaunched** pathway: Grok Apollo film → NASA evidence Atlas → [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → separately approved educational kit. Paid commerce must be outside the historical findings. Clicks, attribution hints and newsletter interactions are not sales. KPI is independently verified realized net revenue per 1,000 qualified human sessions; no denominator or paid numerator is established.

## HARD HOLD

Await genuine axe-core, independent screen readers, non-Chromium browsers, installed WP/Assembler/CDN and browser HTTP-header CSP, hosted CI on exact PR HEAD, NASA/editorial/media-rights acceptance, source-label owner approval, verified Grok campaign, real payable kit/checkout and founder/QD release. **No WordPress writes, deployments, media uploads, social posting, merchant activation, tracking installation, emails or spending.**
