# Apollo Experience 2.0 R356 — demand-scoped source assets

**RESEARCH-ONLY / DRAFT / NOT LIVE.** Stacked on R355 at `aa484fea03a172fe6738256216ab2a63f48e7988`; separate from frozen homepage PR #49 and Research Desk PR #158. No WordPress, Grok/Praxxis, tracking, merchant, email, publishing or paid service changes.

## Correction

The R355 adapter conservatively enqueues **six CSS assets and one JavaScript asset** for either full composite or its standalone post-fire note. The standalone note has no filter controls and does not require the Atlas code. This R356 adapter registers **two new, separate, opt-in staging shortcodes**:

- `[fv_apollo_postfire_r356]`: later NASA 2018 source note only; **one CSS / zero JavaScript**.
- `[fv_apollo_experience_r356]`: complete Apollo 1 evidence Atlas plus later source note; **six CSS / one JavaScript**.

The immutable upstream text, evidence source custody, 13-entry index, one free editorial continuation, lack of invented geographic pins, print source and rights notices remain unchanged. Source is NASA's [February 14, 2018 flammability-test retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/); it describes **102 deliberate ignitions after the fire**, not a finding from the original accident inquiry.

The reviewed asset files total **2,670 CSS bytes** for standalone versus **19,777 CSS + 3,117 JS bytes** for composite, a **20,224-byte (~88%) reduction in locally measured referenced source bytes**. These are uncompressed filesystem sizes, not observed browser transfer savings or production CWV improvements.

## Executable QA

```bash
php -l experience2/apollo-r356/asset-bridge.php
php experience2/apollo-r356/qa/wp_contract.php
python experience2/apollo-r356/qa/browser_gate.py
```

R356 WP API contract fixture: 11 cases (direct/composite/both, reusable/nested/cycle, unrelated/spoof/non-singular/oversize). Real Playwright Chromium: six source-controlled cases at 320, 390, 768, 1440 and 1920px; note and full modes; no-JS, touch, keyboard native disclosure, 400% root-font stress, reduced-motion, forced colors, evidence filters, named NASA source, unique DOM IDs, horizontal overflow. Native Chromium printed PDF retains NASA source link. Local synthetic LCP/CLS observations are fixtures, not production Core Web Vitals.

## Release blockers (HARD HOLD)

- No installed WordPress/Assembler + Jetpack/cache acceptance. Dynamic theme template parts and late shortcode evaluation may bypass early `wp_enqueue_scripts` discovery; must explicitly test. No retroactive CSS enqueue that could induce CLS.
- No genuine axe-core, NVDA/VoiceOver, Firefox/WebKit or full browser-enforced HTTP/CSP acceptance.
- No hosted green CI, commercially cleared media or product offer/checkout, authenticated Grok asset IDs, verified paid conversions or founder/QD production approval.

**Conversion:** Grok-produced Apollo film → verified NASA evidence → existing free Apollo investigation → relevant educational purchase only after a rights-cleared, payable SKU is independently authenticated. No purchase CTA or new instrumentation here. KPI realized net revenue / 1,000 qualified human sessions is uncomputable without confirmed orders, refunds, fees and attributable qualified visits.

Coordination: Issues #150, #820; charter #818; TASK-008 in Drive. Grok owns scripts/distribution, Praxxis owns external creator QA, Claude owns core site/analytics, founder owns release.
