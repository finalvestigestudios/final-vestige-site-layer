# Experience 2.0 — free local WordPress Playground staging lane

**Status: DRAFT / UNPUBLISHED / RELEASE HOLD.** This replaces the obsolete assumption that the founder can create a free WordPress.com one-click staging clone. The connected site `finalvestige.com` is on **Personal**, and `vestigefinal-tezws.wpcomstaging.com` is the existing site's alternate address, **not** a private clone. Do not request an upgrade or install anything on production.

The source-controlled program `prepare_isolated_stage.py` builds a *localhost-only* review kit around the **already-tested, PHP-only, authenticated staging-preview plugin** from the current homepage stack (PR #225/#244/#250). The existing seven-chapter candidate and all its HTML/CSS/JS are packaged from a clean **exact HEAD**, never from a synthetic stand-in or a newly invented chapter. This stage is an isolated WordPress instance, **not** a WordPress.com Atomic replica.

## Inputs (must be provided locally)

1. A complete Git checkout whose `HEAD` is the exact reviewed 40-character SHA, including the nested Experience 2.0 homepage changes and the new QA directory. Never use a branch name as a substitute for the exact SHA.
2. The official **Assembler theme ZIP** from [WordPress.com's free Assembler page](https://wordpress.com/theme/assembler) (download button), unmodified. The program requires `assembler/style.css` identifying the Assembler theme and `assembler/templates/index.html`. **Important:** the Theme Name header is spoofable; the builder now additionally requires an independently recorded SHA-256 of the exact Assembler ZIP. Never treat hashing an untrusted ZIP and passing that hash as proof of official origin. Do **not** silently replace it with Twenty Twenty-Five or a different theme.
3. A fresh output directory **outside** the Git checkout, e.g. `/tmp/fv-ex2-local-stage`.
4. For actual WordPress execution, Node 20.18+, free official `@wp-playground/cli`, and local Chromium/Playwright. Dependency installation can require internet and has **not** succeeded in the current automation environment; no CLI launch is claimed.

## Offline, exact-source package preparation

```bash
cd /path/to/final-vestige-site-layer
python -m unittest discover -s experience2/home-flagship/qa/playground -p 'test_*.py' -v
python experience2/home-flagship/qa/playground/prepare_isolated_stage.py \
  --repo . \
  --expected-head "$(git rev-parse HEAD)" \
  --assembler-zip "$HOME/Downloads/assembler.zip" \
  --expected-theme-sha256 "<64-character checksum from separately reviewed trusted record>" \
  --out /tmp/fv-ex2-local-stage
```

The entry point first verifies the **Playground stage builder itself**, its tests and this runbook against `git show <exact SHA>:<path>` and rejects dirty/untracked/symlinked files, then invokes the existing `attest_private_preview.py` rather than trusting the command-line commit string. That attester compares required files with committed Git blobs, runs the canonical 19-check Node source gate, and builds the PHP-only ZIP twice for byte equality before the Playground builder accepts it. An untracked/modified/incorrect staging builder, a malformed theme ZIP, a theme ZIP whose SHA-256 differs from the independently supplied pin, plugin source disclosure, or a failed gate is a hard failure. A matching operator-supplied hash **does not independently prove that Automattic published the ZIP**; retain the official download receipt and conduct a separate provenance review before release. The generator marks this status as unresolved.

The generated output contains `mounts/assembler` (from the supplied theme ZIP), `mounts/fv-ex2-private-preview` (PHP-only), `playground-blueprint.json`, `playground-cli-arguments.json`, the exact-source ZIP and `STAGING_PREP_RECEIPT.json`. The manifest explicitly says release HOLD, records hashes for all three version-pinned staging source files and the theme, and records `official_assembler_origin_independently_confirmed: false`. **No private WordPress.com database, users, subscribers, tokens, Jetpack settings, analytics secrets, or WXR export are imported.** The generator makes no WordPress or network calls and does not install/activate anything anywhere.

## Optional separate local developer launch — not authorized production deployment

Review `STAGING_PREP_RECEIPT.json` and `playground-cli-arguments.json` first. On a machine where the official Playground CLI can be obtained, run the argv list (not a shell string):

```bash
python - <<'PY'
import json, subprocess
from pathlib import Path
args=json.loads(Path('/tmp/fv-ex2-local-stage/playground-cli-arguments.json').read_text())
assert args[:3] == ['npx','@wp-playground/cli@latest','server']
subprocess.run(args, check=True)
PY
```

The Blueprint defines `WP_ENVIRONMENT_TYPE=local` and `FV_EX2_ALLOW_PREVIEW=true` **inside Playground only**, activates the independently supplied Assembler theme and guarded preview plugin, and creates one **private** WordPress page with `[fv_ex2_homepage_preview_private]`. It never sets the local site front page or changes public production URLs. The Blueprint's local seeding PHP refuses to run unless the WP environment is `local` **and** the runtime host is `localhost` or `127.0.0.1`. The preview plugin independently requires logged-in editor capability and valid nonce for its AJAX renderer.

Once running, the editor-only preview path is `http://127.0.0.1:9400/?pagename=fv-ex2-playground-review` (unless the CLI chooses a different host). Confirm authentication and the preview manually before collecting a local browser storage-state file. Never publish, attach, or commit browser storage state or WordPress credentials. Run the repo's existing `verify_exact_staging.py` with `--allow-host 127.0.0.1`, `--expected-head <exact HEAD>`, `--storage-state <local-private-file>` and `--axe-script <locally licensed axe.min.js>`; **do not assert an axe PASS if the script is unavailable.** Record 360/390/768/1440/1920 and, separately, the 320px/200% zoom, reduced-motion, no-JS, keyboard/touch, and manual AT observations. Also execute the committed #252 seven-width/four-interaction/three-negative-control offline CSP gate against the same SHA. Capture *actual* screenshots, image `currentSrc`, `naturalWidth` and network transferred bytes, and Lighthouse CLI output where available. Flag absent data as **NOT MEASURED**.

## Strict environment-parity limitations

This is **WordPress-native PHP and Assembler in a local Playground**, NOT WordPress.com Atomic: it cannot establish Jetpack signup behavior, WordPress.com reverse-proxy cookies/redirects/cache/CSP, production template customizations, real storage/sync, or field p75 Core Web Vitals. Its PHP renderer is a private *iframe review tool*, not the final WordPress-native homepage migration. The real `/focus/` destination remains production; do not transplant or simulate signup credentials. Original historical imagery points to the public site/CDN, but the image-rights ledger (especially NYPL) still requires independent editorial clearance. NASA imagery may not imply endorsement. No new Inspire3 checkout link or unsupported claims are added.

## Actual evidence and release requirements

The original PR included 12 local offline synthetic-fixture regression tests; this follow-up adds real Git-repository dirty/symlink/SHA cases and independent theme-digest mismatch/missing-pin cases (16 total). for archive/path attacks, substituted themes, source leak detection, source receipt mismatch, output isolation, local-only/private WordPress seeding, and HOLD state. The seeding PHP also passes `php -l` locally. This is NOT a claim that WordPress Playground was started, that actual image bytes transferred, that 7-width live Chromium, axe, Safari, or Lighthouse ran, or that WCAG 2.2 AA or GitHub CI/QD passed.

Before ANY public release: founder visual review of three art directions and selected first-screen design, actual isolated WordPress+Assembler browser QA, verified archival image rights, actual Lighthouse lab measurements and separate field CWV baselines, hosted CI, exact-SHA independent QD, and explicit release approval. Frozen PR #49 must remain untouched, all 72 Margins records and the published 52-page Focus Fieldbook/Jetpack signup must be preserved. No staging-to-production database sync under any circumstances.
