# Apollo WordPress staging bridge — independent run #7 QA record

**Source baseline:** PR #215 commit `74375657f2cdaac0710f94c6de6c24534ee06858`. **Change type:** new standalone sibling `experience2/apollo-wp-bridge/` only. **Published change:** none.

## Evidence from this actual run

- PHP CLI syntax: pass (plugin + mock harness).
- WordPress-function-mock shortcode: pass, unique instance, export URL substitution.
- Source pin: 12 verified expected Git blob hashes are declared; local archived fixture: exactly 4 mismatches to GitHub baseline and default build correctly refuses.
- Deterministic local fixture build: pass, seven outputs + manifest, two runs with identical SHA256.
- File tampering: pass; PHP rejects an edited `apollo.js` even with an otherwise trusted temporary fixture.
- Real installed Chromium / Playwright: pass at 320/360/390/768/1024/1440/1920 in a **local in-memory rendered fixture** (NOT WordPress server), six evidence/response/trail/Atlas records present, native details and focus/deep-links work, no horizontal overflow, no JavaScript available fallback, reduced-motion and 200% zoom reflow.
- Accessibility: Chrome AX tree inspected; no unnamed button/combobox found in tested views. **Axe NOT RUN**.
- Observed in-memory CLS 0 per checked width; LCP no browser event => **not measured**. Field CWV not available.
- Chromium network navigation to even `http://127.0.0.1` and `file://` rejected by sandbox administrator, so **HTTP path/CSP/MIME and actual hosted asset loading are untested**. No screenshots or perf claims from a real WordPress host.

## Release blocker matrix

**Blockers:** exact GitHub-built shortcode package test, real WordPress staging installation/routing/Assembler compatibility, axe-core WCAG 2.2 AA with pinned local bundle, real HTTP and CSP, verified original NASA photograph rights if any eventually reproduced, iOS Safari/VoiceOver and NVDA, true LCP/INP/CLS and independent QD/hosted CI, explicit founder release authorization.

**Safety:** no guessed coordinates/pins, source-page links only, no new NASA image bytes, no WP/plugin activation or content changes, no changes to homepage PR #49 or Research Desk PR #158. Historical witness evidence must not be construed as final completed engineering certification.

## Further action

First run the builder without overrides on this PR's exact source and record artifact SHA256. Deploy the produced ZIP to **disposable WordPress staging only with approved credentials and review**; verify CSS specificity, asset handling in dynamic/reusable blocks, CSV/JSON download routes, run pinned real axe-core at seven widths and full screen-reader and CWV QA. Independently report pass/fail before any governed release.
