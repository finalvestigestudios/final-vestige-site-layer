# Final Vestige homepage — integrated WordPress browser admission hardening
**2026-11-01 — DRAFT / HOLD. No production publication, plugin activation, CMS write, merge, or independent QD approval.**

## Exact branch lineage
- Parent: draft PR #414, `5b70b26f3d2434a3ae53a39557f0cd5e5ac932d9` (selective preservation of page 6, seven-chapter source, isolated Playground).
- This PR only changes the *staging browser admission criteria* and adds pure checker/unit-test files. Frozen v1 PR #49 remains untouched; Apollo #158 and Mind #171 remain separate.
- The before-version browser runner: `verify_playground_browser.py`, Git blob `a00dfe88a6819715d2559c590f30445759b5b5ba`.

## Source-grounded findings — why the previous browser gate could give a false release signal
1. The old runner collected but **did not verify the theme**. A standalone HTML imitation with seven chapter anchors, three cases, one H1 and one main landmark could pass its DOM checks without being an integrated WordPress/Assembler homepage.
2. It did not assert **72 retained Hidden in the Margins records**, original Focus links or absence of the obsolete hero/development toolbar. This left a gap between source-level migration tests (PR #408) and the actual rendered acceptance.
3. It checked **three media response sizes and natural dimensions**, then *recorded* SHA-256 computed from that same test response. It never compared those digests to an independent original-media manifest. The same-size altered-image class demonstrated in PR #395 was therefore still possible at this browser gate.
4. The original URL guard refused finalvestige.com itself but allowed arbitrary external hostnames and did not check redirect destination. A local preview redirecting to production could be mistaken for a safe stage.
5. If the runner failed before finishing, its success receipt was never written; the new CLI records a separate **FAILED_CLOSED** receipt for reproducible investigation.

## Corrections in this branch
- Strict isolated host allowlist: loopback, `*.localhost`, official WordPress Playground, or **one exactly named, HTTPS** externally approved stage host. No production host, subdomain, credentials, URL query or fragment. HTML and archival-media HTTP redirects must remain on the exact stage origin.
- Rendered DOM must prove **WordPress Assembler body class**, one flagship root, exactly 72 Margins DOM records, original Focus-link inventory, no obsolete hero/development controls, seven chapters, three cases, one H1/main and no root overflow; the same check executes in no-JavaScript mode.
- Browser runner now requires the **independently generated three-original media SHA-256 manifest** already specified in PR #395. Each complete first-party HTTP image response is compared with its prior trusted digest, byte length and browser-decoded dimensions. Reporting a digest from an untrusted response is no longer a pass.
- Positive results are evidence of that isolated environment **only**; they cannot establish art-rights clearance, Jetpack email delivery, hosted WordPress.com differences, Safari/assistive-technology parity or field Core Web Vitals.
- Failure writes `PLAYGROUND_ADMISSION_FAILURE.json` with stage host and reason; no production database, subscriber or credentials are stored.

## Verification performed
- Ten independent standard-library Python unit tests covering isolated URLs, named-host restrictions, production refusal, integrated DOM inventory, malformed/missing media manifests, and a **same-byte-count image alteration**. **10/10 passed** in the author's local scratch-source equivalent.
- Source fetch from the actual GitHub branch reverified three changed files and their Git blob identities: `integrated_admission_checks.py`, `test_integrated_admission_checks.py`, `verify_playground_browser.py`.
- The committed script wiring was checked read-only for the integrated and media gates, redirect rejection and closed-receipt path. **GitHub Actions and exact remote full-checkout execution are not claimed as passing.**
- Attempted genuine local Chromium HTTP navigation to `127.0.0.1:8765` returned `net::ERR_BLOCKED_BY_ADMINISTRATOR`. External archive/theme fetch remains unavailable in this environment. **No real WordPress installation, image-transfer run, axe audit or Lighthouse results are claimed.**

## Exact checkout reproduction
```bash
python -m unittest discover -s experience2/home-flagship/qa/playground -p 'test_integrated_admission_checks.py' -v
python experience2/home-flagship/qa/playground/verify_playground_browser.py \
  --url http://127.0.0.1:8080/ \
  --trusted-media-manifest /private/independently-reviewed-media.json \
  --axe-js /private/verified-axe-core.js \
  --output-dir /private/fv-playground-admission
```
The above browser command must run **only after** a working, isolated WordPress/Assembler host has been launched using the guarded PR #414 integrated Blueprint and authentic original media. Missing verified originals, theme or axe must **fail closed**, not be worked around using random pictures, invented SHA values or a published WordPress site.

## Remaining release blockers
Real integrated WordPress/Assembler staging; licensed first-party image originals and transfer hashes; seven-width Chromium and human visual review; keyboard/touch/200% zoom/reduced motion/no JS; axe WCAG 2.2 AA plus manual review; measured Lighthouse/CWV; actual Jetpack subscription and Focus fulfillment on a non-production host; exact-head independent QD and CI; founder art-direction choice and explicit release authorization.

**HOLD. Do not publish or deploy.**