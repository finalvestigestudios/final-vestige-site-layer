# Apollo R403 — rendered CSS custody (DRAFT / HARD HOLD)

**Scope:** source-controlled isolated Experience 2.0 staging QA enhancement based only on R402 PR #2720 (HEAD `67cf29e5acfaeefb423c8caa73fa1309faa7ad0e`). No edits to frozen homepage PR #49, Research Desk PR #158, WordPress, site configuration, Grok/Praxxis TASK-008 or Claude analytics/commerce.

## Reproduced risk and correction

R400 verified the correct SHA-256 bytes had been fetched for two Apollo gallery CSS assets, while R401/R402 checked semantic custody, chronology, accessibility structure, network admission, headers and genuine-axe requirements. **Bytes fetched do not prove bytes actually applied**: blocked CSS, `media=print` on screen, late-theme overrides or broken responsive breakpoints can render a misleading or inaccessible experience even if HTTP byte-level proof succeeds. R403 adds an independent, read-only Playwright **computed style and layout geometry** gate in every acceptance context, verifying gallery background, evidence grid, chronology, publication index, evidence-rights boundary, CTA minimum height, responsive column geometry and horizontal overflow. It returns stable defect codes, never a release authorization.

`qa/css_effect_custody.py` injects its page inspector only in the current Python process before calling the existing R401+R402 staging acceptance; it restores the parent inspector even on exceptions. `inspect_receipt` requires all seven expected contexts. No CSS, JavaScript, trackers or markup are added to the site; only offline fixture acceptance tests add adversarial styles for verification.

## Executed, reproducible evidence

- `FV_APOLLO_OFFLINE_FIXTURE=/path/to/source-generated-apollo-fixture.html FV_APOLLO_MOBILE_CSS=/path/to/reviewed-mobile-fit.css python -m unittest discover -s experience2/apollo-r403/qa -p 'test_*.py' -v`
- 8/8 unittest methods PASS on actual Chromium, including **two disabled/overridden CSS attacks, a forced wrong mobile grid, real no-JavaScript/reduced-motion contexts, 320–1920px and 320px/400% root-font stress**. The prior bytes-only gate would not check applied styles in these three adversarial cases.
- Eight local browser fixture screenshot contexts (320, 390 touch, 768, 1440, 1920, 320 no-JS, 390 reduced motion and 320 with 400% root text) observed **0px horizontal overflow**. These are offline fixture screenshots, not installed staging.
- LCP/CLS unavailable in this environment's `set_content` navigation-only restriction; recorded as `null`, **not** zero. Genuine axe-core was **not run**. No native 400% browser zoom or independent screen-reader QA occurred.
- Screenshot ZIP is deterministic and SHA-256 manifest-backed. Tests use the earlier R393 local generated HTML fixture and the reviewed R395 mobile-fit stylesheet; verify genuine source checksums in `QA/browser-measurements.json`.

## NASA provenance, scope and conversion

Keep the 1967 [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) separate from the [Feb. 14, 2018 NASA post-fire flammability retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/). The former states no single original ignition source was conclusively identified; 102 deliberate Command Module tests in the latter occurred after the accident. The gallery has no NASA photographs, logos, imagined geospatial pins or sponsor affiliation. Follow [NASA media-use guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) and no-endorsement rules; no new licensed media introduced.

**One proposed path, not live:** Grok-owned, independently reviewed Apollo long-form asset (asset_id and permitted UTM still unknown) → source-backed Apollo evidence gallery → exactly one existing [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) CTA → future educator dossier *only* after rights-clearance, actual merchant SKU, checkout, fulfillment and founder approval. Mini Museum remains a distinct potential affiliate program, not inserted into the Apollo narrative. No visitor attribution, confirmed leads/orders, merchant refunds/fees or net revenue/1k qualified sessions is verified. No additional pixels or measurement scripts.

**RELEASE: HARD HOLD.** Exact checkout/CI of the new PR and parents, installed WordPress/Assembler staging, delivered CSS+CSP, genuine pinned axe-core, native zoom, screen readers, QD review, founder approval remain outstanding. Coordinate [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). No merge, deploy, WordPress write, affiliate activation, tracking install, email, social post or spending.

### Deterministic archive recipe

Run `python experience2/apollo-r403/qa/package_evidence.py` after executing the local Chromium fixture suite and capturing screenshots under `QA/`. The script refuses a false staging/release status, hashes every included source and screenshot, writes `QA/MANIFEST.json`, builds the ZIP twice with fixed timestamps and file permissions, and verifies byte identity. To regenerate screenshots, run a local source-created R384 fixture with reviewed R395 CSS prepaint and use Playwright `set_content` in the seven R400 contexts plus 320px 400%-root-font stress. Locally collected `QA/browser-measurements.json` identifies its source fixture hashes. The ZIP is a *local artifact*, not an exact-head hosted CI result.
