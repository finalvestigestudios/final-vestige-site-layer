# EX2 Playground sealed-preview mount custody — 2026-11-09

**Status:** DRAFT; no production CMS writes, no deployment, no staging runtime acceptance. Source branch is stacked on PR #1767, not frozen PR #49.

## Reproduced defect (local, not on finalvestige.com)

The local Playground launcher checked SHA-256 of the generated PHP entrypoint, receipt, ZIP and Blueprint, **but mounted the entire plugin directory** with `--mount=hostpath:/wordpress/wp-content/plugins/fv-ex2-sealed-staging-preview`. Extra files in that directory, such as `assets/index.html.txt`, were never inventoried. If present in an actual web-served WordPress plugin directory, raw source files could be directly requestable without the private PHP/AJAX authorization checks. This violates the sealed-preview threat model in PR #224.

The builder reuses output directories and wrote `fv-ex2-sealed-preview.php` with `Path.write_bytes` without checking whether the existing destination was a symbolic link. A synthetic local test demonstrated writing through such a link to an external canary file. **This is a demonstrated filesystem flaw, not evidence of a real attack, production leak or WordPress installation.**

## Source-controlled repair

1. `make_local_playground.py` now performs **pre-write validation**, before invoking the ZIP builder or creating directories. Reject symlinked/incorrect-type output files and plugin directories; reject any extra file, hidden item or nested directory in the mounted plugin folder. Prevent accidental overwrite outside the approved temporary output through a preexisting symlink.
2. `run_local_playground.py` independently rechecks that its mounted plugin directory contains exactly the expected sealed PHP file. The existing SHA-256 and source-head checks remain intact.
3. `test_mount_custody.py` adds **10 adversarial local-filesystem cases** for HTML/.txt copies, hidden files, nested source directories, extraneous PHP, symlinked folders and files, and unintended external writes.

## Reproducible local verification

```bash
cd experience2/home-flagship/qa/integration/playground
python -m unittest -v test_run_local_playground test_make_local_playground test_mount_custody
python -m py_compile make_local_playground.py run_local_playground.py test_mount_custody.py
```

**Local results:** 29/29 passing Python tests (19 inherited regression tests + 10 added); Python compilation PASS. Source copies executed locally matched the three exact GitHub blob SHAs for this branch at the time of publication. Negative controls reproduced **both** the previously accepted unlisted public HTML file and the symlinked-PHP external-canary overwrite in a synthetic directory before the fixes.

**Not tested:** WordPress Playground runtime (CLI unavailable due to network/DNS restriction), actual WordPress plugin activation, authenticated AJAX page, browser screenshot/axe/Lighthouse, image-network transfers, hosted WordPress.com-specific behavior or a genuine Jetpack signup. **No security finding is claimed against the live website.** Do not promote synthetic tests into WordPress staging acceptance.

## Explicit release gates / ownership

- Run the actual exact-HEAD local Playground Blueprint and mount against a clean WordPress/Assembler installation.
- Confirm private page and top-level link with authenticated editor; anonymously probe for raw source assets and fail on **any HTTP 200**. Verify no source files are installed alongside the PHP plugin.
- Independently execute the existing Chromium seven-chapter/CSP interaction suite, a real WCAG 2.2 AA review, 320/390/768/1440/1920/200%-zoom and reduced-motion/no-JS/keyboard tests.
- Measure image network bytes for Apollo/Franklin/NYPL and lab Lighthouse; retain source rights caveats from PR #1730.
- Keep existing Focus PDF, Jetpack signup, 72 Margins, and Grok source/UTM ownership unchanged. Homepage hero Focus CTA remains on hold pending PR #1681 real subscriber-state acceptance.
- No merges, activation, plugin install, CMS edits or production release without founder sign-off. CI/QD exact SHA approvals outstanding.

**Conversion contract:** Offer = existing 52-page Focus Fieldbook; funnel = first-party evidence → meaningful CTA → verified lead → independently verified paid order; blocker = no safe integrated private preview acceptance; change = fail-closed plugin asset custody; evidence = 29 local tests; commercial result = unmeasured (not a purchase or subscriber improvement).
