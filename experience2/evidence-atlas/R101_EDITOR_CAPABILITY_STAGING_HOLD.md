# Apollo R101 — editor-level private-preview boundary (STAGING HOLD)

**Issue:** #150. **Parent:** R100 draft PR #840, exact parent commit `7c9ad6b5b3e7536b5822e9414ec21193957bc90c`. **Scope:** Apollo source review only. All evidence remains unreleased.

## Reproduced defect from reviewed source

The R99 WordPress private-review guard checked `current_user_can('edit_posts')`. In unmodified WordPress roles, **Contributors and Authors have `edit_posts`**, although neither is necessarily entitled to inspect an unreleased NASA research workspace. R100's genuine WordPress acceptance verified anonymous and Subscriber denial but **did not exercise Author or Contributor**. The earlier "editor-only" narrative therefore overstated the enforced access boundary.

## Remediation

- Replace the preview guard with `current_user_can('edit_others_posts')`, ordinarily held by **Editor** and **Administrator**, rather than relying on login state or `edit_posts`. This is a WordPress *capability* boundary, not a hard-coded role name; customized roles with this capability are also authorized by design.
- Apply the same boundary to both the privileged `template_redirect` resource endpoint and `[fv_apollo_r99_review]` iframe/shortcut access (both share the guard). The plugin still defaults to disabled unless `FV_APOLLO_R99_PRIVATE_PREVIEW === true` on an isolated installation.
- Update the PHP contract shim, Python negative regression, and **genuine disposable WordPress** E2E. The real WP test provisions Contributor, Author, Editor, Subscriber and Administrator and verifies that Subscriber, Author and Contributor cannot retrieve unapproved HTML/JSON/CSS, while Editor and Administrator can reach reviewed routes.
- Validate `do_shortcode('[fv_apollo_r99_review]')` under real WordPress roles without inserting or publishing any post: Editor receives the reviewed private iframe; Author receives the public-investigation fallback.

All R92→R99 source identities, NASA destinations, zero embedded images, no geographic pins, full source SHA-256 pinning, print rights warnings, keyboard/touch, 320–1920px, JS/no-JS, axe, and local LCP/CLS checks are inherited unchanged.

## Reproducible acceptance

The existing `.github/workflows/ex2-apollo-r100-actual-wordpress.yml` now triggers when this guard or its tests change, and rebuilds the sealed R99 preview package twice, byte-compares both archives, lints generated PHP, executes the R99 Python regression suite and genuine WordPress Chromium acceptance. The R99 PHP-contract workflow also triggers on the changed template and contract fixture.

**Acceptance remains pending until both workflows pass at the exact final R101 head**. Failed/not-started jobs must be reported as such, not called passing. Exact SHAs, run links, and any red tests should be recorded on Issue #150.

## Release decision — HOLD

No live page, CMS setting, media library, plugin, navigation, homepage PR #49, homepage lead branch, original Research Desk PR #158, or production deployment has been changed. Tests use a disposable, loopback-only local WordPress instance in GitHub Actions. This sprint does **not** establish hosted WordPress.com or Assembler compatibility. Six photograph-specific NASA reuse reviews and the provisional `S67-19766` association remain open. Manual assistive-technology, physical-device and independent editorial QA, production CWV and explicit founder approval remain required. No invented geo pins, relationship edges or archival photographs.
