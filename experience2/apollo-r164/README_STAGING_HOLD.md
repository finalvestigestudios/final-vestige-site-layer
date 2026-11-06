# Apollo R164 — installed-page Chromium acceptance witness (DRAFT / HOLD)

## Why this work exists
Previous R154–R163 fixture tests are useful but cannot establish the **real WordPress frontend** accepts an independent gallery, actually serves NASA-context media, survives live CSP/theme behavior, or passes accessibility and performance. R164 adds a source-controlled read-only *installed-page* Playwright acceptance witness that must return HOLD when network access, axe-core, or interaction testing is missing. Do not confuse this with an installation or a deployed fix.

**Read-only WP editor source check (2026-11-06):** Published Page 2017 at `https://finalvestige.com/apollo-1-evidence-atlas/`, last modified `2026-11-05T18:19:45`, still contains the chronology controller `const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2)`, which ties unrelated archival images to fire seconds. Current R163 patch remains only a staging candidate, NOT live. Confirmed source has one R163 patch start, one end and one old-note occurrence; 3 NASA photo/source records and one original-investigation CTA. The gallery images are **context**, not measurements of the fatal event. Apollo 204 Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/.

## Execute after staging deployment has been separately authorized
Requires Python Playwright + a Chromium binary, local free axe-core JS supplied by the operator (no SaaS, no analytics). Install or obtain tools through existing approved development environment, do not download at browser runtime.

```sh
python experience2/apollo-r164/live_acceptance.py \
  --url https://YOUR-AUTHORIZED-STAGING-HOST/apollo-1-evidence-atlas/ \
  --out evidence/apollo-r164-installed \
  --axe /path/to/local/axe.min.js
```

**Exit codes:** 0 = controlled-browser lab acceptance with axe complete; 2 = HOLD; 3 = invalid input/tool failure. Even exit 0 does not authorize release. Full `acceptance.json` and 6 PNGs under out; no screenshots uploaded automatically; avoid credential-bearing URLs. Tests 320/360/390/768/1440/1920 CSS widths, reduced motion, no-JS three-source visibility, keyboard Home/Arrow, touch, 44px targets, image decode, source anchors, independent photo and fire-second controls, one editorial investigation link, screen errors and offline lab LCP/CLS. axe WCAG 2.2 AA tags at 390px via **locally provided genuine axe-core**, never a homegrown substitute. Manual assistive-technology and zoom checks remain required.

**Controlled fixture diagnostics (NOT real WordPress):** `--fixture-html path/to/controlled_fixture.html` uses `page.set_content` and always returns HOLD, even with passing checks. Local R163-derived excerpt fixture with placeholder data images produced **88/88 checks passed in each of two Chromium runs**, screenshot PNG hashes **6/6 identical**, and a deliberately reintroduced slider/photo coupling produced **82/88**, failing the intended independence assertion at 390px. These fixtures did not fetch real NASA image bytes. axe was unavailable; genuine axe-core was NOT run. Browser navigation to HTTP(S) addresses was blocked in the restricted execution environment, so **no actual WP installed-page Playwright acceptance and no real-page field CWV evidence exist**. The initial network attempt recorded navigation errors, not a pass.

## Release and commercialization contract
- Until actual installed-site accessibility, CSP, live image delivery, browser performance and QD acceptance and founder approval: **STAGING HOLD**. No WordPress writes/merges/analytics/email/affiliate/social activations by this lane. PR #49 and PR #158 untouched.
- Flagship: Apollo 1 / *Fourteen Seconds, More Than One Failure*. Grok controls scripts/video and distribution; Praxxis controls external review. One contextual action only: *Read the full investigation*.
- Purchase bridge for educators is hypothetical until a **real rights-cleared Apollo-appropriate SKU**, approved checkout and verified merchant order/refund/fee evidence exist. NASA agency identifier/endorsement and astronaut likeness rules still apply: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/.
- Metrics under #820: distinct asset_id and UTMs → qualified-human visit → editorial CTA → verified lead if consented → **confirmed paid order**, net fees/refunds; 7/30 day cohorts and net revenue / 1,000 qualified humans. No conversion claim without denominators and merchant settlement.

Cross-references #150 / #820 / #818. This branch stacks on R163 only; never modify frozen homepage or Claude's branches.
