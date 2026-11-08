# Apollo Experience 2.0 — R225 rendered-source custody reconciliation

**Status: DRAFT / ISOLATED STAGING ONLY.** Parent is R224 draft PR #1654 at `2b4e14262db93f072f7aee1e7433a639a9db7f1c`. No WordPress, homepage PR #49, Research Desk PR #158, social, merchant, analytics, email, or production writes. Related issues: #150 (engineering), #820 (conversion), #818 (business charter).

## Verified inconsistency (R224 artifact manifest f739b70c…)

The rendered R224 HTML has **56** outbound HTTPS anchors, **11** distinct external destinations, **6** source-ID-labelled outbound anchors, and **5** dated chronology milestones ending in month-precision `1967-04`. The inherited `source-url-crosswalk.json` incorrectly reports 50 outbound anchors, 5 source bindings, and only the four pre-report chronology dates. Therefore prior claims of a fully reconciled rendered crosswalk are withdrawn. This is a custody/accounting problem; no new historical claim is needed.

## Change

`build_r225.py` takes the exact byte-verified generated R224 package as input. The stdlib HTML parser inventories actual rendered source and chronology markup, refuses unreviewed destinations, mismatched photo IDs/URL bindings, duplicated IDs, active-content injections, invented geocoordinates, commercial-link substitutions, and invented precision for NASA's April 1967 report. It emits an updated deterministic source crosswalk and updates the PHP adapter's **pinned SHA-256** for the crosswalk. The visible Atlas, EvidencePlate/SourceDrawer/ChronologyRail, gallery and **single free editorial CTA** remain unchanged. Unexpected custody-byte corruption still fails open to the original Apollo 1 investigation. No fabricated geospatial pins or merchant claims.

`qa/crosswalk_browser_gate.py` runs PHP lint, normal/print/late rendering, SHA tamper fallback, 5 semantic mutation cases and 14 Chromium fixture contexts (320–1920px, JS on/off, touch/keyboard native source disclosure, reduced motion, forced colors, anchor census, overflow). It reports screenshot digests; it does NOT represent installed WordPress or a full WCAG audit.

## Local reproducibility

Use the R224 exact-source ZIP associated with #150 and verify its `generated-r224/manifest.json` SHA-256 equals `f739b70ced7c93254f69b9d58e1463a97d4288780202622b74d2be50431a57ea`.

```bash
python experience2/apollo-r225/build_r225.py --parent generated-r224 --out generated-r225
python experience2/apollo-r225/qa/crosswalk_browser_gate.py --parent generated-r224 --builder experience2/apollo-r225/build_r225.py --out r225-qa
```

R225 generated manifest SHA-256 on two local runs: `4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628`.
Crosswalk SHA-256: `d0da5ce673a53c482afc21069dd52760c9770e9a72cd2089ed42293682a7dd38`.
No field LCP, field CLS, genuine axe-core, screen-reader, localhost navigation, real browser zoom, installed WordPress, hosted exact-head CI, or commercial transactions have been verified. Localhost Chromium is blocked by administrator. R198 ancestor custody discrepancy remains open.

## Conversion-first handoff

**High-intent audience:** educators/research-oriented viewers of a *future verified* Grok Apollo long-form film. One permitted editorial step: source-verified Atlas → original free investigation. A paid educator dossier remains a **hypothesis**, not a sellable SKU; no paid CTA, email form, tracking, or attribution code is included. Grok owns scripts/distribution; Praxxis owns independent creator-source QA; Claude owns approved production engineering and merchant measurement; founder retains release permission. Real paid orders and settled revenue are **NOT VERIFIED**. Do not compute net revenue per 1,000 qualified sessions without legitimate source and denominator records.

## Required release gates

Reconcile R198 source ancestry; independent QA; obtain genuine axe-core and manual screen-reader checks; accept in an installed WordPress/Assembler staging site with real navigation, consent and CLS/LCP; obtain green hosted exact-head CI and founder release authorization. Separately verify an existing rights-cleared commercial offer, checkout/delivery, fee/refund records and Grok asset ID before planning any paid pathway. No deployment or merge in this draft.
