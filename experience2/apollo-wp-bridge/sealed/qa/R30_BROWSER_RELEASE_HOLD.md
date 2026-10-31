# Apollo Experience 2.0 R30 — repository-native browser release gate

**DRAFT / RELEASE HOLD.** This code is isolated to `experience2/apollo-wp-bridge/sealed/qa/` and MUST NOT be installed on production. No WordPress writes, homepage files, PR #49, PR #158, or Atlas geographic data are changed.

## What changed

`browser_release_head_r30.py` exercises the **existing** `qa.browser_exact.get_fixture()` assembly of the source-pinned staging PHP, rather than inventing a second HTML exhibit. It checks complete DOM/source custody, the 6 NASA concordance records, the 6 media-rights holds, the 1 unresolved NASA identity hold, all in-page links, unique IDs, accessible link/field names, safe outbound-link attributes, zero geospatial pins, horizontal reflow, native keyboard/nested disclosures, touch, reduced-motion and JS-disabled reading. It captures screenshots and laboratory-only PerformanceObserver readings across seven viewport widths.

`test_browser_release_head_r30.py` adds fail-closed adversarial cases for fabricated coordinates, removed rights/identity warnings, missing NASA source records, duplicate IDs, broken anchors, unsafe/unnamed links, unlabeled fields and horizontal overflow.

### Reproduce from a full exact repository checkout

```bash
python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p test_browser_release_head_r30.py -v
python experience2/apollo-wp-bridge/sealed/qa/browser_release_head_r30.py --out /tmp/fv-apollo-r30
```

Requirements: Python 3.10+, PHP CLI, `playwright` and **installed** Chromium. The script expects `/usr/bin/chromium` by default. For axe-core, supply only a locally verified executable source and `--axe-js ... --axe-sha256 ...`. This checks equality to the **caller-supplied** hash; it does not authenticate an official upstream release and does not by itself constitute accessibility certification.

### Actually executed local evidence (2026-10-31)

- Separate source-locked R29 ZIP `d29ee02d629ae50716058b8ffa6cb3d9bac76a9cd72d9e3387504e2d22dab14f`, sealed plugin SHA-256 `ea465fcb6518ae2ba6bfaf8c6cd66dae354de4887e402ab4f0a27d02d28c8168`, PHP shim output SHA-256 `adc83b7d801356c57a327866d7a1d8cba9b01a357e4dfc64810e77f4b27a59a6`.
- **Actual Chromium 144**: 7/7 viewport passes (320, 360, 390, 768, 1024, 1440, 1920). No page errors, external network requests or horizontal overflow. Six NASA records, six photo rights holds, one unresolved identity hold and zero Atlas location pins. Keyboard and native nested details worked; a separate JS-disabled and touch-enabled context passed.
- R30 local source-controlled gate tested with a fixture adapter pointing to the *same exact rendered R29 HTML*, not a complete freshly cloned GitHub checkout. Reported `7/7 PASS`; two screenshot hashes reproduced byte-identically in a second run. The repository-native `qa.browser_exact` import has **not** been executed in a full current checkout. Do not conflate the local fixture validation with complete exact-HEAD integration.
- 9/9 independent ZIP/HTML/adversarial tests plus 5/5 repo-gate mutation tests passed locally. All source-controlled file blob SHA-1 IDs verified against local tested bytes.
- Synthetic browser `largest-contentful-paint` samples ranged approximately 152–404ms and zero layout shifts were observed **in the limited in-memory session only**. These are not field metrics, meaningful website LCP/CLS guarantees or full accessibility evidence.

### Required release gates

Verified upstream axe-core bundle run (not available in the isolated environment), real browser-enforced WordPress HTTP response CSP/cookies and staging login, independent real WordPress Assembler integration, keyboard/screen-reader and Safari verification, media rights review, source identifier `S67-19766` authoritative reconciliation, hosted p75 CWV, independent QD and exact-HEAD passing CI. No image reuse clearance, publication or approval is implied.

**Coordination:** Homepage consolidated PR #368 and frozen PR #49 are separate lanes. Keep this QA-only branch unmerged and do not alter live WordPress or the Research Desk PR #158.
