# Final Vestige · Assembler presentation parity (isolated local WordPress only)

**31 October 2026 · DRAFT / RELEASE HOLD · No production writes or publication**

## Why this exists

The earlier [isolated Playground stage builder, PR #265](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/265), provisions a genuine Assembler theme package, but the live Final Vestige WordPress **Assembler 0.0.126** experience also depends on **four site-editor overrides** and **custom global styles** that are not contained in a vanilla theme ZIP. Without these the staging viewport/art-direction composition can misrepresent the actual site's chrome.

Read-only connector audit of production site **256784396**, with no changes to it, identified:

| Public presentation source | Observed | This package |
|---|---|---|
| `assembler//page` (custom template) | Custom post-content wrapper + local style block | Sanitized block markup |
| `assembler//header` (custom template part) | Navigation, identity, CSS plus script-bearing custom HTML | Public navigation and CSS retained; scripts removed |
| `assembler//footer` (custom template part) | Public links and **production PostHog / Google Tag Manager and tracking scripts** | Public links/CSS retained; all active custom HTML omitted |
| `assembler//fv-archive-index-overlay` | Custom full-screen navigation overlay | Static public navigation + safe CSS retained |
| Global styles | Content size **760px**, wide **1440px**, ~48K of CSS | Public CSS retained verbatim; outbound CSS URLs/imports prohibited |

**No scripts, production analytics identifiers, API secrets, user accounts, subscriber records, production database, Jetpack activation, raw WXR, or private media** belong in the staged package. All incoming source is read-only and treated as untrusted even though it originated from WordPress.

## Actual source-controlled artifacts

- `assembler-public-safe.json` — *already-sanitized* site chrome, extracted using read-only WordPress tools and reviewed for script/telemetry/email markers. **This is public presentation, not a database export.** It is deliberately identified `local_only: true` and `release: HOLD`.
- `sanitize_theme_parity.py` — deterministic, strict fail-closed sanitizer if the local developer refreshes from a freshly captured **public-only** snapshot. Do not commit the raw input; its scripts may contain production analytics identifiers.
- `apply_local_parity.php` — opt-in, **not executed** WordPress importer. It refuses all hosts except `127.0.0.1`/`localhost`, requires `WP_ENVIRONMENT_TYPE=local`, exact Assembler `0.0.126`, the sanitization schema, and no unowned preexisting template overrides. Changes a **local-only development database** and is not a production installer.
- `blueprint.local.json` — WordPress Playground Blueprint for the local-only environment and import sequence.
- `test_sanitize_theme_parity.py` — 13 Python adversarial/unit tests including real PHP lint and in-memory Chromium synthetic telemetry rejection.

**Important:** Package creation and source-level verification are **not** an installed WordPress test, site rendering acceptance, exact-source browser QA, or an endorsement of archive image rights.

## Runbook (requires an already vetted Assembler theme directory)

**First** independently retrieve and verify the official **Assembler 0.0.126** theme archive and pin its SHA-256 under the checks required in [draft PR #272](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/272). Do **not** treat a copied `style.css` theme name or an arbitrary operator-supplied hash as proof of official origin.

From an isolated development workstation with Node.js 20.18+ and a free Playground CLI:

```bash
PARITY_DIR="$(pwd)/experience2/home-flagship/qa/playground/parity"
THEME_DIR="/ABSOLUTE/PATH/TO/INDEPENDENTLY_VERIFIED/assembler"

python -m unittest discover -s "$PARITY_DIR" -p 'test_sanitize_theme_parity.py' -v
php -l "$PARITY_DIR/apply_local_parity.php"

# This changes ONLY a new local Playground database; do not point it to production.
npx @wp-playground/cli@latest server \
  --site-url=http://127.0.0.1:9400 \
  --port=9400 \
  --mount="$THEME_DIR:/wordpress/wp-content/themes/assembler" \
  --mount="$PARITY_DIR:/wordpress/wp-content/uploads/fv-ex2-parity" \
  --blueprint="$PARITY_DIR/blueprint.local.json"
```

This command is **documented, not executed** in the engineering environment: official Assembler files, Node Playground runtime and a complete checkout were unavailable. A version drift or template override conflict must fail closed and be reviewed, never overridden silently. The Blueprint uses `defineWpConfigConsts`, `activateTheme` and `runPHP` steps supported by official WordPress Playground documentation:
[CLI](https://wordpress.github.io/wordpress-playground/developers/local-development/wp-playground-cli/),
[Blueprint steps](https://developer.wordpress.org/playground/blueprints/steps/),
[environment type](https://developer.wordpress.org/reference/functions/wp_get_environment_type/).

## What happens next

1. Run the parent exact-SHA private staging build from [#265](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/265)/[#272](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/272), authenticate a local editor-only preview, and ensure no public source exposure. Do **not** install/activate on the production WordPress.com Personal site.
2. With the actual seven-chapter `index.html` plus six CSS and four JS files from this PR's **exact Git checkout**, run the #252 seven-viewport/four-interaction/three-negative-control suite, #254 Franklin hero screenshot and 200% zoom, and #250/#285 WordPress/archival-HTTP admission. Do not mistake one source stack's SHA for another branch.
3. Run real Chromium first-screen/full-page comparison at 320/390/768/1440/1920px, 200% zoom, reduced-motion, keyboard, touch, no-JS, axe WCAG 2.2 AA (fail closed if absent), actual image HTTP response byte identity; Lighthouse/CWV lab. Test other art directions without selecting one for the founder.
4. Record **environment parity differences**: Playground uses local PHP/SQLite, not WordPress.com Atomic CDN, cookies, Jetpack, signup delivery, host-specific redirects or field CWV. The Focus Fieldbook and Jetpack form on **production homepage ID 6** are untouched; do not import subscribers or clone the live DB.
5. Obtain rights signoffs for the NYPL, Franklin and NASA images, hosted CI green on exact SHA, independent QD, founder art decision and explicit release approval. **RELEASE HOLD until all gates.**

## Security note

Only the *pre-sanitized* JSON is in Git. The original production header/footer custom HTML contained executable tracking; this package excludes it on purpose. Do not re-enable production analytics in staging. Do not copy secrets into test fixtures or receipts.

No additional subscription, affiliate CTA, historical chapter, image, CMS mutation, production template/style changes, PR #49 edits or live publication was performed. Apollo PR #158 and the separate Mind/Perception #171 lane remain independent.
