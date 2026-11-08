# EX2 — independent MU-plugin runtime isolation (review only)

**Status: built and tested in PHP CLI stubs; not WordPress-core integration. Release HOLD.**

## Concrete weakness
The canonical full-source review ZIP starts with a read-only WordPress Blueprint preflight that checks loopback before installing Assembler. Both separate MU-plugin files, however, only test the `fv_ex2_playground_review_only` option. If **either file is independently copied into a mapped WordPress site with that marker already set**, WordPress can register the preview shortcode and footer receipt. This is a *defense-in-depth gap*, not evidence of production compromise. Import preflight is still necessary and unchanged.

The new `make_loopback_guard_variant.py` refuses to operate unless the original local ZIP exactly matches SHA-256 `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`. It appends an independent early-return guard to BOTH PHP entrypoints, before each marker check. Each requires a WordPress home URL with a genuine loopback hostname (localhost, 127.0.0.1, ::1 or a subdomain ending **.localhost**), and refuses explicit `WP_ENVIRONMENT_TYPE=production`. It then retains the existing activation marker and per-page restrictions.

This is a **derived variant**. It does not rewrite the canonical Blueprint, the actual seven-chapter HTML/CSS/JS, the live WordPress page, or earlier protected source ZIPs. The variant rehashes both edited PHP files in its custody manifest and includes the original protected source hashes. The input/output are private artifacts, not deployable public pages.

## Measured before / after (actual PHP execution with WP-function stubs)

| Case | Before / canonical | After / derived variant |
|---|---|---|
| Real loopback + review marker | Registers preview shortcode and footer QA receipt | **Registers both; same original HTML/CSS/JS hashes** |
| `https://finalvestige.com/` + copied review marker | **Registers shortcode** (unsafe hypothetical) | **Registers nothing** |
| Loopback + explicit production environment | Would register with marker | **Registers nothing** |
| `https://localhost.evil.example/` | Would register with marker | **Registers nothing** |
| Missing marker | Registers nothing | Registers nothing |
| Wrong page on local host | Returns no shortcode markup, CSS or JS | Returns no shortcode markup, CSS or JS |

Local run: **13/13 Python regression methods PASS**, including multiple separate PHP invocations. PHP 8.4.24 CLI used. The original shortcode output is byte-identical in accepted local mode to the earlier bridge receipts:

- HTML SHA-256: `baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d` (50,938 bytes)
- CSS SHA-256: `152bfd327325997bee65191028501467292c70bc8573a39b439a5e6d49bc8afb` (71,883 bytes)
- JS SHA-256: `67230d93773a46fb2942368d5e13fb127788bf4504bb8ff106c317fd4af5b6ee` (15,273 bytes)
- Seven chapters, **72 Margins items**, **five original Focus destinations**, **two archival image elements** remain.

New derived private ZIP SHA-256: `dbc305c6047756665a2fd54ffb88ab4822b7b43dad370c575423a627fd4ce061`. The original Blueprint JSON SHA-256 is still `17a9ea5428f0c56a36ce376793d9b53521871dd0bc38a9f947d0ff49c91be4ca`.

## Reproduce without production

Obtain the original `blueprint_review.zip` from the **prior PR #1500 review-evidence ZIP** (not WordPress media or the production server). On an isolated machine with Python 3 and PHP CLI:

```bash
export FV_EX2_CANONICAL_ZIP="$PWD/blueprint_review.zip"
python -m unittest -v test_loopback_guard_variant.py
python make_loopback_guard_variant.py "$FV_EX2_CANONICAL_ZIP" --out "$PWD/fv-ex2-guarded-local-only.zip"
sha256sum fv-ex2-guarded-local-only.zip
```

If using a copy named `fv-ex2-local-cli-preflight-guarded.zip`, the test runner also accepts it next to the test script. The **source file is intentionally not duplicated into this PR** and should not be exposed through public WordPress file paths. This variant should be considered only for an explicitly isolated Playground deployment and must be re-admitted by all previous exact-source checks rather than silently replacing the protected canonical ZIP.

## Reproducible blockers / owner

- The connected site reports **only production blog ID 256784396, Assembler theme, WordPress 7.1.4, PHP 8.4.27, Personal plan**. It is not an authorized staging clone.
- This execution environment cannot resolve the Playground npm registry and Chromium navigation to `127.0.0.1` returned `ERR_BLOCKED_BY_ADMINISTRATOR`; therefore the guard was tested in *real PHP* with **stubbed WP callbacks**, not installed WordPress core or WordPress.com-hosted PHP. No host release gate is passed.
- Do not interpret unchanged HTML/CSS/JS hashes as genuine rendered-site pixel proof or as first-party image loading. Real Apollo/NASA #473 and Franklin #474 HTTP bytes, canonical Assembler, axe/manual WCAG 2.2 AA, keyboard/touch/no-JS, Lighthouse/CWV, authenticated Jetpack confirmation, independent conversion data, exact SHA CI/QD and founder visual/release approval remain open.
- The rights-pending NYPL #1258 image remains excluded; NASA no-endorsement and 1869 reproduction labels remain, unchanged.

**OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER:** Existing free 52-page Focus Fieldbook → evidence-led homepage → contextual CTA → Jetpack confirmed lead → verified paid order. One portable staging component could inadvertently activate outside the intended localhost while review is underway → independently guard both MU plugins on hostname/environment → 13 passing local PHP-stub tests, previous before/after registration witnessed, **no paid conversion evidence** → interim engineering / Site QA. Claude retains real Jetpack/commerce attribution; Grok/Praxxis retain social asset IDs and campaign handoff (#820, TASK-008).

**Governance:** Draft-only on an isolated PR; frozen PR #49, Apollo #158, Mind #171, Focus page and published homepage unchanged. No theme/plugin install, CMS writes, merge, deploy, social post, subscriber action, instrumentation or spending. The existing 7-chapter release gate stays HOLD.
