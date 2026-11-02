# Labs R132 — native LedgerDiff mapping accessibility contract repair (DRAFT / RELEASE HOLD)

## Reproduced exact-head failure

R131 introduced two visible, keyboard-focusable optional CSV match-header entries in the **free** LedgerDiff Lite GUI. On its exact candidate commit `25d4e1ca857bb55ab9242f3d6cb9cbeb671c819e`, [Actions #41403913157](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41403913157) finished **failure**, not success: Linux source-tests passed, Windows completed both modes of source tests and successfully built/smoked six internal Windows x64 candidates, but Windows stopped at **R106 native Tk keyboard/focus preflight**. The R106, R107 and R108 native observers still treated LedgerDiff as having only two file entries and one output entry. That obsolete inventory rejected the new, legitimate focusable mapping controls; the following native scale/event gates were not reached.

The failure is **not** an acceptable reason to remove, disable, skip or make those two fields non-focusable. Doing so would hide accessibility regressions and weaken the source-controlled acceptance evidence.

## Code fix and intended native observations

- **R106 native keyboard:** require five LedgerDiff entries (two file inputs, two optional match-key inputs, one output), three Browse buttons and one Generate button. Require the exact visible source-owned optional labels. Enforce the complete Tab sequence: `input_1 → browse_1 → input_2 → browse_2 → ledger_left_key → ledger_right_key → output → browse_output → generate → input_1`. Continue verifying native mapping, the single first-field focus callback, fixed Alt/Ctrl key bindings, and no free-tier premium review accelerator. The other three free UIs retain their former strict control inventories.
- **R107 native 200% / 400% scaling:** require the two additional actual editable LedgerDiff controls to be mapped/focusable, while retaining the original three Browse buttons, one Generate button, scrolling, focus visibility, hint wrapping and system background requirements. No extra file picker is invented for the two optional header entries.
- **R108 native Tk shortcut events:** require five LedgerDiff entries and three Browse buttons, and require both optional mapping inputs to remain unpopulated during cancelled-file-picker probes. Count only the two required file inputs as file selections. Retain Alt+1/2 input focus, Ctrl+1/2 cancelled browsing, output focus/cancel, two blank-input Generate rejections, no engine invocations, and no premium window access.
- **Source unit fixtures:** correct R106/R107 source-owned expected inventories to match the real new UI. R131's financial engine, Decimal logic, SHA-256 input provenance, local import behavior, premium locks, and human review semantics remain unchanged.

## Test evidence and custody boundaries

[21 additional synthetic methods](../tests/test_ledger_native_access_r132.py) assert the new exact LedgerDiff Tab chain; omitted/reversed/extra stops; missing left/right labels; unchanged other-app controls; both native scale inventories; rejected Boolean counts; existing cancelled-action guards; and rejection of premium editors. [The redacted, no-skip runner](../scripts/safe_unittest_r132.py) enforces all 21 exact source-owned method names (not just a nonzero count), requires all passed with zero skips, and prints no private test exceptions or financial values.

Both Linux and Windows mandatory workflow jobs execute this gate in normal and optimized `-OO` Python. Target: **21 × 2 operating systems × 2 modes = 84 named method executions**, in addition to the full inherited suite and actual Windows R106/R107/R108 native probes. Only completed exact-commit CI can substantiate those results. R106/R107/R108 synthetic observations are **not** a human keyboard, NVDA, contrast or physical Windows 11 assessment.

This R132 branch is stacked on draft R131 #577, not on production. It must remain a **draft PR and release HOLD** until independently reviewed. No customer input, premium EXE, entitlement, signing key or download is published by this change.

## Unfinished independent release gates

A QD-authorized reviewer must privately receive the six exact Windows x64 executables and separately authenticate the R9 build pin. An actual Windows 11 workstation must complete **46 physical accessibility checks** and genuine Defender/EDR assessment (with any remediation retested). Code signing, protected premium fulfillment, QD sign-off, and founder authorization remain separate required release controls. All six utilities are **UNRELEASED**.

## Follow-up exact-commit diagnostic after first native CI run

Initial [R132 Actions #41417802839](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41417802839), commit `1af26e4c5f28418279eaf2cb4215fe12074b3b2f`, completed Ubuntu source-tests successfully (18 additional methods in two modes). Windows source and six private candidate builds/smokes completed; **R106 native keyboard passed** the updated two-key Tab contract. Windows then **failed at R107 native 200%/400% scrolling/focus**, so R108 did not run and that run is NOT green. R132 now retains the fail-closed R107 native checks while emitting only **fixed, source-owned diagnostic categories** identifying the affected free app, simulated zoom and failed check; unrecognized/Tk exception text and customer/path values are never printed. Three added synthetic tests verify diagnostic specificity and redaction, making 21 named R132 methods. No scaled-focus fix or Windows success is claimed until the new exact-head Windows diagnostic identifies the reason and any required remediation passes CI.
