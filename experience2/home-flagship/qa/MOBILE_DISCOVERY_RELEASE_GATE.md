# EX2 flagship — mobile discovery and Focus-CTA admission
Date: 2026-11-09 PT · Review-only · **NOT** production acceptance

## Source-grounded accessibility/conversion defect
At <=920 CSS px, the seven-chapter study hides its sole desktop masthead links through `.fv-hf__nav{display:none}`. Investigations, Public Record and Library therefore lose their *masthead* routes in the study at tablet/mobile widths, although the separate WordPress production theme currently supplies its own navigation. The Focus CTA remains elsewhere; this is **not** a claim that live production has no navigation. All four destinations were checked as publicly reachable via read-only requests on 2026-11-09.

## Change / experiment
Add one native `<details><summary>Explore site</summary><nav>...</nav></details>` in the existing masthead, with the **same three editorial destinations** as desktop. No new chapter, library record, paid service, script, tracking, email, opt-in, merchant claim or artwork. Restore links with **JavaScript disabled**, preserve keyboard Enter/Space behavior without custom JS, and give native menu and links 44px hit areas. Preserve the high-intent Focus Fieldbook as the distinct direct action; under <=560px it sits in its own full-width row and an open menu cannot occlude it.

## Evidence available this run
- Source inspected at exact parent PR #1780 SHA `4ebe69cd0194376df24e7135a214d23eccc1cd9b`, existing CSS hides the desktop masthead nav at 920px and below.
- Local **component fixture**, real headless Chromium: **16/16** width×JS conditions passed at 320/390/560/768/920/921/1440/1920, with JS ON and OFF. Checked native keyboard open/close, actual three routes and CTA, 44px target geometry, CTA not overlapped by open panel, and horizontal overflow. Screenshots saved locally for 320/390/768/1440 before/after (not shipped as binary assets).
- This fixture is a **representative component constructed from verified masthead/CSS rules**, not the complete exact-source WordPress render. The committed `verify_mobile_discovery.py` is designed to read **actual candidate** `index.html` + `flagship.css` when run in a full checkout. It has **not** run inside real WordPress or GitHub CI. Do not promote fixture evidence into WCAG/Lighthouse acceptance.
- Original historical/archival rights and source records remain governed by #1730; no new media or historical claim.
- Full seven-chapter QA, genuine 200% browser zoom, axe WCAG 2.2 AA, mobile touch devices, first-party transfer bytes, Lighthouse/CWV, WordPress/Assembler + Jetpack and independent QD remain **HOLD**.

## Reproduce from exact branch checkout
```bash
python -m py_compile experience2/home-flagship/qa/verify_mobile_discovery.py
python experience2/home-flagship/qa/verify_mobile_discovery.py
python experience2/home-flagship/qa/verify_mobile_discovery.py --browser --out /tmp/fv-mobile-nav
```
Requires Python Playwright and Chromium at `/usr/bin/chromium` for browser option. The harness intentionally fails closed if unavailable.

## Conversion mandate
OFFER: Existing free 52-page Seven Day Focus Fieldbook (not a sale). FUNNEL STEP: mobile archive discovery and contextual Focus access. BLOCKER: missing study masthead navigation at <=920px. CHANGE: native accessible editorial navigation, preserved clear direct CTA. EVIDENCE: component fixtures pass; **no verified change to visitors, leads or paid orders**. OWNER: homepage engineering for candidate QA; Claude for event instrumentation; Site QA/QD independent acceptance; founder for any production release.

Upstream Focus signup-success integrity (#1681) **still blocks** aggressive conversion CTA expansion. Keep PR #49 frozen. WordPress production page ID 6, Jetpack and the 72 Margins items are untouched. WordPress.com Personal has no native staging clone; isolated Playground/developer site differs from production hosting and cannot certify Jetpack or field CWV.
