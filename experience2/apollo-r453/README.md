# Apollo R453 — creator proof custody and real-navigation preflight (DRAFT / HARD HOLD)

Scope: **only `experience2/apollo-r453/`**; stacked on draft Apollo R452. Do not touch frozen homepage PR #49, original Research Desk PR #158, Claude engineering, Grok production, Praxxis review queue, WordPress or analytics. [Apollo issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); [conversion contract #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

## Concrete integrity problem found and contained

R452 `qa/funnel_guard.py` correctly labels every result structural-only and holds production, but its `validate_campaign()` uses `exact_url()` without a host constraint. A malicious HTTPS URL can therefore be marked **STRUCTURALLY_DOCUMENTED_REQUIRES_EXTERNAL_REVIEW** if other strings claim independent publication. This is *not* a demonstrated compromise or fabricated actual traffic; it is a review-integrity weakness that increases risk of misclassifying creator attribution.

R453 adds an additive, SHA-pinned `qa/authenticity_guard.py` that only accepts **canonical YouTube/Shorts/live/youtu.be or TikTok video URL shapes matching the declared platform**; rejects subdomain spoofing, credentials, fragments, redirect parameters, duplicate IDs, encoded control characters, malformed IDs and other non-video pages. A valid URL shape is expressly **not actual post-publication proof**. `qa/test_authenticity_guard.py` has 12 passing adversarial test methods including 20 malicious URL shapes. Every result remains `HARD_HOLD` and realized net revenue remains `null`, not $0. This isolated overlay does not alter R452 or authenticate any external service.

## Actual browser navigation attempted and blocked

`qa/http_navigation_probe.py` is a reusable, source-controlled Playwright tool which locally serves the **actual inherited R448 PHP-rendered NASA crosswalk** through an HTTP listener and attempts `page.goto`, real CSS/JS interaction with JS on/off at 320/360/390/768/1024/1440/1920, keyboard and one free CTA, screenshot capture and **local-only lab** LCP/CLS diagnostics. The sandbox returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` navigating even to `127.0.0.1`. The probe explicitly records `HOLD_NOT_RUN`, zero browser cases executed, no screenshots and no LCP/CLS values. **Do not claim a navigated browser PASS, true axe-core, hosted WordPress staging, independent screen reader review, or p75 field CWV.** A suitable approved runner may subsequently execute it; it remains local PHP, not real WordPress integration. The preexisting R450 HTTPS staging gate separately requires an approved staging URL and independently reviewed axe SHA-256.

## NASA and editorial boundaries

R448 NASA source manifest remains inherited, unmodified, with four differently dated source/event records. [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) calls electrical arcing the most probable initiator without establishing one conclusive ignition source. [NASA's 2018 later flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) is not evidence of the actual original spark. [NASA media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) requires separate advertising/likeness review; no NASA images or logos copied, no unreviewed geospatial pins, no invented linkage.

## Run tests from a full checked-out stacked branch

```sh
python3 experience2/apollo-r453/qa/test_authenticity_guard.py
python3 experience2/apollo-r453/qa/authenticity_guard.py experience2/apollo-r452/proof-template.json
python3 experience2/apollo-r453/qa/http_navigation_probe.py
```

These commands are local read-only checks. The two Python proof checks require identical R452 base Git blob `86537e55ebb5b7da546e9361626adcc083d7e60b`. They do not post to social media, install tracking, send email, call paid APIs, install plugins, enable commerce, or update WordPress. The browser probe attempts a local-only listener, never production.

## Release gate

Existing R417 source discrepancy and public Atlas editorial-review labeling still need reconciliation; source/media rights and independent QD remain pending; actual installed staging, genuine axe, LCP/CLS/INP p75, real Grok Apollo post and allowed profile/caption link, seller-accepted rights-cleared payable educator kit, fulfillment, merchant settlements/fees/refunds and approved 7/30 day human-session cohorts are all unverified. Green exact-head CI, founder visual/commercial approval and independently governed deployment are still required. No merge, production activation, payments, publishing or spend.
