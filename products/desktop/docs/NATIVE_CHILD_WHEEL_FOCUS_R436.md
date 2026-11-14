# R436 — preserve native nested wheel controls and keyboard focus (DRAFT / HARD RELEASE HOLD)

**Issue:** [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). **Parent:** R435 draft [#2529](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2529), exact parent SHA `3acda23e5ce614fe94f21a654a2c4b6946e10009`; proposed change is isolated to `feature/labs-r436-native-wheel-focus-20261114`, not production `main`.

## Concrete defect and repair

The shared root-bound wheel handler applied the **form canvas** wheel action to descendants even when a child was itself a native scrollable/editor control. Depending on native Tk class bindings/platform routing, this could double-scroll the form, steal a user gesture from a child, or perturb a pending Windows precision-wheel fraction. Root-viewport checks and Shift/Ctrl/Alt exceptions alone did not distinguish the child wheel owner. This was reproduced headlessly with actual uninitialized Tk widget classes; no deployed customer incident is claimed.

- New `fvs_suite/native_wheel_owner.py` explicitly preserves control-owned gestures for classic Tk Text, Listbox, Spinbox, Scale, Scrollbar and **nested** Canvas, and ttk Treeview, Combobox, Spinbox, Scale, Scrollbar and Notebook. The form's own canvas remains form-scrollable. The helper does not call widget getters, interpret financial data, inspect file paths, or alter event state.
- `fvs_suite/scroll_access.py` calls the helper only after the existing viewport-boundary check and **before** touching modifier bits, the form yview or the Windows precision-wheel residual. Generic child labels/entries and the form canvas continue to scroll the form.
- Keyboard focus-to-visibility now also covers classic Tk Listbox, Spinbox, Checkbutton, Radiobutton, Scale plus themed Scale/Notebook, alongside the prior R435 targets. The existing same-root and descendant guard remains mandatory.

The six launchers use this shared Tk form: **LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk** (free); **GrantAudit Studio Pro, ProcureGuard Studio Pro** (premium). This sprint changes no money math, cryptographic evidence, source custody, offline processing, entitlement gates, human compliance review, payment approvals, site or distribution URLs.

## Executed local evidence (not Windows certification)

The local Linux Python **3.13.5** workspace reconstructed the **entire R435 `scroll_access.py` source** and two imported wheel guards, with Git blob SHA-1 IDs verified against GitHub (`ce75d380...`, `7d63c855...`, `4e3af832...`). The new helper, modified full module and both newly authored test files were then run; all four files' Git blob hashes match the R436 feature branch exactly.

| Test command | Results |
| --- | --- |
| `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_*r436.py'` | **20/20 PASS** |
| `PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_*r436.py'` | **20/20 PASS** |
| Python `compileall` for helper, module, tests | **PASS** |

The local directory used the same relative `fvs_suite/` and `tests/` import layout under an isolated scratch folder; on a full checkout, use `PYTHONPATH=products/desktop` as above. New tests use **real Tk classes without initializing a display**, synthetic event/widget ancestry, private-value getter traps, platform-specific delta routing, and new classic/themed focus targets. A controlled substitution of the **exact original R435 module** reproduced **21 assertion failures/subtests and one error** in the 12-method new integration test before the R436 fix; after the fix both new files passed.

**Limits:** No live Tk display, Windows native event delivery, screen reader, 400% UI scaling, full inherited repository suite, six executable builds or premium access flow were tested locally. These 40 executions are **focused headless test runs**, not six-app acceptance evidence.

## Hosted CI and required launch gates

`.github/workflows/desktop-source-evidence-r385.yml` adds R436 full-source/helper tests plus R227/R229/R230/R434/R435 inherited wheel/focus checks in normal and optimized modes across hosted Ubuntu and Windows matrices. The most recent checked R435 exact-head runs, [source #43646093212](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43646093212) and [Windows build #43646093327](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43646093327), failed with **four jobs, zero recorded steps and no assigned runner**. The infrastructure root cause remains unconfirmed; no hosted test success is asserted.

**Smallest unblock:** Repository owner checks Actions billing/spending limit, Actions policy and hosted-runner eligibility, then reruns source verification and Windows build **against the exact proposed R436 commit**, preserving logs and artifacts. After genuine CI execution, manually test actual Windows x64 scroll/focus and 400% scaling on all six programs, six-engine financial and cryptographic regressions, Defender, SHA-256/version/manifest custody and gated premium distribution. Independent QD review and explicit founder approval remain mandatory before merging/publishing.

**Release flags:** `release_authorized=false`; no merge, executable upload, public download, premium asset exposure, WordPress changes, telemetry, customer data transfer or payment authorization.
