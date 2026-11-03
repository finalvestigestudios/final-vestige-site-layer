# EX2 / WordPress Playground draft-cleanup failure gate — RELEASE HOLD

**Independent regression review, 2026-11-03.** Isolated companion stacked on PR #801 exact parent `0917de876959a9b5cebb638b98606fda9b94eb24`, which itself stacks on PR #793. The published site, frozen PR #49 and Apollo #158 are **not changed**.

## Confirmed defect and consequence

The original isolated WordPress core probe invoked `fv_ex2_probe_fail()` from inside its `try`/`catch` after creating a draft. That helper calls PHP `exit`. In PHP, `exit` bypasses `finally`; the intended `wp_delete_post()` therefore never executes for a failed raw readback or a caught exception. A disposable Playground site could retain an unexpected synthetic draft even though the script reported failure. The fixture is synthetic, but leaving unreviewed drafts violates the project's fail-closed staging policy.

The fix replaces post-insert exits with exceptions, runs cleanup for all successfully created draft IDs before emitting any PASS/FAIL receipt, and checks that `wp_delete_post()` succeeded **and** `get_post()` cannot find the draft afterward. A cleanup failure downgrades any otherwise successful result to **FAIL**. Pre-insert host and synthetic-marker rejection remain untouched.

## Independently executed offline evidence

On 2026-11-03, a local PHP 8.4 syntax check and nine Python/PHP synthetic fault-injection cases passed. Cases cover successful save/remove, exception after insertion, null readback after insertion, altered raw readback, false deletion, thrown deletion, failed insertion, production-host refusal and missing synthetic-marker refusal. The harness uses **mock WordPress functions only**, not a live WordPress database; tests assert attempted deletion and observable residual draft state. PHP itself confirmed that `exit` inside `catch` does not execute `finally`.

Reproduction after checkout:

```bash
php -l experience2/home-flagship/qa/release-candidate/playground_core_save_readback.php
python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_probe_cleanup.py -v
```

The existing Playground CI now runs this regression suite **before** its real WP core persistence check. Its exact-head execution remains a separate gate: do not assert real WordPress save/readback, Assembler render, Gutenberg browser editor, WCAG, or CI PASS from the mock results.

## Release decision

**HOLD.** An isolated WP core integration still requires a genuine CI runner, and saved Gutenberg editor readback plus complete browser/axe/no-JS/zoom/rights/manual QD and founder approval remain outstanding. GitHub Actions jobs were observed failing before a single test step at parent PR #801 commit `0917de8`; this branch cannot claim CI pass until steps actually execute. No WordPress.com site writes, migrations, staging upgrade, plugins, credentials, subscriber data or production exports are introduced. No merging or deployment authorized.
