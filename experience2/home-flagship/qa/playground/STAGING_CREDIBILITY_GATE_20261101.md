# Integrated staging credibility gate — November 1, 2026

**DRAFT / RELEASE HOLD.** Stacked on PR #445 exact `8658d4c60312b73129545b7b5ffe548a975e00a3`. Frozen PR #49 and production WordPress page 6 are untouched.

## Real vulnerability reproduced in previous exact source

The original `check_runner()` accepted any local file named `verify_playground_browser.py` if it merely contained four static textual markers. A controlled three-line file consisting of comments and `print("FORGED_PASS")` passed as a supposed authentic browser harness. Combined with an exit status of zero, this could support an unjustified WordPress/axe/image acceptance claim. This is a **test-runner trust defect**, not evidence that the public site was altered. Other acceptance gaps: readiness accepted any HTTP 200 on an occupied loopback port, Lighthouse output accepted an empty/invalid metrics object, and repeat executions silently retained an earlier run's receipt without writing a new report.

## Source corrections

- `--browser-runner-sha256` is **required** and compared with the exact browser-runner bytes, in addition to the previous static sanity markers. Obtain the expected digest independently from the approved checkout; do not derive it unquestioningly from an unreviewed replacement.
- `--execute` now verifies the real non-symlink Playground CLI and Lighthouse executable against separately reviewed `--playground-cli-sha256` and `--lighthouse-cli-sha256`. No runtime download or dependency substitution.
- Before launch, reject occupied/unavailable localhost ports; fail immediately when the spawned Playground process exits before readiness. There remains a theoretical bind race, so this is not a substitute for the actual WordPress DOM/Assembler gate.
- Require a complete Lighthouse report, exact requested/final isolated-stage URL, no runtime error, finite LCP, CLS, TBT and performance score. Report mobile and desktop LCP <= 2500 ms and CLS <= 0.10 as **lab** budgets, never field p75 CWV.
- Generate a different private mode-0600, append-only JSON receipt every run. Stale success/failure receipts are never reused or replaced.

## Verification and limits

The initial exact PR #445 suite passed **15/15**. The corrected source and nine additional adversarial regression tests passed **24/24** in the local PHP/Python-capable workspace. Baseline fake-runner acceptance was independently reproduced. The committed Git blob hashes match the byte-for-byte locally tested files. These are **offline source/fixture checks**, not actual WordPress or Lighthouse execution.

Local developer command now additionally requires:

```text
--browser-runner-sha256 <INDEPENDENTLY_APPROVED_SHA256>
--execute
--playground-cli <RESOLVED_REAL_EXECUTABLE>
--playground-cli-sha256 <INDEPENDENTLY_APPROVED_SHA256>
--lighthouse-cli <RESOLVED_REAL_EXECUTABLE>
--lighthouse-cli-sha256 <INDEPENDENTLY_APPROVED_SHA256>
```

The existing Blueprint, axe-js, media manifest and private directory flags remain mandatory. Never include WordPress production users, subscribers, secrets, private database, settings or unreviewed asset files.

## Open gates

The current environment lacks official WordPress/Playground runtime, Assembler theme package and independently verified three archival originals; outbound source DNS cannot resolve. Therefore **no actual WordPress integration, first-party image-byte transfer, WCAG/axe pass, Lighthouse result, hosted Jetpack behavior or source-media rights clearance is claimed**. An isolated local Playground is not WordPress.com Atomic. Before release, execute the complete integrated Gutenberg seven-chapter candidate, confirm the actual 72 Margins records, native Jetpack block and two Focus links, test seven widths/200% zoom/keyboard/touch/no-JS/reduced motion, source-verify Apollo/Franklin/NYPL image binaries and rights, collect real axe/Lighthouse evidence, then require independent exact-SHA QD and CI and founder approval. No production writes, deployment, merge or new subscription.
