# Apollo R307 — custody-to-continuation return (STAGING / NOT LIVE)

Source of truth: [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); conversion charter [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) / [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

## Defect / experiment

In R306, a viewer who opened the new three-record source receipt could jump to an individual NASA catalogue record but had no direct return to the existing *free investigation* decision point. The only visible return link went back to the corresponding evidence plate. R307 provides a source-to-existing-continuation route per catalogue entry. This reduces *navigation friction* in the evidence-led journey; it does not establish improved revenue.

- Adds `id="fv-r281-N-continue"` and `tabindex="-1"` to each existing continuation footer, within the current shortcode instance.
- Adds one contextual same-instance fragment link to each of the three source records. Native fragment focus and visible outline work without JavaScript. Text survives CSS failure.
- Retains the original source-to-evidence link in its original wrapper (for inherited QA compatibility). Print hides the extra return navigation.
- Stylesheet version `r307-c85b6b2d9dd9` is bound to the reviewed CSS SHA-256 prefix.
- **No** extra purchase or editorial CTA, UTM rewrite, marketing event, API call, geospatial pin, map edge, image, WordPress setting or production write. `data-fv-conversion-kind="editorial-continuation"` stays editorial/noncommercial.

## Run executable QA from the checked-out repository

```bash
python experience2/apollo-r307/qa/source_controlled_gate.py
python experience2/apollo-r306/qa/source_receipt_contract.py
python experience2/apollo-r304/qa/gate.py
python experience2/apollo-r305/qa/gate.py
python experience2/apollo-r305/qa/check_rd_crosswalk.py
```

Actual local Chromium / Playwright on the *offline PHP fixture* exercised 10 width/JS contexts (320, 390, 768, 1440, 1920), 2 shortcode instances, 60 keyboard source-to-continuation journeys, 20 deliberately corrupted cross-instance links, forced colors, touch, reduced motion, 200% text, CSS-off/no-JS and screenshots/PDF. The original R306 component **fails** the new navigation contract as expected, while R307 passes. Inherited R304/R305/R306 tests passed after keeping the original source-return anchor unchanged.

**Not verified:** genuine axe-core (blocked installation/DNS), standalone native browser HTTP navigation (Chromium reports `ERR_BLOCKED_BY_ADMINISTRATOR` even with proxy bypass), installed WordPress/Assembler, independent screen readers, production LCP/CLS/INP, editorial/rights release and founder authorization. Fixture LCP/CLS measurements are not field CWV.

## Historical / usage boundaries

NASA's [Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) did not conclusively identify a single ignition source. The [proceedings](https://www.nasa.gov/history/Apollo204/proceed.html) record the January 28 meeting, while NASA's own establishment accounts vary between January 27 oral authorization and January 28 descriptions. These records share institutional custody; they are not independent eyewitnesses. See [NASA's advertising and branding guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/): no NASA endorsement or rights clearance is inferred. No NASA photograph appears in this PR.

## One potential conversion path, still blocked

**Grok long-form Apollo history audience → source-verifiable Atlas → free Apollo investigation → independently approved, relevant collectible/education offer.** A separate potential offer is Mini Museum's Apollo 11 Command Module Foil in its publicly listed Air & Space Collection. Apollo 11 is **not Apollo 1**; its fit and visitor purchase intent must be tested separately, without inserting a product pitch into the accident history. FV-specific affiliate approval, usable tracking link, seller settlement evidence and checkout rights are **unverified**. This PR inserts **no** merchant link.

**Measurement:** actual Grok `asset_id` / platform-tagged qualified-human sessions → landing view → editorial continuation → relevant approved offer view/click → merchant-confirmed paid orders → refunds/fees → realized net revenue; 7/30-day small-cohort caveats. Do not treat NASA source links, editorial clicks, affiliate outbound or lead capture as paid orders. Claude owns measurement and core website engineering; Grok owns creator output, Praxxis independent creator QA; founder owns approval/release.

## Isolation / release

Stacked on R306 draft PR #2175, not on homepage PR #49 or Research Desk PR #158. No changes to either branch. No merge/activation/deployment without independent source and rights review, real accessibility/WordPress QA, green CI on the exact HEAD and explicit founder approval.
