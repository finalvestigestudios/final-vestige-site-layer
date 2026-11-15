# R375 · Apollo 1 governed WordPress staging loader (not activated)

**Scope:** the existing source-sealed R372 Evidence Path, its R365 chronology record, R367 sequence gate, R371 NASA document catalog, and bounded R372 stylesheet detection. This is a source-controlled **candidate for independent installed WordPress/Assembler QA**, not a public plugin release or WordPress write.

## What was fixed

R365's original module adds `fv_apollo_r365_enqueue` to **every page** on `wp_enqueue_scripts` (priority 20) when included. An integration that naïvely loads all dependencies could quietly add CSS on unrelated pages. R375 checks six exact upstream files before inclusion, requires an *explicit* approved staging hostname and WP environment, and removes only that legacy unconditional callback. R372's pre-head, shortcode-aware stylesheet is left intact. If any precondition fails, the shortcode returns only the free investigation link, without a potentially mislabeled NASA claim or exposed source citation. No JavaScript or licensed archival photography is required.

## Isolated staging acceptance protocol

An authorized staging operator **may** include `experience2/apollo-r375/staging-gate.php` via an already-approved staging-only loader, preserving all sibling `experience2/apollo-rXXX` directories and exact bytes. Explicitly define both `FV_APOLLO_R375_STAGING_ENABLED` as PHP boolean `true` and `FV_APOLLO_R375_APPROVED_HOST` as the literal HTTPS staging hostname (no wildcards). WordPress must report `wp_get_environment_type() === 'staging'`; production hosts are refused. Do not install on a live domain. Shortcode is **`[fv_apollo_source_path_r372]`** on a *nonpublic, authorized staging test post*. No WordPress post, settings, plugin activation or DNS is written by this code. The upstream components register their other shortcodes but this loader only promises styling/QA for R372 path; do not use the other shortcodes through this gate.

For an installed staging acceptance run, execute the R374 guarded HTTPS acceptance runner with a verified, pinned *genuine* axe-core distribution. Confirm exact first-party CSS HTTP bytes, CSP, four source-custody joins, no external trackers, real installed WP/Assembler, keyboard/touch/no-JS, 320–1920, 400% text, print destinations, browser LCP/CLS, and independent screen-reader review. **Unit stubs and local Chromium fixtures do not satisfy these gates.** If the staging host is unavailable, leave release on HARD HOLD rather than substituting production. Do not merge PR #49 or modify #158.

## Local tests

```sh
php -l experience2/apollo-r375/staging-gate.php
python3 experience2/apollo-r375/qa/run_tests.py --out /tmp/apollo-r375-qa
```

`run_tests.py` uses real PHP stubs, actually loads all unchanged upstream PHP dependencies on a mock staging WordPress lifecycle, verifies no global CSS pollution and runs local Chromium with original R372 stylesheet injected from reviewed bytes (never an installed WordPress claim). It also checks adversarial dependency corruption and no-JavaScript interactions. No external network, emails, media, merchant operations or tracking.

## Commercial gate / provenance

Audience: history and social-studies educators. **One proposed pathway:** approved Grok Apollo long-form asset → evidence-stage source trail → [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → future rights-cleared educator kit **only after** payable SKU, fulfillment, licensing and merchant success are actually verified. The only deployed-experience CTA proposed here remains the free investigation link. NASA's Apollo 204 Board report is primary evidence; the 2018 NASA retrospective material and 2022 historical page are not original 1967 eyewitness documents. Linking does not grant commercial reuse rights, license media or imply NASA endorsement. No pins or map edges are asserted.

**Measurement if approved later:** unique Grok asset ID and utm_campaign → qualified human landing session → relevant CTA → independently confirmed lead, if used → verified paid order → fees/refunds → net revenue / 1000 qualified sessions, with 7/30-day cohort and tiny-sample flags. No merchant conversions or revenues are represented by this code. Founder/QD release authority, Claude's production ownership and Praxxis/Grok distribution ownership remain unchanged.
