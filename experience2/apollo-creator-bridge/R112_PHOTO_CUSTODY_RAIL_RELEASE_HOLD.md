# R112 — photographic provenance and classroom source-trail QA (STAGING HOLD)

**Date:** 2026-11-04. Parent #150; business/control #820 and charter #818. Original Research Desk draft #158 and frozen homepage #49 untouched. Isolated branch `qa/apollo-r112-photo-provenance-browser-20261104`, stacked on R111 `9bb61b250d7e4123d5161f50144097c899818ada`. No WordPress edits or deployment.

## Conversion-first problem and bounded change

An educator arriving from a future Grok Apollo video needs to separate **claims about the fire on 1967-01-27** from **photos taken before, after and 50 years later** before trusting a classroom exercise. The existing six NASA custody records were present but could not be navigated by time period without scanning a wide table. This increases mobile/screen-reader research friction at the exact trust-to-classroom step.

R112 adds one self-contained, **no-JavaScript photo-provenance navigation** linked to six unchanged NASA source rows. Periods are clearly marked as contextual photograph dates, not a reconstruction or sorted proof of causality. The January 1967 crew photo retains its unknown day and provisional `S67-19766` association, and 2017 images are explicitly retrospective exhibits. Source links still open official NASA pages; no photo binary is embedded or represented as commercial-use-cleared. The rail is not a geographic Atlas: no invented pins, location paths or edges.

Focus-visible treatment now covers the **keyboard-scrollable table region** as well as an anchor-targeted evidence row, including `forced-colors`. R112 also clarifies that the roughly fourteen-second headline describes the interval from the first recorded fire report to pressure-vessel rupture, *not* the duration of ignition-to-death; ignition is unproven. The single primary free classroom exercise CTA and its source-return link remain unchanged. No added signup, tracking script, affiliate, checkout or product claim.

## Reproduce against the exact branch source

```bash
python -m unittest discover -s experience2/apollo-creator-bridge -p 'test_r11*.py' -v
python experience2/apollo-creator-bridge/qa_r108.py --output /tmp/apollo-r112-http
# With an already-approved local axe bundle only:
python experience2/apollo-creator-bridge/qa_r108.py --output /tmp/apollo-r112-http-axe --axe /path/to/approved/axe.min.js
```

The existing HTTP browser runner uses real Chromium/Playwright and is extended to click or keyboard-activate source #05 from its chronological rail at 320, 360, 390, 768, 1024, 1440 and 1920px, **with both JS enabled and disabled**. It checks six source anchors, target row, date match, no rights-unreviewed imagery, original single free CTA, NASA disclosures and no third-party requests. The unchanged local laboratory budget requires six valid LCP <=2500ms/CLS <=0.1 trials, with screenshots/checksums. These are development-lab budgets, not hosted p75 CWV.

## What is actually verified, not inferred

- **BUILT**: source-controlled HTML/CSS and real HTTP browser regression updates; one new Python source-contract suite.
- **TESTED**: 13/13 V8-based *exact GitHub source* structural contract assertions over committed branch file blobs (six rail links/targets, NASA link identity, no imagery or purchase form, focus CSS, 14-mode QA coverage and unchanged lab thresholds).
- **COMPONENT-FIXTURE BROWSER TESTED (NOT THE REAL PAGE):** local Chromium using in-memory HTML exercised 14/14 viewport/JS configurations, native source-link keyboard/touch navigation, six custody anchors and no page overflow, with 6 SHA-256 screenshots. Fixture archive SHA-256 `dbfb3dc4fed954cc2f7b5a5e4e273072ca98bc501f1032dac4ab947eba91fbf6`. The actual candidate's HTML was not loaded in this test.
- **INFRASTRUCTURE BLOCK:** Chromium attempts to navigate the disposable `127.0.0.1` HTTP fixture received `net::ERR_BLOCKED_BY_ADMINISTRATOR`. In-memory DOM testing worked; local HTTP lab LCP/CLS **cannot be measured** here, and no threshold was relaxed.
- **NOT YET TESTED**: complete R112 Python unittest execution, exact-R112 real Chromium/axe matrix, actual-page screenshots, LCP/CLS observations, genuine disposable WordPress/Assembler integration, manual device/screen reader. Do not treat 13 source assertions as a browser pass. GitHub Actions runner failure from R104–R107 may persist; check exact-head CI status separately before acceptance.
- **LIVE (separate version only)**: existing WordPress page 2017 `/apollo-1-evidence-atlas/` was independently reported published on Nov 3; this R112 candidate is **not deployed** there. The site's publishing approval / release artifact reconciliation is still with Claude/site release/QD.

## Commercial experiment: one high-intent action, not an invented sale

| Priority | OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| P0 | **Proposed** Apollo teacher-ready source casefile → actual purchase | No independently merchant-verified Apollo SKU, license, deliverables or rights clearance | Verify existing Payhip offers; validate buyer interest before any casefile checkout | **BLOCKED**; no sale, merchant order or net revenue verified | Claude/Growth/founder |
| P1 | Grok Apollo long-form/Shorts → landing source proof → free exercise | No released Grok Apollo asset/campaign; table source navigation was slow on mobile | R112 chronological provenance rail + accessible source anchors, test actual browsers before any integration | **BUILT; source-contract TESTED; browser FAIL/UNKNOWN** | Apollo; Grok scripts/distribution; Praxxis external review |
| P2 | Classroom exercise → relevant *verified* paid listing | No approved matching merchant offer and product QA | Conditional contextual paid CTA **only after** seller-origin proof and founder approval | **NOT VERIFIED** | Claude/Site QA/founder |
| P3 | Paid order → net revenue per 1,000 qualified humans (7/30 days) | No campaign asset IDs, qualified human sessions or independently reconciled orders/fees/refunds | Reuse #820 canonical UTMs and existing consent-compliant measurement; no duplicate scripts | **NOT COMPUTABLE** | Claude/Growth |

**Release hold:** no commercial offer activation without independent product verification, rights and delivery review, founder approval. NASA photo reuse remains 0/6 individually cleared and `S67-19766` provisional. Confirm p75 hosted CWV, WordPress compatibility, manual accessibility, independent editorial/QD review and page 2017 publication provenance prior to any live action. Nothing here claims an affiliate sale, subscriber, paid order, published Grok asset or verified referral revenue.
