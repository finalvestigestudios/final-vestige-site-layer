# R106 — Native Tk focus/traversal preflight for four free desktop applications

**2026-11-01 UTC · draft/release HOLD · tracks #73.** Stacked only on R105 PR #428 at exact parent commit f375fc7f734ad3b430fe4c5b527499f07bd98a71, not production main.

## Gap and engineering response

R105 verified six real Windows x64 portable EXE candidates, PE/SHA256 and command-line smokes; launching actual EXEs showed four distinct free Tk windows and two premium lock dialogs ([Actions #41289376447](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41289376447)). A visible window does **not** prove keyboard focus order, working accelerators, Windows accessibility, or screen-reader support.

This draft adds scripts/native_keyboard_probe_r106.py, using **the real free-app fvs_suite.app.run() Tk widget construction** on a native Windows x64 QA runner. It intercepts only Tk.mainloop to inspect the mapped UI without loading private financial documents or generating reports. File dialogs and report-generation commands are replaced by fail-closed deny callbacks; premium apps are never instantiated, and no production public keys or licenses are changed. Every UI root is torn down.

The native verification demands, per free app:

1. Exact expected main-window identity; expected count of entry, Browse and Generate widgets; required controls mapped.
2. Real Tcl/Tk tk_focusNext() traverses **every** entry, Browse, output and Generate in source-owned order, and returns to the first field without a trap, a skip, or an unexpected additional focus target.
3. The first input actually receives focus after the app's idle-focus setup (on an active native Windows desktop).
4. Actual registered root binding scripts exist for Alt+1..N, Ctrl+1..N, Alt+O, Ctrl+O, Alt+G and Ctrl+Enter. The free windows do not register the premium review accelerator.
5. Required visible field labels, keyboard-help text and the non-determination disclaimer remain present.

Source-only tests/test_native_keyboard_probe_r106.py includes **25 adversarial regression methods** for missing/reordered/duplicated traversal, wrong window identities or field counts, focus failures, missing shortcuts, leaked premium review binding, label/disclaimer loss and invalid CLI arguments. Tests run under normal and optimized Python on Linux and Windows *before* the mandatory source gate; the existing full suite also discovers them. The separate native Windows step follows R9/R105. None of the upload-artifact paths or premium entitlements changed; fail-closed CI failure remains nonoptional.

## How to verify privately

From a full trusted checkout at the exact PR head:

~~~powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p test_native_keyboard_probe_r106.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_native_keyboard_probe_r106.py -v
python products/desktop/scripts/offline_source_gate.py
# Only on a native Windows x64 QA desktop with a functioning Tk foreground:
python products/desktop/scripts/native_keyboard_probe_r106.py
~~~

The native test prints **only** fixed source-owned PASS/BLOCKED labels. It produces no screenshot, user path, customer value, audit report, license or executable artifact. A Linux terminal or unavailable graphical session must produce a blocking result; it is not silently skipped. The 25 synthetic tests can run without a Tk display.

## What this deliberately does NOT certify

The native probe introspects Tk focus traversal and installed bindings in **source-created** UIs. It does not press actual keyboard keys into the *packaged* EXEs. It does not exercise OS-native file pickers, the two locked premium interfaces, UI Automation/MSAA accessibility names, NVDA/JAWS/VoiceOver announcements, high-contrast color readability, 200%/400% reflow, Windows 11 specifically, or physical keyboard latency. R105 separately tests the actual packaged GUIs. Automated traversal is only one bounded component of keyboard accessibility; **do not claim WCAG 2.2 AA or screen-reader conformance.**

Required manual release matrix on a **trusted Windows 11 x64 VM** with exact SHA-pinned candidates: press Tab/Shift+Tab and shortcuts in each of four free GUIs, open/cancel native file pickers without modifying source files, verify visible focus ring and logical labels via NVDA, exercise Windows high contrast and 200%/400% text scaling, confirm every premium editor stays entitlement locked, and confirm no unintentional output/network traffic. Record OS/build, display scaling, exact EXE SHA256, test user with non-sensitive fixture data, and independent reviewer. An actual screen-reader operator must review speech output. Missing test equipment or an inaccessible foreground window is a **HOLD**, not a waiver.

Still additionally required: independent AV/EDR and installer signing/SmartScreen plan; licensed premium **authenticated restricted distribution and issuance**; QD exact-head code/security review; founder approval before any merge/public release. Nothing in R106 changes financial algorithms, Decimal custody, deterministic audit trails, human review, website, artifact uploads, premium access, or public availability. **All six applications remain UNRELEASED.**
