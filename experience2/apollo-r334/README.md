# Apollo R334 — Research Desk source-role crosswalk (STAGING ONLY)

**Release: HARD HOLD.** Standalone, opt-in read-only WordPress shortcode `[fv_apollo_custody_r334]`. Its new six-card Research Desk source-role crosswalk distinguishes contextual NASA image catalogue links from NASA institutional historical/documentary source links. It does **not** alter existing Research Desk PR #158, Apollo Atlas/ChronologyRail runtime, frozen homepage PR #49, WordPress content/settings, creator assets, analytics, merchant or affiliate systems.

## Why this change is needed

The authentic six-record source template in PR #158, Git blob `403d128c57b9bc82dac7c619651689070edef86c`, presents NASA image-detail URLs first under a generic `NASA archive record` label; examples: Evidence 02 `S67-15717` is styled `PRIMARY REVIEW BOARD RECORD`, and Evidence 03 `S66-58038` is styled `INSTRUMENT CHRONOLOGY`. Those photograph accessions are contextual records, **not by themselves Review Board findings, proof of a precise ignition point or commercial media clearance**. The original cards have a separate NASA documentary link. This adapter preserves the six identities and exact twelve underlying URLs but makes source roles and the unresolved rights boundary visible. It does not claim that all historical card interpretations or six media reuse rights have been independently cleared.

The 1967 [NASA Review Board findings](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html) state that no single ignition source was conclusively identified; electrical arcing was considered the most probable initiator. Do not replace that qualification with certainty or imply NASA endorsement.

## Files and behavior

- `apollo-custody-crosswalk.php`: standalone namespaced shortcode, explicit six-source allowlist and fail-closed source-role validation, escaped outputs, native `<details>`/`<summary>` comparisons, one free editorial continuation.
- `assets/custody.css`: optional styling scoped to `.fv-r334`; 320px to 1920px and 400% text fit, forced-colors focus, reduced-motion, print; unstyled and JavaScript-disabled content remains readable.
- `qa/render.php`: deterministic PHP rendering harness without an installed WordPress application.
- `qa/browser_gate.py`: executable Playwright Chromium fixture for source-role links, six identities, one noncommercial continuation, native keyboard, touch-device emulation, forced-colors, reduced-motion, JS/no-JS, 320–1920px, 400%-text reflow, PDF links/privacy and three unsafe DOM mutation controls. Run `python experience2/apollo-r334/qa/browser_gate.py` in a repository checkout with PHP, Chromium, Python Playwright and PyMuPDF installed. No network required.

## Local results (2026-11-13 PT)

- Eight actual Chromium rendered contexts PASS: JS disabled at 320/390px; JS enabled at 320/390/768/1440/1920px; additional 320px at 400% root text. All 13 links have text, visible geometry after disclosure opening, and no horizontal overflow.
- Six photo catalogue links remain labeled contextual; six historical/documentary links remain distinct. All twelve target their original NASA URLs. One and only one link continues to the **free** [Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). Zero invented coordinates/edges.
- Native Enter disclosure works with and without JS. Touch context was emulated, but independent physical-device acceptance was **not** conducted. Forced colors, reduced-motion and CSS print rules were exercised in local Chromium. Three synthetic unsafe DOM mutations (unauthorized merchant URL, invented geo pin and unsupported commercial media clearance) were rejected by the test.
- Browser-generated print PDF: three pages, 13 URI annotations, no UTM strings. Browser screenshots and executable JSON receipt are in the separate evidence archive.
- The LCP/layout-shift entry diagnostic on an offline `set_content` fixture had **no entries**; this is **NOT an LCP/CLS measurement, passing score, or production Core Web Vitals result**.

## Conversion-first gate

**One proposed audience and path:** Grok Apollo long-form viewers looking for evidentiary explanation → this source-role crosswalk/verified NASA evidence → free Apollo investigation → **potential** educator evidence product after founder/Commerce authenticates a genuinely payable, owned or licensed, rights-cleared SKU, checkout, fees and refunds. No confirmed Apollo campaign asset ID, permitted mobile URL, offer inventory, settled order or qualified-human 7/30-day denominator was established in this sprint. No commercial offer is embedded in the historical cards. Net revenue per 1,000 qualified sessions remains **NOT COMPUTABLE**. No new telemetry or consent flows added.

## Blocked release gates

Installed WordPress/Assembler/CDN, actual staging shortcode/theme interaction, hosted CI exact HEAD, axe-core, independent screen readers, Firefox/Safari/physical touch, native browser HTTP/CSP, production LCP/CLS, NASA photo use permissions and editorial review, PR #158 owner-approved labels, QD acceptance, actual Grok asset/landing destination, authenticated paid SKU and founder production release authorization. **No automatic deployment, production write, social post, merchant action or spending.**

Coordination: [Experience Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [Research Desk PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), [Commercial Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), and founder charter #818. Praxxis/Grok retain creator asset and QA coordination through TASK-008; Claude owns production website and analytics; founder controls release and spending.
