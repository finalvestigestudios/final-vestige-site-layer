# Seven-chapter flagship — exact-source Chromium release-output admission

**2026-10-31 · DRAFT · RELEASE HOLD.** Parent PR #375 exact commit `63a25bb77173c77cc6c9d5f1f5d27b345bfa8512`. Frozen v1 PR #49 `10495883299d53596992c26a8987f629b2904670` untouched.

## What was actually executed

The 13 current GitHub source files (canonical `index.html`, six CSS, four JS, builder and existing Node suite) were transferred into an isolated local working directory and independently attested against **all thirteen Git blob SHA-1 values**. **This was a byte-attested working tree, not a full Git repository checkout; don't call it an exact `git rev-parse HEAD` verification.** The release builder's built-in SHA pins independently checked the original HTML and all ten assets, then generated a private 12-file bundle without altering any CMS.

1. **A real Node regression failure was discovered.** The parent `test_release_review.cjs` had 19/20 passing assertions. It compared `manifest.files`, deliberately created with `Object.create(null)`, to a JSON-parsed object whose default prototype differs. This produced a false negative despite identical serialized manifest bytes. The isolated fix keeps the null-prototype dictionary and compares JSON round-trip semantics. **Re-run: 20/20 PASS.** No homepage HTML/CSS/JS behavior changed.
2. **Actual Chromium 144** (Python Playwright, browser `page.set_content`) executed the builder-generated standalone release HTML with the **unaltered six CSS and four JS files inlined with a local test-only CSP nonce**. This bypasses blocked `file://` and localhost navigation, while preserving exact source bytes. **Widths 320/360/390/768/1024/1440/1920: 7/7 PASS, zero root horizontal overflow, zero page JavaScript exceptions.**
3. **Four real interactions: 4/4 PASS**: case chooser selects Franklin and hides Apollo; Victory Point reading lens selects original 1847; Observer Lab switches to Frame B without answer disclosure; keyboard Enter on chapter four moves browser fragment and focus to `#fv-hf-inquiry`.
4. **Three real CSP negative controls: 3/3 PASS** in the local document: unnonced inline script, wrong-nonce inline script, and inline image event-handler injection remain blocked. This is **not** the WordPress HTTP CSP header or session/cookie test.
5. **JavaScript disabled:** all three evidence panels and both observation frames remain visible, with enhancement-only controls hidden. **PASS.**
6. **Simulated 200% CSS zoom at 390px:** no root overflow. **PASS**; not a native browser toolbar zoom/assistive-technology certification.
7. Captured genuine **first-screen Chromium screenshots at seven widths** and **full-page screenshots at 320/390/768/1440/1920**, plus simulated zoom image. These remain offline artifacts supplied to founder; not a hosted WordPress screenshot.

## Reproduce from a full Git checkout at this branch

```bash
node --test experience2/home-flagship/qa/release-candidate/test_release_review.cjs
python -m playwright install chromium  # only if browser not already installed
python experience2/home-flagship/qa/release-candidate/verify_release_surface_browser.py --output-dir /private/fv-seven-chapter-browser
```

Dependencies: Python Playwright, Node, Chromium (discoverable in PATH, override with `FV_CHROMIUM_EXECUTABLE`). Script aborts on any failing assertion; saves a per-file SHA-256 and Git-blob provenance receipt.

## Source custody

Canonical HTML Git blob: `70ebe0d8e122048343c99a3c6adc6f7ac498ed7f` and SHA-256 `98e7b757ef9666cf3edb5c4c33b843657427a7574bba695844ca268464e90b4a`. All ten canonical CSS/JS Git blob pins remain unchanged from PR #375. Updated Node test blob: `f50e64682572587d6d0d6cf9e37853322820d829`. New Chromium test blob: `a6b06331332ab8f11c83ead3f77c315d85717e09`.

## Explicit non-waivable HOLD

- This is an **isolated browser execution of complete exact source**, **not** WordPress Playground, native Assembler theme, Jetpack, production HTTP requests, source-photo bytes, original archival rights, Safari, manual assistive technology, axe WCAG 2.2 AA, Lighthouse or real-user CWV.
- The browser deliberately denied remote images; the source has honest textual fallbacks. Do not infer first-party image loading, image decoding or commercial reuse permission.
- Official Assembler 0.0.126 local WordPress and sanitized public parity import from PR #291/#297/#322 must be executed before WordPress staging can be marked passed. WordPress.com Personal has no native staging clone.
- GitHub Actions exact-head CI, independent QD, founder selection of art direction, and explicit site publication approval remain required.
- No changes to 72 Margins items, Focus Fieldbook, active Jetpack, WordPress homepage page 6, popup placement, Apollo PR #158, Mind Issue #171 or frozen PR #49. No CMS write, plugin activation, merge or deployment.

**Decision: HOLD — source-level and offline Chromium gate materially advanced, native integrated staging remains outstanding.**
