# FV Experience 2.0 — actual PHP hook/shortcode execution, isolated acceptance
**Review-only, 2026-11-07. Release: HOLD.** Parent PR #1477 exact commit `9da9d473ffde09e666ce4bc00214ddd59d4a64a7`. Frozen PR #49 not modified. No live CMS write, network beacon, test subscriber, analytics activation, affiliate link, merge, or deployment.

## Why this is a separate lift
Prior #1469/#1477 tests evaluated full protected homepage HTML/CSS/JS extracted from a WordPress Playground package. This run additionally **executed the actual MU-plugin with PHP 8.4 CLI**, invoked its registered `wp_enqueue_scripts` callback and `fv_ex2_playground` shortcode under controlled stubs, and inspected the emitted assets and HTML. This is a stronger code-path check than merely parsing a PHP heredoc. **It is not an actual WordPress or Assembler runtime.** The correct release gate is still a real isolated WordPress execution with its actual theme.

## Source custody and reproduction
Source artifact: `fv-ex2-local-cli-preflight-guarded.zip` inside the private QA evidence for PR #1469; SHA-256 `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`. Plugin path `mu-plugins/fv-ex2-playground-review.php`; SHA-256 `91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04`. The test rejects any other plugin hash before executing it.

Extract the private ZIP **locally**. Run `php tests/ex2/verify_ex2_php_hooks.php /path/to/fv-ex2-playground-review.php valid`, then substitute `wrong_page` and `flag_off`. The script is a CLI-only stub, not a WordPress plugin. It must not be uploaded to public WordPress. Do not commit the private ZIP, emitted page, subscribers or production database.

## Locally executed evidence
- Actual PHP syntax and plugin callbacks: `valid` **PASS**. Emitted 50,938 HTML, 71,883 CSS and 15,273 JavaScript bytes; source SHA verified. Emitted SHA-256: HTML `baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d`, CSS `152bfd327325997bee65191028501467292c70bc8573a39b439a5e6d49bc8afb`, JS `67230d93773a46fb2942368d5e13fb127788bf4504bb8ff106c317fd4af5b6ee`.
- `wrong_page` **PASS**: shortcode emits empty string; no assets enqueued.
- `flag_off` **PASS**: installation sentinel prevents callback/shortcode registration.
- Source-mutation negative control **PASS**: altered plugin rejected with exit 3. Unknown scenario rejected with exit 3.
- Emitted content preserves **seven chapter navigation links**, **72 Margins notes**, **five Focus links**, **two first-party archival `<img>` elements**.
- Separate local Python/Chromium runner executed PHP-emitted HTML/CSS/JS at widths **320, 390, 768, 1440, 1920**, both JavaScript enabled and disabled: **10/10 PASS**, no document overflow, no uncaught JS exceptions. Unexpected remote requests blocked, so image-transfer success is **not** claimed.
- Visually compared PHP-emitted first-screen Chromium renders at 390 and 1440 against PR #1469's previously source-extracted renders: after cropping the earlier 900px viewport capture to the same 850px height, **pixel-for-pixel identical** at both widths (0 unequal pixels; RGB RMS 0.0). This establishes parity between two *offline* rendering paths, not hosted parity.

## Evidence and owner decision
**OFFER → FUNNEL:** Historic investigations → contextual free 52-page Focus Fieldbook → legitimate confirmed Jetpack subscriber → independent verified paid order or affiliate conversion → net revenue. **BLOCKER:** PHP path had not been executed and native WordPress/Jetpack acceptance remains unavailable. **CHANGE:** fail-closed PHP callback/shortcode and guard checks, plus downstream offline Chromium evidence. **PASS:** tests above. **FAIL/OPEN:** actual isolated WordPress with Assembler theme, real image HTTP bytes, real browser Jetpack form verification (without creating test subscribers), axe WCAG 2.2 AA qualification, Lighthouse/CWV, founder visual acceptance, QD/CI exact SHA, confirmed commercial transactions. **OWNERS:** Interim homepage engineer/Site QA for integration evidence; Claude for live Jetpack/attribution; Grok/Praxxis for campaign acquisition. No purchases or signup conversions were asserted.

WordPress.com Personal provides no native staging clone; do not ask for a non-existent staging button or use production as a surrogate. Free isolated Playground/Docker remains the staging path when dependencies are available. This suite makes no changes to any production theme, page, navigation, settings, or content, including the seven-chapter flagship, Focus signup, and 72 Margins entries. Maintain source/rights distinction: NASA Apollo media #473, Franklin later reproduction #474; NYPL #1258 remains excluded pending editorial clearance. Media lengths observed in WordPress metadata only, not network-transfer confirmation.
