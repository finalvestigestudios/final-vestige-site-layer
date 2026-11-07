# EX2 local WordPress Playground — admission before mutation (2026-11-07)
**Status: DRAFT / RELEASE HOLD.** Parent #1386 HEAD `17dcea5dcc9098fa40b88dcc500499b4ace850b8`. Frozen PR #49 and production WordPress Page 6 are untouched.

## Found release-safety defect
The parent CLI Blueprint's first step was `installTheme` (Assembler), followed by writeFile MU-plugin installs and a `runPHP` that sets `show_on_front=page` and `page_on_front`. Its marker and "never install on production" label were not guards preventing accidental replay against a non-local WordPress installation. A packaging error or misplaced launcher could therefore mutate the wrong site before the review-only marker was ever checked.

## Change: fail-closed admission **before installTheme**
- Builder verifies the **exact original source Blueprint** SHA-256 `300c79f7936d7fdf58294bb96e7b0cd1ebc0b349cdf4d2c4d13e5ec52000b23f`, reviewer SHA `a58e144fd8e9e584681b7edceb667a4a5b0ca303e49b6902299b941d0a95a9fc`, and pinned Assembler commit `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f`.
- Prepends a **read-only** `runPHP` step that checks `home_url()` host; permits exactly localhost/127.0.0.1/[::1]/subdomains of .localhost, and refuses external/public domains, deceptive suffixes, and an explicitly defined `WP_ENVIRONMENT_TYPE=production`.
- The preflight occurs before any theme installation or options write. After it, original six Blueprint steps are preserved **in their original order and byte-for-byte content** after reversing the bundled resource extraction. This is intentionally a seven-step bundle: unlike the parent, it changes admission behavior, never claims a completely identical runtime.
- No new WordPress production data, plugin or analytics is installed; original review PHP source and archival assets remain unchanged.

## Actual local evidence
- The exact parent PR #1379 three-file review ZIP was re-packaged.
- Six Python regression methods PASS, including deterministic bundle, mutation rejection, exact ordered source-step equality and a real PHP CLI host safety matrix with **10 cases**: 4 approved loopback variants and 6 refused external/production variants (test uses WordPress function *stubs*, not a real WordPress runtime).
- Generated local Blueprint ZIP SHA-256: `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`.
- The first `runPHP` admits only local dev URLs. A production domain is refused **before** installTheme; code only executes when somebody runs this local developer bundle.

## Remaining release gates
**Genuine WordPress runtime remains untested.** This environment cannot resolve npm/Playground/GitHub hosts to start the CLI or retrieve Assembler. Local PHP guard tests are not proof of WordPress execution. Real WordPress/Assembler start, first-party image transfer bytes vs CDN comparison, independent axe/WCAG 2.2 AA, keyboard/no-JS/touch/200% zoom, Lighthouse/CWV lab data, Jetpack signup confirmation and any real paid conversion remain unverified. Isolated Playground does not certify WordPress.com Atomic. GitHub CI/QD and founder preview/release authorization outstanding.

## Conversion priority and source/rights custody
Existing 7 chapters / 72 Hidden in the Margins / 5 Focus destinations preserved, no new CTA overlay or merchant claims. Apollo 1 WordPress media #473 (NASA S67-19766; 78,346-byte metadata) and Franklin #474 (1869 reproduction of the 1847/1848 note; 466,043-byte metadata) stay unchanged. WordPress reports CDN derivatives as virtual; bytes have **not** been downloaded in this sprint. NYPL #1258 remains outside the candidate while rights are pending.

**Offer → step → blocker → change → pass/fail → owner:** Free 52-page Focus Fieldbook → visitor's evidence-to-lead journey → unsafe accidental staging/production confusion → read-only first-step local admission → 6/6 offline methods PASS, genuine WP FAIL/NOT RUN → interim homepage engineering + independent QA; Claude owns commercial measurement, Grok/Praxxis own acquisition. No confirmed new leads, orders or net revenue. No production change, merge, deployment or spending.
