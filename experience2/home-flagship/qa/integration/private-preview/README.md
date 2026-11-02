# Experience 2.0 — private-source WordPress staging preview (v0.2)

**Status: DRAFT / NO INSTALLATION / RELEASE HOLD.** This is an additive replacement candidate for the earlier iframe preview in PR #212. Do not modify or activate the live finalvestige.com theme, homepage ID 6, Jetpack, Focus Fieldbook, 72 Hidden in the Margins items or frozen PR #49. WordPress Apollo PR #158 stays in its own component lane. Review under Issue #150.

## Why this sprint matters

The original PR #212 preview builder included `assets/index.html.txt`, CSS and JS beneath the WordPress plugin's web-accessible directory. The PHP iframe route was capability-gated, but `.txt`, `.css` and `.js` files are ordinarily retrievable directly from a public plugin URL on common Apache/Nginx installations. Renaming `.html` to `.txt` does **not** make the document private. This is a **release-stage source exposure risk**, not proof that anything leaked: the original preview has NOT been installed on the live site.

This replacement packages exact source bytes into only guarded `.php` files. A direct GET of `fv-ex2-private-payload.php` without WordPress's `ABSPATH` exits with HTTP 403 and no source content. It rejects missing, extra, corrupted or unexpected compiled source assets before rendering. All six stylesheets and four scripts are inlined into one authenticated response; no public JS/CSS URL is exposed. Each approved response gets a fresh script nonce. Crucially, **scripts are moved to the end of the document** rather than injected into `<head>`: HTML `defer` has no effect on inline scripts, and initializing before the DOM silently broke the art-direction control during the first local QA iteration. This regression is now covered by real Chromium assertions.

## Source / exact-parent and supported build

Stack on unmerged homepage **PR #217**, Git HEAD `c1c00acfa79664163214e1f424a8868e64aa2ee3`. The old PR #212, original homepage PR #49 (`10495883299d53596992c26a8987f629b2904670`), Mind Issue #171 and Apollo PR #158 were READ ONLY. No code overlaps with the separate Apollo WordPress staging plugin.

The builder imports the existing `qa/integration/check_contract.py` checks at runtime: names must match its `ASSETS` allowlist, the editorial/custody/no-JS contract must pass, and all files must actually exist in the checkout. A caller must supply the **40-character commit SHA** being packaged. That SHA is an **unattested input**, not a substitute for checking out the commit yourself.

From the repository checkout root, with the new folder in `experience2/home-flagship/qa/integration/private-preview/`:

```bash
cd experience2/home-flagship/qa/integration/private-preview
python build_private_preview.py \
  --root ../../.. \
  --contract-dir .. \
  --expected-head "$(git rev-parse HEAD)" \
  --out /tmp/fv-ex2-private-preview-HOLD.zip
php -l fv-ex2-private-preview.php
python -m unittest discover -s tests -v
python qa/verify_private_preview_browser.py
```

The ZIP is **not an installation instruction**. It includes only a PHP plugin, an executable/guarded PHP payload, a machine-readable source/hash manifest and an installation HOLD note; no directly readable source assets are packaged. The shortcode `[fv_ex2_homepage_preview_private]` and its single authenticated `wp_ajax_fv_ex2_private_render` endpoint are disabled on production and for unauthenticated/non-editor users. It requires both `WP_ENVIRONMENT_TYPE=staging` (or development/local) and `FV_EX2_ALLOW_PREVIEW === true`. No public `wp_ajax_nopriv` endpoint is registered.

**Do not activate on production.** An actual private WordPress staging installation still requires a separate founder decision, proper security review and release authorization. No email/affiliate/analytics/paid resources are added by this sprint.

## Test evidence and precise limitations

Executed locally against the existing representative seven-chapter HTML fixture (not the full canonical GitHub index):

- **9/9** Python tests: source build, private-only zip contents, hashes, direct PHP payload execution (no output), PHP lint, mutation/incomplete contract rejection, missing release SHA, no CMS writes.
- **62/62** separate real PHP HTTP + real Chromium checks: four denied authorization cases; bad nonce denied; direct payload URL returned 403/no content; tampered source returned 503/no content; response recovered on restoration; no public executable fetches; CSP nonce, noindex and no-store headers; five browser widths (320, 390, 768, 1440, 1920); visible art-direction controls; live mode switching; Chronicle comparison; sticky Reading Trail initialization; no-JS source case visibility.
- PHP built-in HTTP server served real assembled content and headers. Chromium **could not navigate localhost** (environment restriction), so the same verified response HTML was rendered via `page.set_content()`. That browser test **did not enforce the HTTP CSP**. Standalone HTTP header assertions did verify that a nonce-policy header is emitted. This is not full browser-on-hosted-HTTP assurance.
- Source read-back against exact GitHub parent confirmed its 6 expected `<link>` tags, 4 `<script defer>` tags and unpublished design-study markers match the transform's literal requirements. The latest index is **35,173 characters** in GitHub; fixture is only ~20,437 bytes. The code and test harness must run on the complete exact Git checkout before QD. No invented CWV, no claimed WCAG 2.2 AA.

Artifacts: `qa/HTTP_BROWSER_RESULTS.json` (aggregate assertions, no private URLs), `qa/private-preview-1440.png` and `qa/private-preview-390.png` (local fixture screenshots, **not production**). Screenshots remain founder-facing; the ZIP and screenshot binaries are not committed to GitHub.

## Security / editorial custody

- **Production fail closed**: explicit opt-in, named staging/development/local WP environment, logged-in user, `edit_pages`, nonce verification, no public Ajax hook.
- **Source fail closed**: exact asset keys only, SHA-256 per original byte, required unpublished marker, exactly one tag per CSS/JS, no remote executable references, no `</script>` injection, strict `base64_decode`, no caching.
- **Controlled response**: script nonce; CSP `default-src none`, no external JS, no form posts, no outbound connect, source-image domains restricted; `nosniff`, `noindex`, `no-referrer`; iframe sandbox. WordPress media links can still load only where licensed and permitted by policy.
- **External rights unchanged**: Royal Museums Greenwich and Canadian Museum of History Franklin notes are independently sourced; NASA media must not imply endorsement; NYPL 1903 map rights remain unresolved and must not be presented as a 1918 Malbone reconstruction. Observer Lab diagrams are original instructional illustration, not actual historical records or a validated psychological experiment.
- **Commercial firewall**: no Inspire3/ClickBank direct earning URL or unverified benefit; /focus/ and published Puységur files remain editorial pathways. If an earning link is approved in a future separate guide, put the FTC disclosure beside it.

## Remaining release blockers

1. **Actual WordPress staging** native theme/header/footer behavior is untested. The iframe is a staging reviewer tool, not a substitute for integrating WordPress-native blocks into public page ID 6.
2. Browser-on-HTTP CSP and real WordPress cookies/SameSite interactions, screen-reader and mobile Safari testing remain open.
3. Exact checkout full-page Playwright + source contract / `php -l` / independent QD / hosted CI required. GitHub Actions runner dispatch remains broken (Issue #75), branch rules not enforced (Issue #191).
4. Clear individual source-image reuse rights, test delivered WordPress srcsets, collect real staging Lighthouse plus production field p75 CWV (LCP/INP/CLS). No measurements claimed.
5. Select an art direction with the founder, obtain release approval, and preserve page ID 6 live content and 72 Margins entries. Nothing was merged, published or installed in this sprint.
