# Apollo R452 — Source-preserving conversion proof and review fixture (DRAFT)

Part of [Apollo #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Stack on isolated R451 draft PR #2985. **Not approved for production.**

## Intent, custody and commercialization boundaries
Single relevant funnel: separately verified Grok Apollo documentary → published source-backed Apollo Evidence Atlas → original classroom research activity/source receipt → one unobtrusive [full free investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → **only if founder-approved, verified genuinely sellable** rights-cleared original educator kit. No added checkout, affiliate links, analytics scripts, images, forms, geo pins, WordPress writes, or distribution. Grok owns creator production; Praxxis reviews creator evidence and account; Claude owns analytics/merchant engineering.

Primary historical records: [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) identifies electrical arc as *most probable initiator* without determining precise ignition source. [NASA flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) concerns later experiments and must not establish the original spark. NASA archival media usage and any institutional endorsement must be independently cleared; no NASA image is reproduced here. R448 inherited chronological source manifest remains authoritative for custody; no speculative Atlas geo links.

## Files, no dependencies required for proof checker
- `proof-template.json` — explicit missing founder, Grok, Praxxis, seller, rights, merchant and visitor/cohort evidence (null is not zero).
- `qa/funnel_guard.py` — read-only validator; rejects personal visitor data, incorrect campaign/landing or unverified order structure; computes **structural-only** net proceeds after refunds/fees and 7/30-day cohort ratios only from present reconciled aggregates. Never independently verifies accounts or releases product.
- `qa/test_funnel_guard.py` — 27 adversarial smoke cases.
- `reviewer.html` — isolated, no-JS/keyboard-readable HTML reviewer fixture, **not a live site component**.
- `qa/browser_qa.py` — actual offline Playwright/Chromium page.set_content checks 320–1920. Real staging, axe, LCP/CLS and screen-reader acceptance remain NOT RUN.
- `qa/package_evidence.py` — deterministic archive packing from local evidence.
- The reproducible local QA ZIP is deliberately not committed and is only a **local renderer fixture**, not proof of WordPress integration.

## Replication
```bash
python3 qa/test_funnel_guard.py
python3 qa/funnel_guard.py proof-template.json
python3 qa/browser_qa.py      # playwright and Chromium required
python3 qa/package_evidence.py
```

## Commercial contract and owners
| OFFER | FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Original educator source kit | Paid order | No authenticated SKU/rights/checkout/fulfillment | Verify merchant inventory and test fulfillment with founder approval | HARD HOLD; no sale asserted | Founder + Claude |
| Grok Apollo documentary | Published asset → qualified landing | No confirmed platform URL, asset_id, allowed placement, reviewed link | Praxxis verifies real post; Grok supplies campaign inventory; Claude matches landing | UNKNOWN; unverified campaign discarded | Grok + Praxxis + Claude |
| Atlas chronology → free investigation | Relevant CTA | WP staging and real device interactions unavailable | Test single CTA, original activity and NASA provenance | 27 offline guard and 14 Chromium fixture checks; staging HOLD | Apollo + Independent QD |
| Confirmed paid customers | 7/30d net revenue / 1k qualified sessions | Missing merchant settlements, refunds/fees, qualified-human denominator | Reconcile independent data only, privacy safe | NOT COMPUTABLE, do not equate CTA or signup with paid sale | Founder + Claude |

## Acceptance blockers
Founder production approval, independent QD, R417/public editorial review, approved staging and authentic WCAG/axe, screen readers, p75 LCP/INP/CLS and real transactional evidence are absent. Never label local Playwright page.set_content as navigated staging. PR #49 and PR #158 are frozen/independent. No live writes or paid services.
