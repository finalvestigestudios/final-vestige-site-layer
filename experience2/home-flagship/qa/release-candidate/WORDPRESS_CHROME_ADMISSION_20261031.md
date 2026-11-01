# WordPress Assembler global-chrome integration — exact-source custody

**Draft only / release HOLD** (2026-10-31). Parent is PR #368 HEAD `9692321700753506ca433b8d956272bd6878bd3e`. No production write, staging install, merge, new visual direction, affiliate URL or change to frozen PR #49.

## Concrete defect reproduced

The PR #368 WordPress content-only fragment still embedded a `<header class="fv-hf__masthead">` containing a **second Final Vestige site logo, primary Investigations/Public Record/Library navigation and global Focus button**, and `<footer class="fv-hf__footer">` containing a second branded site footer. WordPress site ID **256784396** reports active theme **Assembler**, homepage ID **6** uses the default template (empty custom-template value), and the read-only Assembler `page` template source includes both `wp:template-part {"slug":"header","theme":"assembler"}` and `wp:template-part {"slug":"footer","theme":"assembler"}` around `wp:post-content`. Embedding additional site chrome in content risks duplicate navigation, landmarks, brand marks and screen-reader verbosity. This is a **source/templating contract defect**, not a claim that the unpublished fragment was rendered on production.

## Narrow correction

`build_release_review.cjs` now strips only the existing flagship's global masthead from the **WordPress fragment**, leaving the chapter navigation intact. It converts the fragment's branded `footer` into a plain editorial disclosure band, retaining its direct **Affiliate Disclosure** link and existing scoped CSS hook. The standalone complete-page reviewer HTML keeps its original masthead, navigation and footer; the original three-direction source study remains untouched. Bounds are structural and fail closed if header/footer or disclosure contents drift. The original first-party ten asset SHA pins remain unchanged.

## Exact-source evidence (2026-10-31)

- Source `experience2/home-flagship/index.html` Git blob `70ebe0d8e122048343c99a3c6adc6f7ac498ed7f`.
- Previous builder blob `38941318c0f48d30d8020a5964c7201018a51c06`.
- Updated builder blob `c963b9da14e0d7ed7e5d5e7faccfbbb7af8af97f`.
- Updated Node regression suite blob `b20cbcb6bc71c9c4a7bc5280633866fae19c2534`.
- Actual fetched builder evaluated against actual fetched pinned homepage source in V8: **22/22 structural/invariant and negative-control assertions passed**, including 4 mutated source files that must fail closed. Original fragment 35,668 characters; corrected fragment 34,727 characters (**941 fewer**). Source-grounded before: duplicate global masthead/footer/primary navigation existed. After: all removed from WP fragment; all seven chapter anchors, three Apollo/Franklin/Malbone cases/buttons, chapter navigation, at least two /focus/ links and direct editorial disclosure retained. Standalone document still has one main landmark and its original masthead/footer.
- Committed regression tests extend `test_release_review.cjs` with masthead/footer/dedup/disclosure assertions and 3 new intentional negative controls. **The Node test runner and actual WordPress/Assembler staging have NOT been executed in a full local checkout; only exact-source V8 assertions were executed.** 
- WordPress ID 6 read-only: 72 Margins items, 2 Focus routes and the existing Jetpack subscriptions block still present; `FV Focus Popup` v0.1.1 active but no shortcode on page 6. No CMS changes occurred.

## Admission gates still open

1. Full exact-Git checkout: `node --test experience2/home-flagship/qa/release-candidate/test_release_review.cjs` then `node experience2/home-flagship/qa/release-candidate/build_release_review.cjs --out-dir <private-new-dir>`. Only consume the bundle if SHA checks pass.
2. Test content fragment with the actual Assembler template in isolated local WordPress Playground or localhost, using **public content only**; no production users, subscribers, secrets or database. Confirm exactly one theme header/nav/footer and one main landmark.
3. Compare full screenshots 320/360/390/768/1024/1440/1920 and 200% zoom. Verify overflow, evidence first screen, disabled-JS source visibility, keyboard/touch, reduced motion, forced colors, four interactive components and CSP three negative controls. **Axe fail closed** if unavailable; Lighthouse measured only when executed.
4. Actual first-party media HTTP transfers and decoded dimensions/bytes, NASA/Franklin/NYPL **exact displayed derivative rights**, external image availability; independent QD, CI green exact SHA, founder-selected final art direction and specific deployment approval.
5. WP.com Personal does not provide the native staging clone. Isolated Playground is not WordPress.com Atomic host-parity certification.

Nothing was installed, merged or published. **Release remains HOLD.**
