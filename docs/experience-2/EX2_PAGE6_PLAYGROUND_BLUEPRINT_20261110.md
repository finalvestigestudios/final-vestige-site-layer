# Final Vestige EX2 — Private WordPress Playground Page 6 Integration Admission

**REVIEW ONLY / RELEASE HOLD — 2026-11-10.** Companion to draft PR #1860 and Issue #150. Frozen PR #49, production WordPress page ID 6, theme/navigation/settings, and Grok/Claude lanes stay unchanged.

## Why this exists
PR #1860 established a scoped one-block Gutenberg replacement for the existing seven-chapter flagship rather than replacing the entire published homepage. Its offline HTML and Chromium fixtures are NOT actual WordPress/Gutenberg acceptance. This independent helper produces a deterministic LOCAL Playground Blueprint bundle from the exact source-controlled candidate and a separately captured, **public-only** Page 6 Gutenberg edit-content file. It allows a future reviewer to test the **integrated page**, not merely a standalone sealed preview plugin.

Actual read-only production context on November 10: site 256784396, active theme Assembler; Page 6 modified 2026-11-05T12:07:24, five Custom HTML blocks, one group and serialized native Jetpack subscription block, 72 `fv-margin-strip__item` records, original Focus CTA outside the replaced flagship. The existing seven chapters are already in the SECOND custom HTML block. NO production write or private export was performed.

## Build contract and source custody
`tools/experience-2/build_page6_playground_bundle.py` invokes PR #1860's existing `compose_page6_flagship.py`, rechecks the COMPLETE expected Git HEAD plus pinned blob hashes for 11 archive assets and the composer, and refuses drift, symlinks, output within a repo/WordPress webroot, preexisting destination, unsafe page hash, missing Jetpack/72 Margins/Focus, or synthetic fixtures presented as real content.

The ZIP contains five files: `blueprint.json`, `blueprint.local-cli.json`, `page6-review.blocks.html`, `MANIFEST.json`, and `DO_NOT_DEPLOY.txt`. `blueprint.json` refers to a bundled asset for a private web Playground bundle, while `blueprint.local-cli.json` inlines the SAME exact source bytes to avoid incorrectly assuming a standalone CLI Blueprint can resolve a ZIP's bundled path. Both use an isolated LOCAL WordPress environment, `DISALLOW_FILE_EDIT`, a `/tmp/` write, real WordPress `parse_blocks()`, hash guards, and `wp_insert_post` of a new **private** page `fv-ex2-integrated-review`. The PHP fails closed if not local, checks exactly one serialized Jetpack block and all 72 Margins, and verifies stored Gutenberg bytes. Nothing edits the actual WordPress.com site. A LOCAL WordPress page insert is intentionally part of an isolated test; it must NOT be run against production.

## Generate only from a clean exact checkout

```bash
git rev-parse HEAD    # compare with target PR's exact 40-char HEAD
sha256sum /private/public-page6.blocks.html
python -I tools/experience-2/build_page6_playground_bundle.py \
  --repo "$PWD" --source-dir "$PWD/experience2/home-flagship" \
  --page6-raw /private/public-page6.blocks.html \
  --expected-head "$(git rev-parse HEAD)" \
  --expected-page-sha256 "<fresh actual SHA-256>" \
  --out /private/fv-ex2-page6-review.zip
python -m unittest discover -s tests/experience-2 -p test_page6_playground_bundle.py -v
```

A marked synthetic fixture may be used ONLY with `--synthetic-fixture` for non-historical test demonstration. Do not confuse its passing tests with actual WordPress/Assembler or page content acceptance.

### Private local-CLI test, no paid subscription
Unzip the real public-only Page 6 bundle into a **private folder on an isolated developer machine**, then run the free WordPress Playground CLI from a fresh, nonproduction directory:

```bash
mkdir -p /tmp/fv-ex2-local-session
cd /tmp/fv-ex2-local-session
npx @wp-playground/cli@latest server \
  --blueprint=/private/unzipped/blueprint.local-cli.json --port=9400
```

In this isolated LOCAL Playground, visit `/wp-admin/` and inspect the **private** `FV EX2 ISOLATED REVIEW` page. Do not upload a real Page 6 bundle to public GitHub, a public Drive folder, or a public web server. Browser Playground via `blueprint-url` requires public URL access and is **not** appropriate for the actual page source. Never export subscriber data, credentials, production database, secrets, or WordPress users. User-facing WordPress.com production retains its own account state.

## Tested here, strictly scoped
The builder and its companion `test_page6_playground_bundle.py` passed **12/12 LOCAL synthetic Python regression cases** against a synthetic Git fixture; the test also executes generated PHP through locally installed PHP using MOCK WordPress APIs and rejects the simulated production environment. This is genuinely tested **builder logic**, not genuine WordPress runtime, credentials, Jetpack or images. A runnable synthetic Blueprint review bundle accompanies the local sprint artifact but is NOT the actual historic homepage. The committed GitHub exact-HEAD suite still needs clean-checkout execution and independent CI/QD.

## Mandatory remaining gates
A real isolated WordPress/Assembler render; exact Gutenberg parse/save and content preservation; proper authorization, HTTP CSP and private access; 320/360/390/768/1440/1920 viewport and 200% zoom screenshots; keyboard/touch/no-JS/reduced-motion; axe plus manual WCAG 2.2 AA; actual first-party archival image transfer bytes, rights and credits (PR #1730); Safari if available; measured lab Lighthouse and CWV (field data not inferred); true hosted Jetpack signup, confirmation and delivery via separately authorized safe test; CI/QD on exact SHA; founder's visual and release approval. Playground is NOT WordPress.com Atomic or hosted Jetpack equivalence. Do not automatically promote its acceptance to production.

## Conversion decision
**OFFER:** free 52-page Seven Day Focus Fieldbook, existing saleable offers only when rights/merchant verified.
**FUNNEL:** relevant Grok `asset_id`/campaign visitor → matching historical evidence → visible Focus CTA → independently confirmed subscriber → independently confirmed paid order/affiliate conversion → fees/refunds → realized net revenue.
**BLOCKER:** integrated Gutenberg behavior unverified; an unsafe all-page replacement could destroy historical records/native signup.
**CHANGE:** source-controlled local Blueprint bundle of EXACT scoped Gutenberg replacement, without live CMS writes.
**PASS/FAIL:** source integrity and mock PHP tests PASS (synthetic); real WordPress, accessibility, media, Jetpack and sales NOT TESTED, release HOLD.
**OWNER:** interim homepage engineering; Claude owns production integration and attribution, Grok/Praxxis own social acquisition, founder alone authorizes release.

No subscriptions or payouts asserted; no new affiliate offers, external analytics, campaign links, images, chapters, tracking code, paid plans, live content changes, merge or deployment. The Focus false-success repair PR #1681 remains a distinct release dependency.
