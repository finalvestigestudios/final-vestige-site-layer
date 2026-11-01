# Apollo R49 — reciprocal source navigation · STAGING HOLD

This isolated change adds optional **Research Desk → Evidence Atlas** source links. Existing Atlas → Desk jumps remain. Each of the six backlinks is created only when the independently versioned Research Desk contains exactly six matching NASA catalog identifiers, record IDs, and original NASA image-detail URLs. A missing/duplicate Desk, incomplete link containers, or a late source mutation withholds or removes the enhancement; the static evidence remains readable. No Research Desk source file is edited.

## Exact source custody

- Parent: R48 PR #493, `cdbbd974d5afca4243f34190b04fba0382d5078d`.
- Original Research Desk PR #158, head `250d7f05a4de037e73826dcf0cfaef0ec4c29383`.
- Unmodified original PR158 template Git blob `403d128c57b9bc82dac7c619651689070edef86c`, copied to `tests/fixtures/source-ledger.pr158.html`.
- Unmodified original PR158 CSS Git blob `b8cf00afeceba115a9e9d19044fc11dcf2890cbe`, copied to `tests/fixtures/source-ledger.pr158.css`.
- Unmodified original PR158 JS Git blob `32e757cc4dc8708397ff65ac21e89dd319781d78`, pinned in existing `tests/fixtures/source-ledger.pr158.js`.
- R37 NASA crosswalk blob `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea` unchanged. Six individual image-use reviews remain **UNREVIEWED**.

## Reproduction

Run `python -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q`, `php -l experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php`, `node --check experience2/evidence-atlas/atlas.js`, and `python experience2/evidence-atlas/tests/browser_r49_reciprocal.py --output <private-dir>`.

The source-controlled R49 browser runner consumes actual original PR158 template/CSS/JS blobs and locally PHP-rendered Atlas markup. It covers JavaScript-on/off, touch/reduced motion, 320–1920px, filtered source restoration, keyboard focus, exact fragment navigation, adversarial provenance mutations and reproducible screenshots. It uses Playwright `set_content`, **not installed WordPress or navigated HTTP**, because Chromium localhost navigation is blocked in this execution environment. Until that runner executes in an environment with the original fixture, do not claim its result as PASS.

The separate synthetic fixture smoke tests in the originating workspace are explicitly **not** proof of original PR158 markup compatibility. Unverified axe-core, authentic WordPress/Assembler, hosted LCP/CLS/INP, Safari/AT, image-use rights, green hosted CI and independent QA remain release blockers.

## Release policy

**HOLD:** No merge, production deployment, WordPress content/settings/plugin writes, payments, invented pins/edges or photographs. Homepage PR #49 and the homepage engineering lane remain untouched. Founder approval and independent release QA are required.
