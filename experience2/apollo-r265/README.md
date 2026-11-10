# Apollo R265 — source-sealed, opt-in Grok campaign continuity (DRAFT / STAGING HOLD)

Tracks [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion governance [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), business charter #818. Independent of frozen homepage PR #49 and Research Desk PR #158. **This is NOT authorization to install, activate, merge, track users or deploy.**

## Conversion blocker and scoped intervention

The original Apollo evidence Atlas deliberately preserves one free article CTA, which points to `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`. When a Grok asset brings a viewer to the Atlas with campaign query parameters, a plain CTA drops those campaign parameters on the next internal visit. R265 supplies **an optional no-analytics-script, no-network, no-storage enhancement** that carries four independently validated UTMs only across that existing internal CTA. Without JavaScript, malformed campaign tags, missing source, altered staging assets or a second Atlas instance, the original free link still works. NASA links, source limitations, 31 fragment paths and merchant destinations are never changed. The attribution script itself does not measure sessions, clicks, checkout starts or sales.

Accepted fields: one each of `utm_source` (youtube/tiktok/instagram/facebook/pinterest/x/bluesky), `utm_medium=organic_social`, lowercase `utm_campaign` token 3–64 chars, and case-sensitive `utm_content` Grok immutable asset ID token 3–80 chars. Mixed-case asset IDs are intentionally preserved, since actual Grok inventory includes such values. Unknown/duplicate UTM fields are rejected; arbitrary visitor identifiers are not copied. **An Apollo campaign asset ID has not been confirmed.** No social post is inferred from the test fixtures.

`assets/campaign-continuity.js` is a static progressive enhancement. `fv-apollo-campaign-staging.php` enqueues it only after actual R224 and R262 source/asset integrity preflight and enqueued base styles, using hook priority 30. The script is pinned to exact SHA-256 in PHP. There is no merchant CTA and no duplicate analytics SDK.

## Reproducible QA

Protected fixture: exact R238 source manifest SHA-256 `f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68`. Real R224 and R262 PHP execute through R263's WordPress API simulator. Original HTML SHA-256 `50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6`. No generated claim or historical content modification.

Run the source-controlled smoke test:

```sh
python experience2/apollo-r265/qa/committed_smoke.py fixture/sealed-r238 experience2/apollo-r262 experience2/apollo-r263/qa/wp-real-source-sequence.php
```

Independent extended QA in the attached evidence bundle ran twice with byte-identical receipts and four screenshot pairs: 37 checks per execution, widths 320/390/768/1440/1920, JS on/off, valid/invalid/missing/malicious UTMs, keyboard SourceDrawer and no-JS native disclosure, 55 NASA hyperlinks, 31 internal fragment links, exactly one free article CTA, zero merchant links, no unexpected requests and no detected horizontal overflow. Two deliberate negative controls reject tampered optional source and acceptability-regression mutations. Receipt digest: `d5053eaca08fc0537dc40784e32c0df24b293486ff041158e581e9ab9561f6c9`. Source-controlled smoke: 20 contexts passed.

**Limits:** This test uses Chromium `set_content` because HTTP/localhost browser navigation is administratively blocked. It is not genuine axe-core, installed WP/Assembler, HTTP/CSP, screen-reader, browser UI zoom, production LCP/CLS, or measured commercial success. No action on PR #49 or #158.

## One possible paid continuation, separately gated

The existing original Apollo article stays free; after reading it, a *separately approved* contextual Collection/Mini Museum guide may be evaluated. Current [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) identifies a publicly described [Mini Museum guide](https://finalvestige.com/mini-museum-history-collectibles/) with proximate disclosure, but **does not prove** current Awin advertiser acceptance, authorized payable tracking, completed merchant orders, commissions or refunds. Meteorites/space specimens must not be described as Apollo flight artifacts, and NASA materials must not imply endorsement. No merchant offer is activated by this PR. Founder's production and commercial approval remains required.

## Release gates

Mandatory: approved real Grok Apollo asset ID and matching destination; independent privacy/consent and analytics owner review; authenticated merchant eligibility and payment settlement if adding paid continuation; axe-core, screen readers, actual installed WP/Assembler/CSP/network acceptance; browser UI zoom; field LCP/CLS; independent QD/CI on exact head; inherited R198 reconciliation; licensing review; founder approval. **STAGING HOLD.**
