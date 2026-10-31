# Seven-chapter release-review surface — exact-source staging bridge

**Status: DRAFT / RELEASE HOLD.** This is a controlled engineering bridge from the existing seven-chapter design-study HTML to (1) a standalone local browser preview and (2) a **content-only** WordPress/Assembler fragment. Neither output is a deployed website, theme, template, plugin installation, merge, or authorized release.

## Exact source custody

- Parent: draft PR #362 exact SHA `fa6eab64eb5bc09e2a194690a4eadcdf44cfba7c` (the evidence-case chooser no longer depends on the developer toolbar).
- Original `experience2/home-flagship/index.html` Git blob **`70ebe0d8e122048343c99a3c6adc6f7ac498ed7f`**.
- Original `flagship.js` blob **`1888dbb5f77c348c43ddf2dbd276626459f19290`**. PR #49 remains frozen at `10495883299d53596992c26a8987f629b2904670`.
- No added historical data, images, remote fonts, outside code, affiliate URLs or claims. Franklin source-linked folio retained; the source rights review in PR #329 remains outstanding for binaries.

## Reproducible checkout commands

From the **exact checkout of this PR head**, with Node >=20:

```bash
node --test experience2/home-flagship/qa/release-candidate/test_release_review.cjs
node experience2/home-flagship/qa/release-candidate/build_release_review.cjs --out-dir /tmp/fv-private-seven-chapters
# Open /tmp/fv-private-seven-chapters/index.release-review.html under a local server, not a public CDN.
```

The builder fails closed if the original source Git blob changes, if the page loses its seven chapter identifiers, any Apollo/Franklin/Malbone case/control, its existing Focus paths, or the developer toolbar boundaries. It copies **exactly** six CSS and four JavaScript first-party files, writes SHA-256 size checks to `SOURCE_MANIFEST.json`, preserves the original standalone study unchanged and writes:

- `index.release-review.html` — includes exactly one semantic `<main>`, documentary hero, all seven chapters, three evidence panels, source links, native no-JS story, and no visible developer toolbar. Local relative CSS/JS paths work in the generated folder.
- `wordpress-page-fragment.review-only.html` — preserves the same source-backed story but omits the full document/head/scripts and replaces the nested `<main>` with a neutral content wrapper for embedding inside WordPress's existing page main. **It does not install itself or enqueue assets**; the authorized staging runtime must enqueue the manifest CSS/JS and safeguard the canonical header/footer.
- `SOURCE_MANIFEST.json` — source Git blob, SHA-256 content custody, asset checksums, environment disclaimer.

## Test outcome and limits (2026-10-31)

The **committed builder** was fetched back from GitHub and executed in a V8 compatibility environment against the **exact GitHub index.html blob**: 10/10 structural/adversarial checks passed (seven anchors; three case panels; Focus links; no nested WordPress main; dev controls removed; invalid source rejected). A standalone Node runner is committed but **has not been run in a full local checkout** during this sprint. The original artifact and candidate source are not locally mountable in this environment, and outbound GitHub/Playground HTTP cannot resolve from the local container. Thus the V8 results do **not** represent full Chromium, real WordPress, Assembler, Jetpack, LCP, axe, or Lighthouse certification.

## Production admission is still CLOSED

The WordPress.com Personal site `256784396` has no native staging clone. The default `*.wpcomstaging.com` alias is production, **not** a private stage. A free isolated WordPress Playground/localhost Assembler developer installation may be used only with **public-only** data, never subscribers, secrets, accounts, session cookies or a production DB. WordPress Playground differs from WordPress.com Atomic infrastructure.

Before release obtain an independent exact-head full checkout and actual integrated private WordPress staging with: Assembler theme verification; first-party image network fetch and decoded dimensions/bytes; source-specific NASA/Franklin/NYPL binary rights; full 320/360/390/768/1024/1440/1920 Chromium and 200% zoom screenshots; four real interactions plus three CSP negatives; no-JS content; keyboard/touch/reduced-motion/forced-colors; axe WCAG 2.2 AA with library available; honest Lighthouse and field CWV qualifications; no duplicated navigation/landmarks; and independent QD/CI and founder visual/release approval. Use existing `verify_csp_exact_browser.py`, `verify_exact_staging.py` and `verify_archival_attribution.py` as applicable. Do not call isolated fixture evidence a hosted acceptance result.

Production page 6 read-only audit on this run: **72** Margins records, **2** Focus paths, and native Jetpack subscriptions markup retained. `FV Focus Popup` version **0.1.1 is active** but page 6 does **not** contain the `[fv_focus_popup]` shortcode; installation is not popup placement, nor proof of email fulfillment. No page/template/navigation edits performed.

**No merge, deploy, publication, WordPress settings/markup mutation, or plugin activation is authorized by this work.** Apollo PR #158 and Mind issue #171 remain separate lanes.
