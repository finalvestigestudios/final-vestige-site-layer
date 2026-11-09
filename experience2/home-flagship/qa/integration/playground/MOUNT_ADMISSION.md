# Final Vestige EX2 — exact-seal local Playground mount admission

**REVIEW ONLY / DO NOT DEPLOY.** This is an isolated companion to PR #1760, itself stacked on #1753, #1750 and the sealed renderer #224. The frozen homepage PR #49 is unchanged. The published WordPress Page 6, 72 Margins records, Focus Fieldbook and Jetpack are outside this operation.

## Concrete integration problem

The earlier package builder creates `out/plugin/fv-ex2-sealed-staging-preview/fv-ex2-sealed-preview.php` and a Blueprint that executes `activatePlugin`. However, the Blueprint **does not install or mount local plugin files**. Running `--blueprint=out/blueprint.json` without mounting the generated plugin first can fail at activation. The documented Playground CLI `server --mount=/host/path:/wordpress/wp-content/plugins/plugin-name` fills that gap. See official [Playground CLI handbook](https://wordpress.github.io/wordpress-playground/developers/local-development/wp-playground-cli/) and [Blueprint activatePlugin contract](https://developer.wordpress.org/playground/blueprints/steps/#activateplugin).

## Exact-source local sequence

1. In a clean checkout of **this PR's exact HEAD** (not #254's head or frozen #49), generate the existing offline package with `python experience2/home-flagship/qa/integration/playground/make_local_playground.py --repo . --expected-head <FULL_THIS_PR_HEAD> --out /tmp/fv-ex2-local-package`. The generator separately checks tracked source blobs and stage manifest; output must be outside the repo and WordPress paths.
2. Install the free open-source `@wp-playground/cli` locally in the developer environment (no FV subscription or production integration). Use Node.js 20.18+; record the exact CLI version in the staging receipt.
3. First run `python experience2/home-flagship/qa/integration/playground/run_local_playground.py --out /tmp/fv-ex2-local-package --expected-head <FULL_THIS_PR_HEAD> --dry-run`. Review the mandated `--mount`, local hostname, exact Blueprint path, and checksum verification.
4. Without `--dry-run`, the same command calls **locally preinstalled** Playground CLI via `npx --no-install`. This makes no network fetch for the CLI package itself. The CLI may fetch WordPress/Runtime dependencies when run; keep execution on a private developer machine. Only use the private `/fv-ex2-local-review/` reviewer page. Never point this workflow at production or upload the ZIP.
5. Perform full authenticated top-level / iframe review, first-party archive network, 320/360/390/768/1440/1920px screenshots, 200% zoom, keyboard, touch, no-JS, reduced-motion, axe (fail closed if unavailable), lab Lighthouse/CWV and time-stamped screenshot/bytes receipts. **No JavaScript or browser/WordPress tests are claimed by this change.**

## Verification & acceptance

- `python -m unittest -v test_run_local_playground.py`: **10/10 PASS locally** against synthetic sealed-package fixtures; checks exact-head rejection, checksum/tamper, symlink, missing plugin, production environment, public page and wrong activation path fail closed.
- `python -m py_compile run_local_playground.py`: PASS.
- The two exact GitHub source blobs are independently checked against the local files. These tests establish the *launcher contract*, not an installed WordPress instance.
- No new imagery, user information, passwords, subscribers, redirect scripts, affiliate offers or tracking. Existing rights ledger in PR #1730 is unchanged.

**Open gates:** Real WordPress Playground runtime cannot be launched in this restricted execution environment (CLI unavailable); Assembler theme/WordPress.com hosting equivalence, GitHub Actions/QD, WordPress-native plugin/nonce HTTP behavior, actual images, accessibility, Lighthouse, true Jetpack confirmation, and realized commercial conversion remain unverified. Preserve release HOLD and require explicit founder approval before any live operation.