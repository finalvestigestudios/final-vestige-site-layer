# Apollo R308 — first-party editorial UTM continuity (STAGING; NOT LIVE)

Source of truth: Apollo [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stacked on R307 draft PR #2181, **not** homepage PR #49 or Research Desk PR #158.

## Conversion blocker and safe experiment

Before R308, Grok-to-Atlas campaign labels disappeared on the Atlas-to-free-investigation editorial link. R308 preserves *only* a validated four-field campaign set on the **existing first-party** Apollo 1 investigation URL, without introducing tracking, cookies, user profiles, redirects, sales labels, purchase links, or any new CTA. No Grok post, campaign, human session, product, or sale is asserted live or authentic.

- `utm_source`: exactly `youtube`, `tiktok`, `instagram`, `facebook`, `pinterest`, `x`, or `bluesky`.
- `utm_medium`: exactly `organic_social`.
- `utm_campaign`: exactly `history_pilot_2026_11`, a proposed synthetic November pilot, **not** confirmation that Grok published anything.
- `utm_content`: 3–64 alphanumeric, underscore or hyphen characters, beginning with an alphanumeric character. Syntax alone is **not** an authenticated Grok asset ID.
- All four required; duplicates, PHP-normalized query-key aliases, array values, malformed inputs, missing raw query metadata, and raw strings over 1024 bytes fall back to the unchanged untagged URL. Unknown keys, including email identifiers and advertising IDs, are dropped.
- NASA source links remain exact, untagged, official URLs, distinctly labelled noncommercial. The editorial link stays `data-fv-conversion-kind="editorial-continuation"`, never a paid order.
- The same sanitized output works with JavaScript disabled, including in source-custody failure recovery. Source facts, date reconciliation, rights caveats, photo/media policy and all geospatial exclusions are unchanged.

## Executable QA

From repository root with PHP, Python Playwright and system Chromium:

```bash
python experience2/apollo-r308/qa/source_controlled_gate.py
python experience2/apollo-r307/qa/source_controlled_gate.py
python experience2/apollo-r306/qa/source_receipt_contract.py
python experience2/apollo-r304/qa/gate.py
python experience2/apollo-r305/qa/gate.py
python experience2/apollo-r305/qa/check_rd_crosswalk.py
```

The R308 source-controlled gate tests PHP output on seven permitted platforms, missing/malformed/array-valued inputs, extra PII/advertising-param suppression and 10 real **offline** Chromium viewport/JavaScript contexts (320–1920px), with two instances and keyboard focus. The separate reviewed evidence archive includes an extended 15-negative-input test, screenshots, print PDF, runtime observations, and hashes. Fixture performance is **not** field CWV.

## Release gate (HARD HOLD)

Actual localhost PHP HTTP 200 with a restrictive CSP is possible, but Chromium navigation is blocked by `ERR_BLOCKED_BY_ADMINISTRATOR`; offline `page.set_content` is not HTTP/CSP acceptance. **Genuine axe-core** (library could not be installed via blocked DNS), independent screen readers, installed WordPress/Assembler, actual social campaign links, user consent, editorial rights, hosted CI on exact SHA, and production LCP/CLS/INP remain unverified. No WordPress, merchant, social publishing, email, or paid-services writes authorized.

**One hypothetical journey:** Grok's approved Apollo history long-form → verified Atlas source trail → free Apollo investigation → *separately reviewed, rights-cleared, existing payable offer*, if authenticated. A Mini Museum Apollo 11 collectible is **not** an Apollo 1 artifact and must not be inserted into the accident narrative. Claude owns production analytics and merchant reconciliation; Grok owns content/distribution; Praxxis owns independent creator review; founder owns all release and spending approval.

**KPI after verification:** realized net revenue per 1,000 qualified human sessions, based on merchant-confirmed orders, fees, refunds, and 7/30-day denominators; a UTM string, editorial click, outbound or checkout-start is not a sale.
