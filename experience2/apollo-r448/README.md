# Apollo Experience 2.0 · R448 — Claim/Custody Crosswalk

Independent additive staging-only `experience2/apollo-r448/` work. Source of truth: Experience 2.0 [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), business metrics [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), business charter #818. Stacked on R447; frozen homepage PR #49, initial Research Desk PR #158 and Grok/Praxxis TASK-008 are unchanged.

## Historical/source improvement
The R447 2017 image-catalogue URL remained **NOT RECHECKED**. We do not silently assert that it was verified. R448 uses a different official [NASA Jan 27, 2017 tribute announcement](https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/) as an independent, verifiable source for the exhibit, without presenting it as a fix to the old image ID. Four deliberately differentiated dates/records: Oct 18, 1966 photograph caption, Jan 27, 1967 accident date analyzed in the later Review Board report, Jan 27, 2017 museum opening and press release, Feb 14, 2018 publication of retrospective on post-fire testing. Each states what it does and does not establish, and image/likeness boundaries. NASA logo, photos, third-party media, geographic pins and relationship edges are absent.

## Staging adapter
Shortcode: `[fv_apollo_claim_crosswalk]`. Registration requires `ABSPATH`, `wp_get_environment_type()==='staging'` and explicit `FV_APOLLO_R448_ENABLE_STAGING===true`; otherwise nothing registers. Manifest, CSS and JS are SHA-256 pinned. Missing/tampered data/assets fail open to a plain free-investigation link. If JS fails, all four source/limit paragraphs and native details remain readable. Opt-in source-era filtering is fully keyboard/touch accessible; every instance has unique IDs.

## QA
`python -m unittest discover -s qa -p 'test_*.py' -v`
`python qa/browser_qa.py`
`python qa/staging_gate.py` (without verified HTTPS staging origin and genuine approved/pinned axe-core: **HOLD_NOT_RUN**; intentional). `python qa/package_evidence.py` produces deterministic artifact ZIP.

Local Chromium tests use `page.set_content` on authentic PHP markup. They **do not** constitute actual WordPress staging, axe, navigated LCP/CLS, field CWV, screen-reader acceptance, or exact-head CI. The staging gate can only pass on approved same-origin HTTPS staging with real axe and browser metric evidence; it rejects writes, redirects, unapproved third-party calls and production domains. No deployment performed.

## Business release gate: HARD HOLD
**Offer:** proposed original Apollo educator evidence kit; **funnel:** Grok published long-form → approved link → source-backed Atlas → free investigation → separately approved paid kit; **blockers:** no verified Grok Apollo asset ID, no authenticated rights-cleared paid SKU, checkout/fulfillment, qualified-human sessions or merchant reconciled orders; **experiment:** explicit claim boundaries increase trust without injecting commerce; **evidence:** offline unit/browser results only, actual conversion **UNKNOWN**; **owner:** Apollo for trust/QA, Grok/Praxxis for publishing and independent review, Claude for commerce/measurement, founder for final signoffs. Key revenue-per-1k-human-sessions KPI is NOT COMPUTABLE pending 7/30-day qualified cohorts and net settlements. No CTA change, tracking, paid services, WordPress writes, email or social post.
