# Experience 2.0 — sealed WordPress staging preview (DRAFT / HOLD)

This is a **separate, more restrictive alternative** to the existing iframe preview in PR #212. It does **not** modify the existing preview or production website.

## Problem found

The old staging ZIP places \`assets/index.html.txt\` inside the public \`wp-content/plugins/\` directory. Renaming HTML to \`.txt\` does not make it access-controlled; many WordPress configurations serve it directly to anonymous HTTP clients. The editor-only shortcode and AJAX nonce do not protect the direct file URL. The associated public CSS and JS files are also directly accessible.

## Change

\`build_sealed_staging_zip.py\` packages the **exact checked-out** homepage source (index, 6 CSS, 4 JS) into a deterministic 3-file ZIP: a generated PHP plugin containing compressed, SHA-256 checked source constants, a source-hash manifest, and an installation HOLD notice. **No static unpublished HTML/CSS/JS is present in public plugin asset paths.** The PHP entrypoint is executable only by WordPress. The privileged AJAX renderer verifies site environment, explicit opt-in, login, edit-pages capability and nonce, then emits a complete self-contained iframe document with nonce-authorized inline scripts, order-preserving tail execution, noindex/no-cache and restrictive Content Security Policy. Missing or changed source files fail closed.

Staging-only shortcode: \`[fv_ex2_sealed_homepage_preview]\`. Installation and publication remain strictly prohibited absent founder authorization and a separate non-production WordPress environment. The generated PHP code intentionally has no installer, no backend mutations, no subscriber collection and no public nopriv Ajax registration.

## Reproduction on the precise source checkout

From repository root:

\`\`\`bash
python -I -m unittest discover -s experience2/home-flagship/qa/integration/sealed -p 'test_*.py' -v
python -I experience2/home-flagship/qa/integration/sealed/build_sealed_staging_zip.py --root experience2/home-flagship --expected-head "$(git rev-parse HEAD)" --out /tmp/fv-ex2-sealed-staging.zip
\`\`\`

Also run the existing integration \`check_contract.py\`, \`verify_full_browser.py\` and core homepage tests on this exact head, followed by separate actual WordPress staging authentication/nonce/CSP, real image and cross-browser testing.

### Local proof (scope deliberately bounded)

The new builder and template passed **5/5 Python/PHP tests** on a prior **representative 7-chapter composite fixture**, including deterministic builds, no static source files, no missing JS acceptance, rejection of bogus Git SHA, PHP syntax, production/guest/non-editor refusal, and authenticated Ajax assembly. Chromium rendered the generated **self-contained offline fixture** at 320, 390, 768, 1440 and 1920 CSS px with six styles/four scripts, no root horizontal overflow or page script exceptions in those tests. All remote images intentionally blocked; this did not test actual WordPress HTTP, cookies, browser Ajax loading, same-origin policies or the exact new GitHub commit. A localhost browser test was blocked by Chromium's administrative network policy, so no hosted staging compatibility claim is made.

### Non-waivable holds

- Not a replacement for actual WordPress staging / Assembler theme integration, WCAG 2.2 AA, Safari, axe, assistive-tech or production Core Web Vitals evidence.
- Authentic archival asset licensing (NYPL, NASA publicity/endorsement boundaries) and independent QD remain pending.
- GitHub Actions hosted CI and branch protection remain unresolved (Issues #75/#191).
- Do not merge to main/production, activate a plugin, change the existing page 6, recreate navigation, or touch Focus Fieldbook/Jetpack until a distinct authorized release.

This PR is stacked on homepage Reading Trail PR #217 at the recorded head. The frozen v1 homepage PR #49 remains untouched.