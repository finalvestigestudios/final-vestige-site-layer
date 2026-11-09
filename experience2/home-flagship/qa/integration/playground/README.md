# Final Vestige Experience 2 — local WordPress Playground admission (DRAFT / HOLD)

**Scope:** Close the staging feasibility gap for the existing **seven-chapter** Experience 2 candidate. This is **not a new homepage**, live CMS update, or authorized release. It extends the *sealed* PR #224 renderer on an **isolated, free local WordPress Playground CLI** environment, rather than creating the unsafe public static-asset preview used by PR #212. PR #49 remains frozen and untouched.

## Engineering evidence

The generator requires an exact 40-character Git HEAD and confirms `HEAD:<path>` blob identity for 11 flagship sources, the PR #224 builder and its PHP template. A dirty/missing/symlinked file or HEAD mismatch fails closed. It invokes **PR #224's existing builder** (no second renderer), verifies the output is precisely three ZIP members and that the sealed PHP payload hash matches the manifest. It places **only the PHP entrypoint**, no directly served unpublished HTML/CSS/JS, in a local plugin mount folder.

The generated Blueprint sets `WP_ENVIRONMENT_TYPE=local`, `FV_EX2_ALLOW_PREVIEW=true`, `DISALLOW_FILE_EDIT=true`, logs in the local reviewer, activates the sealed plugin and creates a **private**, uniquely named review page with `[fv_ex2_sealed_homepage_preview]`. Source links in the candidate may still point to public Final Vestige URLs; following those links exits the local review. Do not use the live site's credentials or subscriber records.

## Reproduce (only from a clean exact PR checkout)

```bash
# Run in the repository containing PR #224 and this companion branch.
HEAD_SHA="$(git rev-parse HEAD)"
python -I experience2/home-flagship/qa/integration/playground/make_local_playground.py \
  --repo "$PWD" --expected-head "$HEAD_SHA" \
  --out /tmp/fv-ex2-playground-admission
python -m unittest discover \
  -s experience2/home-flagship/qa/integration/playground \
  -p 'test_make_local_playground.py' -v

# Playground CLI is a free external download; it must be available on this machine.
# Run from a separate, empty, local working directory, not a production plugin directory.
mkdir -p /tmp/fv-ex2-playground-session
cd /tmp/fv-ex2-playground-session
npx @wp-playground/cli@latest server \
  --blueprint=/tmp/fv-ex2-playground-admission/blueprint.json \
  --mount=/tmp/fv-ex2-playground-admission/plugin/fv-ex2-sealed-staging-preview:/wordpress/wp-content/plugins/fv-ex2-sealed-staging-preview \
  --login --port=9400
```

Open the **local** `http://127.0.0.1:9400/wp-admin/` Pages screen, then use View for the private `FV EX2 LOCAL REVIEW — NOT LIVE` page. The sealed iframe should render only for a logged-in user with `edit_pages`, a nonce and `WP_ENVIRONMENT_TYPE=local`. If any of these fail, **fail closed**; do not relax the checks or install on finalvestige.com. A WordPress Playground CLI binary/version must be fetched before this process can launch, and this run **did not execute the CLI, install WordPress, or perform localhost HTTP acceptance**.

## Actual acceptance needed on the isolated local site

Record the exact Git checkout HEAD, sealed ZIP and Blueprint SHA-256, WordPress/PHP/Playground versions, active theme (Assembler may not be available or identical), editor-only access and a 403 for the unauthenticated AJAX renderer. Verify all seven chapters, first screen at 320/390/768/1440/1920, 200% zoom, reduced motion, keyboard/touch, and no-JavaScript source meaning. Run existing exact-source CSP/interaction checks from PR #252, `axe-core` fail-closed, Playwright full-page screenshots and honest local Lighthouse lab results. Measure all actual media requests, selected `currentSrc`, decoded images and transferred bytes; clearly mark CDN/network failures. Compare against the authenticated production Page 6 source, including all **72 Margins items**, Franklin source credits, and Focus/Jetpack preservation. The isolated candidate is **not** a byte-identical copy of the published WordPress home: it is an EX2 art-direction source fixture. Existing public Page 6 content remains the canonical released source.

**Unavailable certainties:** Playground uses a different runtime from WordPress.com Atomic, does not recreate Jetpack account state, cannot confirm email delivery or legitimate subscriptions, does not certify host-specific redirects/cookies, and cannot yield production field CWV or sales. No conversion analytics, affiliate claims, social publishing or live hosting changes are part of this package. The commercial release gate remains blocked by the Focus false-success repair (#1681), paired-dependency docket (#1726), independent CI/QD and the founder's explicit production approval.

## Test scope / local outcome

Eight stdlib Python tests against synthetic, temporary Git fixtures passed: clean-package generation, source HEAD mismatch, dirty file, symlink, unsafe output paths, malformed SHA, and Blueprint private/isolated contracts. These tests are **not** a WordPress runtime, accessibility or visual acceptance and do not prove the 11 actual candidate assets run inside Assembler. No frontend screenshot or measured Lighthouse result was produced in this run.

Docs: [WordPress Playground CLI](https://developer.wordpress.org/playground/developers/local-development/wp-playground-cli/), [Blueprint steps](https://developer.wordpress.org/playground/blueprints/steps/). This path avoids WordPress.com Business-plan staging costs; the user's Personal plan does not support one-click staging. No database, WXR, users, subscriber records or secrets are exported from production.
