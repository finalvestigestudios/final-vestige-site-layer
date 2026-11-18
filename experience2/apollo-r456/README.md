# Apollo R456 — Evidence Claims Review (isolated staging prototype)

## Why this addition exists

This is **not another checkout module**. The strongest Apollo video hook is a specific mistaken claim: that NASA identified the exact wire that caused the fire. This source-custody exercise compares that statement against the Apollo 204 Review Board, distinguishes the later 2017 memorial from a contemporary accident record, and separates 1967–1968 flammability experiments from proof of the original ignition. It is intended as a trust-and-relevance bridge for educators viewing a *verified published* Grok documentary, with exactly one free investigation CTA. No unverified creator attribution is injected.

## Canonical facts, official agency links and rights

1. NASA Apollo 204 Review Board, https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — event date 1967-01-27, NOT report publication; probable electrical arc, no conclusive single ignition source. Source links only; no images copied.
2. NASA Apollo 1 tribute, https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/ — release 2017-01-27, exhibition hatch, **not** fire causality. No museum images copied.
3. NASA Apollo Flammability Tests, https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/ — publication 2018-02-14 about subsequent 1967–1968 tests. Tests cannot locate original spark. No photos copied.

The evidence is sourced to NASA; the independent FV presentation is not NASA-endorsed. Images/likenesses/insignia are excluded, not blanket licensed. The purported 2017 image catalogue identifier from R447 is not used. No geographic pins or inferred edges.

## Integration contract

Shortcode: `[fv_apollo_claim_review_r456]`. The PHP file registers nothing unless `FV_R456_ENABLE_STAGING === true`, a positive integer `FV_R456_STAGING_PAGE_ID` is configured, `wp_get_environment_type()` equals `staging`, and the shortcode is on that exact queried page. Uninstalled by default. Read-only and no paid service. Do not alter PR #49, PR #158, Claude's production branch, Grok's queue or any WordPress setting/content.

`fv456_valid` enforces canonical NASA URLs, strict date validity and order, unique case IDs. CSS/JS SHA-256 are verified at render. Missing or modified assets produce a **free-article fallback**. Without JS all cases and `<details>` sources render; with JS controls disclose focused one-of-three claim views. Print displays all cases. Inlines are staging prototypes, **CSP and host theme interaction must be reviewed before production**.

## Local QA and production hold

- `python qa/test_contract.py` — 11 source, source-custody, URL-tamper, date, fallback and staging-guard tests.
- `python qa/browser_qa.py` — Chromium `page.set_content` of actual PHP output across 320, 360, 390, 768, 1024, 1440, 1920px; JS/no-JS, keyboard, touch, forced colors, reduced motion, print, zoom, independent copies.
- `python qa/hosted_acceptance.py` — fail-closed HTTPS staging navigation, approved local axe bundle with pinned SHA, instrumented LCP and CLS, responsive screens. Produces `HOLD_NOT_RUN` without explicit approved host and axe file. This script has NOT supplied hosted staging evidence.

**Unverified:** actual installed WordPress/staging, genuine axe-core, navigated LCP/CLS, manual screen-reader acceptance, field Core Web Vitals, exact-head CI, approved product/checkout, any Grok Apollo video actually published, qualified-human visits or sales. No release without independent QD, rights, editorial, founder approval and green exact-head CI.

## Conversion decision / ownership

Offer: an **original** Apollo educator evidence kit, PROPOSED ONLY; commercial readiness requires separate rights-cleared SKU, checkout, delivery and settlement verification (Founder/Claude). Qualified journey: verified Grok long-form video (Grok + Praxxis) → official-source Evidence Claims Review (Apollo QA) → one free complete investigation CTA → separately approved educator offer. Paid order and net revenue are *not* inferred from CTA clicks. Instrument only through Claude's existing consent-safe measurement layer if separately approved; no new tracking added here. Cohorts 7/30 days; net revenue per 1,000 qualified-human sessions remains NOT COMPUTABLE.

Coordination: #150 implementation and release gate; #820 revenue provenance; #818 business charter; PR #158 Research Desk source custody; PR #49 frozen homepage. Stacked on R455 PR #3001 only. Draft branch is NOT authority to deploy or merge.
