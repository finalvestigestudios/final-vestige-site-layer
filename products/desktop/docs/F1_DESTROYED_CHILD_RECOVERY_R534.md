# Labs R534 — F1 help child-destruction recovery

**Status:** draft/source-only; independent QD and explicit founder approval are a **HARD HOLD**. Stacked on R533 draft PR #3062 at `f0094891c059aede80ebcdfd974ec64d6f1d187f`, not production `main`.

## Reproduced failure, not merely a hypothetical

An existing F1 `tk.Toplevel` can remain alive after its contained read-only `tk.Text` is destroyed by a Tk callback. In R533, every subsequent F1 raises that same window, catches the invalid child's `TclError`, and **returns without rebuilding readable help**. A direct Linux Tk 8.6/Xvfb negative control against the R533 helper produced one failed case (no replacement window) and one error (no retained original-focus reference) out of six focused cases.

## Code change — shared by all six launchers

- If the help Toplevel and its Text child are live, repeated F1 raises and focuses the same text. If Text `focus_set()` fails during a Tk race, attempt to focus the surviving dialog instead.
- If the Toplevel survives but the Text child no longer exists, destroy that empty dialog and construct a fresh scrollable, disabled/read-only text view.
- Preserve the originally focused form widget identity through recovery; do not read input contents or call Generate, Browse, Review, entitlement checks, data pipelines, or network APIs.
- Support an older dialog without a retained Text reference by focusing its window; preserve idempotent close and exception handling.
- No changes to financial engines, Decimal policy, input files, deterministic audit logs, compliance review, offline privacy, premium gates, site/catalog or workflow manifests.

## Artifacts

- `products/desktop/fvs_suite/keyboard_access.py` — live-child check, safe fallback/reconstruction, original-focus reference.
- `products/desktop/tests/test_keyboard_access_r44.py` — **nine new R534 regression methods** (five mocked headless + four real-Tk optional tests; they explicitly skip if the system has no display).
- This runbook. The existing pinned 416-command source inventory is unchanged.

## Executed local evidence (scope strictly limited)

Platform: Linux CPython 3.13.5, Tk 8.6 with Xvfb virtual display. The local executable subset contains the R533 `format_keyboard_help` and `show_keyboard_help` implementations plus the R534 change, and a six-case native Tk integration probe exercising real widgets, keyboard focus, destroyed children, repeat F1, bad legends and Escape. **6/6 PASS normal; 6/6 PASS with `python -OO`, 12 native Tk case executions.** With the R534 change removed, the same probe gives **1 FAIL and 1 ERROR out of 6**. Tests don't invoke any customer file or financial engine.

**Not yet executed:** the full committed R44 regression module (including these nine committed R534 methods), entire inherited test matrix, the 416-command verifier, native Windows 11/Narrator/NVDA at high DPI, six Windows x64 packaged binaries, actual Defender scans, SHA-256, premium entitlements, and QD approval. The Linux/Xvfb probe is not Windows acceptance or proof of release readiness.

## Next highest-impact step / blocker

Hosted GitHub Actions has been failing before any runner test steps (tracked in #75). A repository administrator should inspect GitHub Actions **billing/spending limits, runner eligibility and workflow policy**, then restore one job that actually executes a step and preserves its logs. On the exact R534 head, run:

```shell
cd products/desktop
python -m unittest discover -s tests -p test_keyboard_access_r44.py -v
python -OO -m unittest discover -s tests -p test_keyboard_access_r44.py -v
```

Then execute all 416 pinned source commands on Ubuntu and Windows; run six native Windows x64 app/shortcut/scale/reader acceptance checks, Defender scans, hashes and premium protected-distribution tests. **No merge, deployment, production QD bypass, executable publishing, or public premium download URLs.**
