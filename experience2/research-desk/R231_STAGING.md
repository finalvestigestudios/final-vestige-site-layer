# Apollo Experience 2.0 — R231 NASA source-role correction (STAGING HOLD)

**Parent:** R230 draft PR #1693, commit `6b74405b172cc9b42842268aa3dc2379d55d17ad`. **Upstream:** Research Desk PR #158 at `250d7f05a4de037e73826dcf0cfaef0ec4c29383`. This is an isolated, mutually exclusive candidate; leave PR #158, PR #1693, Atlas PRs, homepage PR #49, production WordPress and the live theme untouched.

## Why this sprint matters

R230 independently discovered a **misleading evidence pairing** in the real six-record Research Desk template. NASA S66-58038 is titled *CHAMBER - ALTITUDE - APOLLO/SATURN (A/S)-204 - ASTRONAUT TRAINING - KSC*, not a telemetry chart. NASA KSC-20170124-PH_KLS01_0164 and KSC-20170124-PH_KLS01_0090 are *Apollo 1 Tribute* photographic records from 2017, not photographs taken during the January 1967 fire or of subsequent technical tests. Readers must not mistake a linked context photograph for the technical proof backing a claim.

## Source-controlled implementation

- `templates/ledger-r231-source-scope.html`: deterministic derivative of exact R158 template (Git blob `403d128c57b9bc82dac7c619651689070edef86c`). Only records **03, 04, 06** are reclassified. Each adds an explicit visible source-role limitation and the original technical support. Cards **01, 02, 05** are byte-identical to R158 originals. Final derivative Git blob: `0fd4f9ddadb3473110d2709a52332a78fa4ac04a`. The original is preserved.
- `fv-ex2-r231-runtime.php`: isolated alternative to R158/R230 WordPress shortcode. Its PHP verifies the **complete exact source HTML** by Git blob SHA-1 before display, plus three expected evidence-scope notes, and falls back to the original free investigation on mismatch, missing template or empty content. It retains late stylesheet recovery, duplicate-instance unique IDs and optional JS.
- `assets/source-ledger-r231.js`: the optional filter now indexes **rendered source text**, so visitors can search newly visible distinctions such as “altitude-chamber”; the original static `data-fvx-search` string previously omitted added evidence context. No network, storage, external scripts or analytics.
- `assets/source-ledger-r231.css`: original R158 CSS plus scoped minimum **44px** source-proof links and keyboard-visible focus, including forced-color support. No visual redesign or imagery changes.
- `qa/r231_smoke.php`: actual PHP + **exact checked-out** derived NASA template, two shortcode instances, bound source and tamper fallback; it runs without WordPress and leaves tracked original files untouched.
- `qa/r231_playwright.py`: executable test harness for the **actual checked-out** R231 PHP, HTML, CSS and JS across 320/390/768/1440/1920 CSS px, JS/no-JS, keyboard/touch, overflow, source-scope, CTA, optional real axe-core using a reviewer-supplied local `axe.min.js` path. **This script is committed but has not been run on a full GitHub checkout in this environment.**

Source references: NASA altitude-chamber record https://www.nasa.gov/image-detail/amf-s66-58038/ ; NASA tribute records https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ and https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ ; technical fire findings https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; later engineering response https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/ .

NASA source pages are linked for review. **No NASA photographs, emblems or insignia are reproduced in this correction.** The presence of a NASA source URL is *not* authorization for commercial reproduction, nor an endorsement. See NASA advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ .

## Verification actually performed

1. **GitHub source/static audit PASS:** exact R158/derived record crosswalk; 6 original cards and 3 scope notes; records 01,02,05 unchanged; exact PHP template Git-blob pin; approved external URLs only (17 links / 10 destinations); search indexes rendered text; optional CSS gives source links 44px min height.
2. **Local PHP lint PASS** for byte-identical current R231 adapter Git blob `1d00472af067e647859d1fd2631d87b5bdf5bc67`.
3. **Two independent local component-simulation runs PASS:** 5 PHP lifecycle cases and corrupted synthetic-source fail-open, 10 Chromium contexts each across 320–1920 CSS px × JS/no-JS, source term search, keyboard/touch native disclosures, responsive no-overflow and single investigation CTA. **10/10 screenshot hashes and QA receipts reproduce between runs**. Deterministic component receipt SHA-256: `ba364c339f3d3a7c20c0b8f55d323d08c7779f863083df81af0cc544b83bc512`.
4. **CRITICAL limitation:** local browser cases used a six-record **synthetic fixture** and synthetic CSS with a behavior-equivalent script. The actual R231 PHP file was tested with only its **template hash constant swapped to the synthetic fixture hash in a temporary test copy**; the permanent GitHub version and its original hash remain intact. Do not claim the complete NASA template or true R231 CSS/JS passed browser QA here. Real axe-core was unavailable, and no installed WordPress/Assembler QA, NVDA/VoiceOver, actual browser zoom, localhost transport, hosted CI or production p75 LCP/CLS was completed.

### Exact checkout acceptance commands (reviewers; no deployment)

```bash
php -l experience2/research-desk/fv-ex2-r231-runtime.php
php experience2/research-desk/qa/r231_smoke.php normal > /tmp/r231-normal.json
php experience2/research-desk/qa/r231_smoke.php duplicate > /tmp/r231-duplicate.json
php experience2/research-desk/qa/r231_smoke.php tampered > /tmp/r231-tampered.json
python experience2/research-desk/qa/r231_playwright.py --repo . --out /tmp/r231-browser
# Optional real axe, if a trustworthy pinned local copy is installed:
# python experience2/research-desk/qa/r231_playwright.py --repo . --out /tmp/r231-axe --axe-js /path/to/axe.min.js
```

Browser navigation to actual WordPress staging must additionally prove CSS/JS delivery from nested or reusable blocks, no conflicting original plugin, screen readers, actual zoom and theme conflicts. Test an approved `[fv_ex2_research_desk]` shortcode only on isolated staging after the founder's governance approval. The inherited R198 canonical-source ancestry discrepancy and hosted CI spend block still require resolution.

## Conversion-first contract — Issue #820 / charter #818

One immediate visitor action only: Grok's **not-yet-verified** Apollo asset → NASA-supported Research Desk → **Read original Apollo investigation** (free). Keep the narrative free of unrelated advertising. A potential Apollo educator dossier is **not** an approved product or purchasable SKU. Mini Museum publicly offers meteorites, but an Apollo-specific affiliate approval, approved tracked link, purchase evidence and contextual editorial placement are unverified; **do not add any merchant CTA yet**. Grok owns creator assets/links, Praxxis independently reviews them, Claude/commerce verifies SKU, tracking and checkout, the founder controls live approval.

**Offer → Funnel step → Blocker → Change / experiment → Evidence → Owner**
- Paid educator dossier → order → no rights-cleared purchasable offer → founder/Claude validate deliverable, checkout and fulfillment → BLOCKED → Founder/Claude.
- Grok long-form → R231 → published asset ID/destination not proven → reconcile TASK-008 source-linked post inventory and UTMs → UNVERIFIED → Grok/Praxxis.
- Research Desk → free investigation → contextual image implied technical proof → R231 source-role correction and rendered-text search → GitHub static PASS; synthetic browser PASS; real install BLOCKED → Apollo/Site QA.
- Paid transaction → realized net → no qualified human-session denominator, authenticated orders, fees or refunds → 7/30-day measurement and merchant reconciliation → NOT COMPUTABLE → Claude/Commerce.

Do not conflate impressions, outbound taps, leads or checkout starts with confirmed purchases. Primary KPI **net realized revenue per 1,000 qualified human sessions**, with 7/30-day cohorts and small-sample flags.

**RELEASE: HARD STAGING HOLD.** No merge, deployment, WordPress writes, Grok posting, email, affiliate activation, analytics changes or spending. Link issue #150 and cross-reference #820 before requesting independent review.
