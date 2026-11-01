# Local Jetpack subscription boundary — source-grounded release gate

**Scope:** Experience 2.0 integrated seven-chapter WordPress Playground; draft review only. No production CMS writes, plugin installation, deployment, merge, change to frozen PR #49, or commercial link.

## Finding (November 1, 2026)
Authenticated, read-only WordPress `pages.get` for **published page ID 6**, modified 2026-10-30 09:14:14, returned 47,021 characters of raw Gutenberg and **exactly one** self-closing `<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->` block. It contains no saved form markup fallback. The same raw page retained 72 unique Margins `--i:` records and two original `/focus/` links.

The isolated 19-step WordPress Blueprint installs **Assembler** and only the **fv-ex2-playground** test plugin. It does **not install Jetpack or import subscribers**. Therefore preservation of the source marker is not proof that an interactive Jetpack signup is actually rendered, usable, or connected in a plain isolated WordPress instance. The previous browser acceptance checks recorded Margins/Focus but no independent Jetpack render or delivery result.

## Corrective integration (this branch)
Within the existing `render_block` callback, when `blockName === 'jetpack/subscriptions'`, `is_front_page()` and `fv_ex2_safe_stage()` are all true, return an accessible, noninteractive **local-only notice**: "Dispatch signup — hosted verification required." The notice has `data-fv-subscriptions-local-only="true"` for private visual QA. It includes no input, form, tracking pixel, JavaScript or merchant link, and explicitly states no addresses are collected.

The original Gutenberg Jetpack block is **not changed**; the notice is an isolated render-time overlay only. All other block types remain untouched; any non-local environment returns the existing block HTML unchanged. The existing seven-chapter source/media hash guard remains intact. Only one `render_block` callback is registered to avoid ordering surprises.

**Regression tests:** `node --test experience2/home-flagship/qa/playground/test_local_jetpack_boundary.cjs` executes the actual PHP callback in a minimal controlled PHP runtime and checks 8 positive/negative scenarios. PHP syntax lint is included. The tests are not a native WordPress execution or Jetpack delivery verification.

## Correct stage and hosted release interpretation
An isolated WordPress/Assembler preview may show this **explicitly nonfunctional** newsletter notice, and may pass separate visual/keyboard/evidence QA, but **Jetpack functional acceptance MUST remain NOT VERIFIED**. A later authorized hosted WordPress.com acceptance must prove the actual Jetpack block renders as a real usable form; successful subscription + email delivery must be tested only with explicit consent and a controlled test address, without importing, copying or exposing the site's existing subscribers or secrets. A placeholder alone must never satisfy that gate.

WordPress.com Personal does not support a native staging clone; do not misidentify `vestigefinal-tezws.wpcomstaging.com` as a second private staging instance or recommend upgrades automatically.

## Other independent blockers
Original Assembler theme bytes, independently reviewed Apollo/Franklin/NYPL originals and reproduction rights, native WP/Assembler render, actual browser image response SHA-256, complete 7-width mobile and 200% visual QA, manual/axe WCAG 2.2 AA, measured Lighthouse and field CWV, Jetpack hosted delivery, QD and exact-head CI remain open. All claimable staged results must distinguish source-only/PHP-mock from genuine WordPress runtime evidence.

**Release:** HOLD until founder explicitly approves a production release. Coordinate Apollo #158 and Mind #171 separately.