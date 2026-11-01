# Apollo R53 — nested Gutenberg pre-head assets and original R38 QA gate (DRAFT / HOLD)

**Parent:** R52 PR #518, SHA `ecd9bf1c4b33c119d343e84dac062f7c6de0795d`. **Scope:** `experience2/evidence-atlas/` only. No WordPress CMS writes, plugin activation, photography, navigation changes, merges, or deployment.

## Concrete risk corrected

The R52 suite correctly admits exact original PR #158 or complete R38 source profiles but it did **not** enqueue Atlas CSS/JS before `wp_head` when the suite shortcode was hidden inside a dynamic Gutenberg/reusable block. Its early hook also inspected only raw top-level `post_content` and thus missed nested blocks. R38 Research Desk preloads its own scoped assets on singular pages; the Atlas and suite stylesheet still had a late-style/FOUC risk.

R53 calls the registered Atlas enqueue helper from the suite's existing pre-head enqueue function. Because Atlas registers at `wp_enqueue_scripts` priority 20 and suite preflight runs at 22, CSS and JS can be queued before `wp_head`. For nested Gutenberg/reusable/template-part instances on a **known private staging singular page only**, the host may define an explicit ID allowlist in private PHP configuration:

```php
define('FV_EX2_APOLLO_SUITE_PRELOAD_PAGE_IDS', array(123)); // replace 123 with PRIVATE staging page ID
```

This constant is optional. Direct top-level shortcodes continue discovery from raw `post_content`. Invalid/list string/negative IDs fail closed; unrelated pages do not preload suite assets. WordPress `wp_enqueue_*` deduplicates handles; do not copy an unreviewed shortcode into public template parts and expect this to cover arbitrary archives. This is a narrow, explicit stage workaround, not a universal Gutenberg discovery engine. Do **not** use production page ID 6 without separate release approval.

## Real-source browser acceptance path

`tests/browser_r53_actual_r38.py` checks all **five** exact original R38 file Git blob hashes before rendering the actual R38 `templates/ledger.html`, `assets/source-ledger.css`, `assets/source-ledger.js` with Atlas-generated compiled PHP markup, Atlas assets, and the real suite PHP wrapper. Its standalone Chromium assertions cover eight 320–1920px widths × two JS modes, reversible source navigation, keyboard focus, no overflow, provenance notice, unexpected requests, JS errors, repeated screenshot bytes, and controlled page-fragment LCP/CLS. Optional axe is allowed only from a local independently SHA-verified bundle (`--axe-file` and `--axe-sha256`); lack of a bundle never reports an axe pass.

The CLI **fails with exit code 2** when the original R38 files are absent (as in a standalone R52 ZIP) rather than silently substituting a synthetic Desk. Run it from a full repository checkout (with R38 branch content) using:

```bash
python experience2/evidence-atlas/tests/browser_r53_actual_r38.py --output /private/qa-r53-real
```

These browser results, even if executed, are PHP-assembled `set_content` tests, **not actual WordPress/Assembler/hosted HTTP tests**. Genuine private WordPress should test direct shortcode, nested reusable block, dynamic block, template part, CSS loaded before first paint, actual screen-reader navigation, axe/Lighthouse, and hosted CWV. Confirm the preload constant's page ID against the private staging installation before running.

## Actual execution in this environment — November 1, 2026

- PHP lint suite adapter/probe: PASS.
- `python -m unittest discover -s tests -p 'test_*.py' -q`: **82 run, 81 pass, 1 skip** (the existing R52 exact real-R38 test requires files not in the standalone ZIP).
- `python test_atlas.py`: **11/11 PASS**.
- `node --check atlas.js`: PASS.
- Existing `tests/browser_r50_suite.py`: **16/16 PASS**, 320–1920px JS on/off, synthetic Desk + real Atlas PHP, repeatable 390/1440 screenshots. Lab component LCP 96–156ms; CLS 0. Not hosted metrics.
- NEW `tests/browser_r53_actual_r38.py`: **BLOCKED, exit 2**, because the standalone ZIP lacks the four actual R38 Desk source files. **No original-R38 browser PASS claimed.**
- Axe-core: not executed (no independently verified local bundle); authentic WordPress/Assembler, Safari/AT, hosted CI, independent QD: not executed.

NASA photograph-use decisions remain open for all six records; record-01 `S67-19766` association remains unconfirmed and explicitly disclosed. No NASA photograph bytes, invented geo pins, speculative chronology, or production artifacts have been introduced. No merge or activation authorized.

**Release decision:** HOLD. The next acceptance milestone is executing the exact real-source browser runner in a full checkout and genuine isolated WordPress/Assembler staging with direct/nested/template-block CSS first-paint measurements. Protect homepage PR #49, homepage lead branches and Research Desk PR #158.
