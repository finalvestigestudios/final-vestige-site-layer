# R437 — nested native wheel ancestry (DRAFT / RELEASE HARD HOLD)

**Tracking:** [Final Vestige Labs #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).  
**Parent:** R436 draft [#2534](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2534), pinned at `e2c9fe07c52a84e3fb12868067a0094aa7e05ce0`.  
**Branch:** `feature/labs-r437-native-wheel-ancestry-20261114`, **never production `main`**.

## Problem and smallest production repair

R436 protected a native Tk Text, Listbox, Treeview or nested Canvas **only when that control itself was the wheel event target**. A child label, embedded editor, or nested frame *inside* such a native scrolling widget was still interpreted as a generic form child and scrolled the **outer** application canvas. On Windows this also modified or consumed the precision-wheel residual. On X11 it could hijack a native child gesture. This is a controlled synthetic reproduction, not a claimed observed customer incident.

`fvs_suite/native_wheel_owner.py` now inspects the `master` chain from the event target up to (but **never including or beyond**) the *specific form canvas*. If a native owner appears below that boundary, the outer form declines to scroll. Ordinary forms and inputs keep outer-form scrolling, the form canvas itself continues to scroll, and outside-viewport/dialog isolation remains handled by the existing `ScrollableForm._inside_viewport` gate. The implementation bounds cyclic malformed ancestry using an identity set, accesses only widget parentage/type, and uses `object.__getattribute__` so displayless Tk proxies do not invoke Tcl fallback; it reads no financial values, paths, widget text or files.

**In scope:** Shared local-first Tk shell for all six launchers: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk (free), and GrantAudit Studio Pro / ProcureGuard Studio Pro (premium). **Out of scope:** Money algorithms, compliance decisions, audit event format, premium entitlements, executables and live site.

## Reproducible local test evidence

Tests were run on **Linux Python 3.13.5** in a scratch checkout with the complete existing R436 `scroll_access.py`, `wheel_modifiers.py`, `wheel_edge_guard.py`, two R436 test files, and new R437 code/tests. All eight reconstructed Python source files with externally pinned Git blob IDs match the corresponding branch blobs (exact committed new test and helper files confirmed by connector read-back). No real Tk display was started and no user financial files were used.

| Local command | Actual result |
| --- | --- |
| `PYTHONPATH=<scratch> python -W error -m unittest discover -s <scratch>/tests -p 'test_*r43?.py' -q` | **40/40 PASS** (R436 20 + R437 20) |
| `PYTHONPATH=<scratch> python -OO -W error -m unittest discover -s <scratch>/tests -p 'test_*r43?.py' -q` | **40/40 PASS** |
| `python -m compileall -q <scratch>/fvs_suite` | **PASS** |
| Controlled source substitution: original R436 wheel helper plus new R437 tests, normal mode | **17 assertion failures and 2 errors** (expected red) |

The 20 new unittest methods contain **12 targeted unit methods + 8 real-`ScrollableForm`-method integration methods** with synthetic widget geometry/events. They test Windows precision residual preservation, X11 routing, nested native classes, ordinary-form behavior, outside-viewport protection, cyclic ancestry and sensitive-content getter traps. The original R436 test files also passed unchanged. This is strong focused source evidence, **not** full six-app, browser, genuine GUI or Windows executable certification.

## Hosted CI / release gates

`.github/workflows/desktop-source-evidence-r385.yml` adds R437 plus inherited R436 suites in standard Python and `-OO -W error`, on its existing Ubuntu/Windows matrix. At inspection, the pinned **parent R436** source run [#43650797052](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43650797052) and Windows build [#43650797029](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43650797029) were both marked **failure** with four jobs failing before any recorded steps; this is an **infrastructure/blocker observation, not evidence that tests ran or failed**. No confirmed billing/runner/policy root cause. R437 exact-head CI should be inspected separately after PR creation.

**Smallest unblock:** Owner opens repository Actions settings plus organization billing/spending-limit and hosted-runner eligibility, then reruns source/Windows build workflows on the **R437 exact commit** and preserves step logs. Next validate the six actual Windows x64 portable applications with physical wheel/focus at 100–400% scaling, NVDA/keyboard, full financial/crypto/entitlement suites, Defender, SHA-256 manifests and protected premium distribution.

**Nonnegotiable:** `release_authorized=false`. Do not merge to production, deploy, publish test executables, expose premium binaries, invent live download links, modify WordPress, or make automated compliance/payment approval. Independent QD review and explicit founder approval remain mandatory.
