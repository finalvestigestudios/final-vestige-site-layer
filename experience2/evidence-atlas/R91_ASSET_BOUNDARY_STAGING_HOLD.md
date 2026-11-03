# Apollo R91 — source-safe staging asset boundary and four-view browser matrix

**NOT FOR PUBLICATION / STAGING HOLD.** Isolated from homepage PR #49 and its lead branches, Research Desk PR #158, main and production WordPress.

## Actual gap in R90

R90 verifies all six NASA source identities in 24 individual HTML evidence cards. Its link scanner does not examine stylesheet imports or the contents of packaged CSS/JavaScript. A remote `@import`, CSS background photograph, or stylesheet link could therefore evade the current NASA-link and `<img>` checks. This is a preventive custody correction: no such inclusion is alleged in R90.

## Implemented

`tools/build_release_candidate_r91.py` runs the actual R90 staging generator in a disposable directory and audits the generated files **before exporting**. Only four expected HTML pages, four local stylesheets, one deferred local script and four exact legacy receipts may enter the package. HTML stylesheet imports, unexpected scripts, inline event handlers and styles, preloads and media attributes are refused; CSS imported URLs/images/fonts, escaped CSS assets and common JS network APIs are rejected. The independent Chromium suite blocks/records any unexpected outbound request as a second protection. Static scans are **not** claimed to be an exhaustive script security proof.

The new R91 receipt preserves R90's 24 verified card-to-source bindings and explicitly records `STAGING_HOLD`, no publication approval, zero cleared photographic rights and no hosted WordPress acceptance. The wrapper writes a reproducible, sorted ZIP with pinned metadata and SHA-256 manifest.

The independent four-view Playwright suite tests **40 configurations:** each of the four actual interfaces at 320/390/768/1440/1920px, JavaScript disabled and enabled. Each is checked for six individually correct NASA links, no invented geo/media, keyboard Enter and Space source disclosure, no horizontal overflow, local-only requests and no-JS completeness. R88 two-source comparison is exercised when JS is enabled. Eight axe-core WCAG-tagged audits, reduced-motion settings, forced-colors screenshots, native printed evidence PDFs for all four views and laboratory LCP/CLS checks are retained as review artifacts.

## Reproduce from exact GitHub PR head

```bash
export PYTHONPYCACHEPREFIX="${TMPDIR:-/tmp}/apollo-r91-pycache"
python -m unittest discover -s experience2/evidence-atlas/tests -p test_release_candidate_r91.py -v
python experience2/evidence-atlas/tools/build_release_candidate_r91.py /tmp/fv-r91-A /tmp/fv-r91-A.zip
python experience2/evidence-atlas/tools/build_release_candidate_r91.py /tmp/fv-r91-B /tmp/fv-r91-B.zip
cmp /tmp/fv-r91-A.zip /tmp/fv-r91-B.zip
# Real browser acceptance: .github/workflows/ex2-apollo-r91-asset-boundary.yml
```

Do **not** install or publish the generated review bundle. It is an offline engineering artifact, not a deployable WordPress plugin or approved media package.

## Release blockers remain

Individual NASA photograph reuse decisions **0/6**; crew portrait `S67-19766` catalog association remains provisional; authorized isolated hosted WordPress.com testing, NVDA/VoiceOver and physical device acceptance, independent QA, hosted Core Web Vitals and founder approval are still needed. Lab success does not close any of those gates. No CMS, theme or plugin writes; no merges or paid services; no changes to homepage PR #49 or Research Desk PR #158.
