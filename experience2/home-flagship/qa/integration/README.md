# Experience 2.0 — Full-home integration and WordPress staging gate

**Status: UNPUBLISHED / HOLD. This is not a release authorization.** This deliberately consolidates testing across the formerly isolated hero, Franklin chronology and lens, Apollo/Franklin/Malbone source plates, Source Inquiry, Observer Lab, and Mind/Focus bridge. It is a release-readiness sprint, **not another speculative homepage ornament**.

**Precise parent:** homepage PR #205, `78a1002026de05688db2024ed9b3732f7bdc4367`, stacked on #199 → #192 → #184 → #177. Release candidate PR #49, `10495883299d53596992c26a8987f629b2904670`, is frozen and is never changed by this project. Apollo Research Desk PR #158 is a separate lane; no plugin/shortcode conflict is introduced. Track Issue #150 and companion Mind Issue #171.

## What has changed from earlier component-by-component QA

**Before:** five isolated standalone HTML/CSS/JS chapter demonstrations had individually recorded browser evidence, but no shared, source-controlled test that exercises all of them on one actual `index.html`. A proof-of-concept page is not evidence of integrated WordPress compatibility, accessibility, or performance.

**After:** `check_contract.py` rejects missing/new third-party executable assets, broken chapter anchors, duplicate IDs, missing case controls, altered art-direction controls, absent Observer Lab or chronological comparison modes, orphaned editorial routes, unsupported affiliate checkout paths, unbounded images, and missing authentic source links. `verify_full_browser.py` runs full-page Chromium interactions across eight widths, switching cases, chapter lens, observer frames, art direction, native disclosures, full-page screenshots, no-JS, reduced motion, 200% CSS zoom, script errors, and the offline remote-media fallback. A build script makes an explicitly gated private WordPress preview plugin ZIP with SHA-256 hashes of every included source byte. The WordPress preview is inside a sandboxed iframe; **it does not install a new theme, replace a live page, create duplicate navigation or certify final native WordPress integration**.

### Exact execution against a real Git checkout

From the repository root, with Chromium, Python and Playwright installed:

```bash
python -m unittest discover -s experience2/home-flagship/tests -v
python experience2/home-flagship/qa/integration/check_contract.py --root experience2/home-flagship --report /tmp/ex2-contract.json
python experience2/home-flagship/qa/integration/verify_full_browser.py --root experience2/home-flagship --out /tmp/ex2-full-browser --chromium /usr/bin/chromium
php -l experience2/home-flagship/qa/integration/fv-ex2-preview.php
python experience2/home-flagship/qa/integration/build_staging_zip.py --root experience2/home-flagship --out /tmp/fv-ex2-staging.zip --expected-head "$(git rev-parse HEAD)"
```

The browser harness *inlines the exact checked-out CSS/JS into a throwaway document* because the current isolated Chromium environment blocks `file://` navigation; original source bytes are not rewritten. This validates rendered behavior together, **but not hosted HTTP asset paths, real-image delivery, WordPress theme/canonical URL, network requests or a real visitor's CWV**.

### Actual sprint testing boundaries

A **representative composite local fixture** using existing original chapter snippets (not the GitHub canonical index) passed 21/21 source contract checks and 179/179 integrated Chromium assertions at eight sizes, including JavaScript-off, keyboard, CSS zoom, and offline media failures. Ten Python unit/mutation/PHP-simulation tests also passed; `php -l` succeeded. These validate the QA tools, not the current PR #205 combined page. Separately, 19/19 structural source checks were executed by independently fetching every canonical GitHub source from exact parent SHA and reading live WordPress page ID 6. **Do not convert those checks into a claim of full-page visual QA on PR #205.** Any PR update requires re-running full browser checks at its new exact head.

The representative fixture is intentionally NOT committed or deployed, so it cannot be mistaken for an approved visual. Its screenshot samples and test receipts are founder-facing QA package artifacts.

### Staging-only WordPress preview — intentionally fail closed

`fv-ex2-preview.php` registers `[fv_ex2_homepage_preview]` and one **authenticated** `wp_ajax_` action; it does **not** register public `nopriv` Ajax. Requires all of: the WordPress environment is `staging`, `development` or `local`; the site operator explicitly defines `FV_EX2_ALLOW_PREVIEW` `true` in staging `wp-config.php`; the visitor is signed in and has `edit_pages`. Anonymous viewers and actual production environments receive no preview markup. The endpoint checks a nonce, sets noindex/non-cache and restrictive CSP headers, and serves the versioned HTML only to approved reviewers. The HTML ships inside the plugin as `index.html.txt` rather than an anonymously accessible `.html` file; CSS and JS are static local assets.

The preview iframe is intentionally sandboxed, so reviewers can see the source-controlled complete page without overwriting Assembler theme/header/footer or the live homepage. **Only install after separate founder staging authorization**; the script itself neither uploads to WordPress nor activates the plugin. In particular, do not install the ZIP on the production domain, and do not insert the shortcode into public page ID 6.

### Source custody and release-specific blockers

1. **Franklin Victory Point:** narrative and original editorial typesetting point to [Royal Museums Greenwich](https://www.rmg.co.uk/collections/objects/rmgc-object-504898) and [Canadian Museum of History](https://www.historymuseum.ca/blog/a-very-special-piece-of-paper). Original document wording is not manufactured. The museum description and transcription differ on April 25/26 cataloguing; keep “April 1848”. Scan originates from Wikimedia Commons public-domain marked source, but recheck scanned-file provenance before commercial distribution. No new museum scan binary has been introduced.
2. **Apollo 1:** NASA original source and Apollo 204 Review Board remain separate. Crew photo is evidence of personnel, **not** proof of the first spark or hatch mechanism. NASA permits many informational uses but prohibits implied endorsement of affiliate products; preserve credit and original-context boundaries. Review [NASA Brand Center](https://www.nasa.gov/nasa-brand-center/) and [official image/media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) before publication.
3. **Malbone Street:** NYPL 1903 map cannot be passed off as a spatial reconstruction of the temporary 1918 curve. The exact NYPL item reuse rights remain unresolved; its official catalog record [here](https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0) still needs rights confirmation. The 5,553,669-byte WordPress original has responsive CDN srcset widths 768, 1024, 1536 in the prototype; **real transfer bytes still not measured**. See [NYPL rights policy](https://www.nypl.org/research/rights-and-permissions).
4. **Observer Lab:** original CSS-created specimen illustrations, **not** historical artifacts or claims of diagnostic/scientific testing. DOI links are research context, not evidence that this demo reproduces experimental protocols.
5. **Commercial firewall:** hero/evidence gallery remains historic and unsponsored. The only Mind bridge points to published Puységur files and the **52-page free Focus Fieldbook**. No direct Inspire3 earning links, invented outcomes or extra signup form on this prototype. Later affiliate pages require separate consent, near-link FTC disclosures and source review.

### Mandatory release gates — still HOLD

- Founder approves art direction, visuals and WordPress-native integration scope; main proposed direction Black Dossier is **not founder-selected**.
- Independent full-page actual WordPress staging/browser screenshots at 320/360/390/768/1024/1440/1920, no-JS, keyboard, mobile touch, zoom, reduced-motion, screen reader (NVDA/VoiceOver), axe audit, real source media loading, licensing.
- Synthetic Chromium lab timings are **not** p75 CWV. Measure live/staging LCP/INP/CLS via appropriate Lighthouse and then production field data, targeting good thresholds; do not assert numbers that have not been measured.
- GitHub Actions hosted CI must run and pass against exact current candidate head. The cross-repo runner dispatch incident persists (Issue #75). Branch protection/required checks missing (Issue #191). No “CI pass” or “QD PASS” marker may be invented or substituted.
- Publication to `finalvestige.com` page ID 6, production theme/navigation, Jetpack subscriber flow, and all 72 Hidden in the Margins items require separate explicit approval and independent safeguards. **No merge/deploy/CMS changes performed.**

### Preservation observed in read-only WordPress snapshot, October 30

Published page ID 6 remains modified `2026-10-30T09:14:14`, carries all **72 unique** Hidden in the Margins item indices 0…71 and continues linking the Focus Fieldbook and Jetpack subscriptions. PR #49 exact head still `10495883299d53596992c26a8987f629b2904670`. The draft prototype itself does not and must not attempt to recreate or replace this existing production page.
