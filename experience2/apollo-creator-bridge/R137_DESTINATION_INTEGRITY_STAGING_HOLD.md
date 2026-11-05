# Apollo R137 — creator and merchant destination custody (2026-11-05)
**STAGING ONLY / NO LIVE OR COMMERCIAL APPROVAL.** Governing #150, #818, #820; frozen homepage #49 and Research Desk #158 untouched.

## Actual defect and targeted fix
R136 accepted a well-formed HTTPS merchant URL without constraining its host or product route, meaning a hostile domain could pass the *document-only candidate* check. Its creator candidate only recognized YouTube watch links, not Grok's YouTube Shorts. R137 changes the actual `r136_conversion_evidence_gate.cjs` to call a source-controlled, deterministic URL boundary:
- Canonical YouTube watch, Shorts, and youtu.be URLs receive **syntactic-candidate** classification, never an assertion that Grok published a video. Unknown URL parameters, embeds, redirects, deceptive hostnames and credentials fail.
- Payhip only `https://payhip.com/b/<product-id>` or `https://www.payhip.com/b/<product-id>` can be considered a **document-only** candidate. No new CTA. Other storefronts and custom domains require independent founder/engineering review before policy expansion.
- First-party campaign-route preflight checks exact `utm_source=youtube`, `utm_medium=organic_social`, `utm_campaign=history_pilot_2026_11`, `utm_content=<asset_id>` with no extra tracking/PII parameters. The example route is *synthetic*; actual Apollo WordPress URL and asset ID are **UNKNOWN**.
- No site or merchant is contacted. Passing URLs do not prove legal reuse, saleable listings, landing accessibility, referral sessions, lead confirmation, checkout completion or paid orders.

## Reproduction
In a complete checkout of this PR branch:
```sh
node --test experience2/apollo-creator-bridge/test_r137_destination_integrity.cjs
node --test experience2/apollo-creator-bridge/test_r136_conversion_evidence_gate.cjs
node --test experience2/apollo-creator-bridge/test_r136_run_evidence_receipt.cjs
node experience2/apollo-creator-bridge/r134_actual_page_browser_acceptance.cjs --out /tmp/apollo-r137-browser
```
Native Node v22.16.0 ran the **exact committed** new module/test files locally; 10/10 PASS (verified Git blob IDs `f5c2351f7b7cd53735df28f54ccab90f0c2962cf` and `8e00103ffa622d8cb888a80196f2af25794e24ed`). Contract integration on committed R136 code: 5/5 V8 stubbed-interface checks PASS; NOT a native R136 CI run. Full R136 integration and R133 deterministic builds remain not executed. Chromium navigation blocked by administrator in available environment; no actual Apollo Playwright, axe, LCP/CLS, screenshots or p75 performance claims. Browser gate remains CLOSED.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER
| Offer | Step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| Educator evidence kit (proposed, **not verified saleable**) | Paid checkout | Merchant-link host was insufficiently constrained | R137 exact Payhip candidate boundary | BUILT; 10/10 native test PASS; no merchant inventory attestation | Apollo / Claude Growth |
| Free Apollo worksheet | Grok video → editorial → exercise | YouTube Shorts URL unsupported; actual asset_id/unpublished route unknown | Shorts/watch/shortlink candidate preflight | BUILT; stubbed interface 5/5 PASS; no real live link | Apollo / Grok and Praxxis |
| Future teacher product | Worksheet → contextual offer | No verified matching merchant item, photo reuse rights, license or fulfillment | Withhold paid CTA; verify exact seller inventory/rights outside this PR | BLOCKED | Claude / Founder |
| Confirmed paid orders | Reconciled net revenue per 1,000 qualified sessions | No verifiable human-session/order/fee/refund evidence | Issue #820 privacy-first 7/30-day verified scorecard only | NOT COMPUTABLE | Claude Analytics |

All six NASA photographs remain external-only visual references, not technical telemetry or commercially cleared assets. `S67-19766` remains provisional. Do not change source chronology or embed NASA photos until rights reviews.

**Release remains STAGING_HOLD:** actual-page browser/axe/performance, independent source/editorial and six rights reviews, merchant listing/checkout/fulfillment validation, WordPress/Assembler integration, exact CI head, and founder approval. Never merge or deploy by this workstream.