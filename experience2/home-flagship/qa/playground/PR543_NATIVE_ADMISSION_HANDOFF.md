# PR543 private WordPress Playground bundle: native admission bridge

**Status: DRAFT / RELEASE HOLD.** This is an isolated adapter for the bundle layout created in PR #543, not a WordPress or production deployment.

## Verified integration mismatch

The source-controlled `launch_offline_bundle_stage.py` already in the stack is the separate PR #459 adapter. It expects `assembler.zip` and `media/{apollo,franklin,nypl}` at bundle root and requires the independently pinned original Blueprint. The PR #543 packager instead produces `assets/assembler.zip` and `assets/{apollo,franklin,nypl}`. Pointing PR #543's ZIP at the earlier adapter **cannot** complete staging. This is a real format mismatch, not an absent concept.

`launch_pr543_offline_stage.py` is an **explicit compatibility adapter for PR #543**, not a replacement for the PR #459 pathway. Before merging to the main project, choose one canonical bundle and launcher format and eliminate redundant maintenance paths.

## Exact behavior

- Only accepts a private, regular, unmodified, independently SHA-256-pinned ZIP and approved original-blueprint semantic fingerprint.
- Permits only the five deterministic ZIP members; rejects duplicates, unreviewed extra files, symlinks, wrong image bytes, substituted sources, altered WordPress PHP, bad manifest and theme.
- Reconstructs the original 19-step URL-resource Blueprint **in memory** and re-executes the inherited exact `package_offline_playground_bundle.seal` gates. The ZIP contents must match its deterministic reproduction byte for byte.
- For `--execute` only: calls the existing `launch_integrated_staging.run` against the verified local ZIP, inheriting loopback-only port checks, actual WordPress, Chromium/axe, actual media-byte admission, mobile/desktop lab Lighthouse and process cleanup.
- Does **not** create an image, import a production database, export subscribers, contact WordPress.com, change theme or navigation, merge a PR or publish the homepage.
- This lab is not identical to WordPress.com Atomic. Jetpack email delivery, host-specific cookies/redirects, field CWV and production release still require separate gates.

## Commands

From a reviewed, exact-SHA `experience2/home-flagship/qa/playground` checkout:

```bash
python3 -m unittest -v test_launch_pr543_offline_stage.py test_package_offline_playground_bundle.py

python3 launch_pr543_offline_stage.py \
  --bundle /private/fv/stage.zip \
  --bundle-sha256 <independently-reviewed-sha> \
  --original-source-sha256 <independently-reviewed-semantic-sha> \
  --theme-sha256 <independently-reviewed-theme-sha> \
  --media-manifest /private/fv/media-attestation.json \
  --axe-js /private/fv/axe.min.js --axe-sha256 <independently-reviewed-axe-sha> \
  --browser-runner /exact-checkout/verify_playground_browser.py \
  --browser-runner-sha256 <independently-reviewed-browser-runner-sha> \
  --private-dir /private/fv --output-dir /private/fv/qa
```

Add `--execute --playground-cli /reviewed/executable --playground-cli-sha256 <sha> --lighthouse-cli /reviewed/executable --lighthouse-cli-sha256 <sha>` **only after** installing/caching an independently reviewed, functional Playground runtime and providing all verified original media and Assembler files. Keep private files mode 0600 and parent workspace 0700. The original-source semantic SHA is obtained from the independently reviewed *original* 19-step URL-resource Blueprint (never derived from the candidate ZIP): `sha256(json.dumps(blueprint,sort_keys=True,separators=(',', ':'),ensure_ascii=False).encode('utf-8'))`.

## Evidence and limitations

Local Python 3.13 suite: **25/25 PASS** (13 new adversarial adapter tests and 12 inherited packager tests). Exact local Git blob hashes of the two new files matched the GitHub blobs when published. All images and theme content used by these tests are intentionally synthetic. Adapter tests use an imported launcher contract double, *not* the real WordPress launcher's runtime. This proves the bundle admission logic under tested fixtures; it does **not** prove the real `--execute` path succeeds.

**NOT DONE:** real official theme ZIP, original photo bytes and independently reviewed usage permissions, full exact-checkout native WordPress, axe, screen reader, 200% zoom, mobile Safari, Lighthouse/CWV, hosted Jetpack/WordPress parity, CI/QD, founder art-direction selection. No release approval or live edits.

WordPress official bundle contract: https://developer.wordpress.org/playground/blueprints/bundles/
