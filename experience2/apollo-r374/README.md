# Apollo Experience 2.0 — R374 strict source/HTTP transport custody (DRAFT)

**Scope:** Additive, isolated, staging-only QA under `experience2/apollo-r374/`. Stacked on R373. Parent engineering Issue #150; commercial charter #818 and coordination #820. **Production HOLD.** Homepage PR #49, lead homepage lane, Research Desk PR #158, and Grok/Praxxis TASK-008 remain unchanged.

## Actual defect addressed

The prior R373 runner confirms that *somewhere in the document* the set of four approved NASA URLs appears. An altered citation can therefore attach a different NASA document to one chronological stage without changing the unordered source set. R374 adds a SHA-256 custody seal across the four source-bound event records (original wording, limitations, dates, rights, link destinations, print citations, native disclosures), chronology order, separately labeled 2022 retrospective and exactly one existing free-investigation CTA.

Additionally, the older runner accepts a CSS request by filename/status. R374 verifies the single actual same-host HTTP stylesheet response has the SHA-256 of the reviewed R372 CSS; an unexpected CSS variant, missing stylesheet or redirect fails rather than being counted as accepted. Existing R373 HTTP/CSP/axe/keyboard/touch/layout gates remain inherited and must *also* pass. No JavaScript was added to the visitor-facing component.

Pinned reviewed R372 PHP/Chromium source snapshot SHA-256: `9ce651c80e7d6d5dc91a5ad3b7a8bac7eb9a6341c18d41ac2877298697ff117f`. Pinned R372 CSS body SHA-256: `a7b05064f31439840d68a973db000bc6d6836c05d60b5a6f239f83fb1b9fb5c7`. This is a reviewed *fixture* identity check, not a NASA media reuse license.

## Reproducible local proof (fixture, NOT WordPress staging)

From a checkout containing all stacked R365–R374 sources, PHP 8+, Python Playwright, Chromium and pypdf:

```sh
python3 experience2/apollo-r374/qa/test_stage_custody.py
python3 experience2/apollo-r374/qa/staging_acceptance.py --mode fixture --out /tmp/apollo-r374-local
```

The new Chromium suite covers 320, 390, 768, 1440, 1920 CSS pixels; no-JS, 400% root text, reduced motion, forced colors and touch; plus 15 deliberate source/CTA/rights/order/print mutations. The swapped-source regression explicitly proves the older unordered-URL test would accept the wrong stage assignment. Screenshots, native print PDF, structured result JSON and reproducible ZIP can be produced locally. Fixture LCP/CLS are not real-user Core Web Vitals.

## Real installed staging acceptance only after approval

```sh
python3 experience2/apollo-r374/qa/staging_acceptance.py --mode staging \
  --url https://approved-staging.example.org/apollo-evidence/ \
  --host approved-staging.example.org \
  --axe-js /verified/local/axe.min.js \
  --out /private/qa/apollo-r374-staging
```

Run **only** against a specifically authorized WordPress/Assembler *nonproduction* hostname with a genuine local pinned axe-core library. The R373 guard hard-rejects finalvestige.com, credentials, query strings, admin/API paths and non-HTTPS routes. R374 additionally rejects altered evidence and delivered CSS bytes. Never bypass CSP, simulate an axe pass, visit the outbound CTA, enable paid services or modify WordPress content/settings. Passing this local runner would not be a release approval: still require independent QD, native NVDA/VoiceOver, cross-browser testing, current rights/media review, exact-HEAD hosted CI, commercial fulfillment and founder authorization.

## Offer → funnel → blocker → experiment → owner

| Offer/funnel | Blocking fact and safe experiment | Owner |
| --- | --- | --- |
| Proposed Apollo educator dossier → paid order | No verified payable, rights-cleared SKU or accepted checkout. Withhold purchase CTA; authenticate product/merchant/fulfillment first. | Founder + Claude |
| Grok Apollo long-form → qualified landing | Published approved Apollo asset_id and human/UTM sessions unverified. No Grok queue or social post changes. | Grok + Praxxis |
| Evidence Path → existing free Apollo investigation | Correct stage citation/limitations/copy/transport are fail-closed by R374; actual installed staging test still missing. Single editorial CTA only. | Apollo QA |
| Verified orders → net revenue | No authenticated settlements, fees/refunds or 7/30-day qualified human denominator; **net revenue per 1,000 qualified humans not computable**. | Claude / Commerce |

Path: **approved Grok Apollo documentary → reviewed NASA source chronology/gallery → existing free Apollo investigation → separately founder-approved, legitimately sellable educator product**. This is a conversion hypothesis, **not** a demonstrated paid sale, lead or lift. NASA's Board identified a probable arc initiator but not one proven exact spark. Later 102 ignitions were engineering tests, not observations during the fire. No photo assets, speculative geospatial edges or unverified merchant URLs added.

**Executed scope:** local fixture tests only. **Not verified:** installed WP/Assembler, true HTTP/CSP/stylesheet response, genuine axe, independent AT, hosted exact-HEAD CI, production CWV or commercial net revenue. **No merge/deploy/post/WP write/spending.**
