# Apollo Experience 2.0 — R215: link custody and script-free staging

**DRAFT / STAGING ONLY. No production changes, WP installs, paid CTAs, or content publication.** Governing issues: #150, #820 and founder charter #818. Stack solely on R214 PR #1584; homepage PR #49, homepage branches and Research Desk PR #158 remain untouched.

## Material staging change

R214 blocked optional campaign-handoff.js from loading; the JavaScript file and dead PHP enqueue function nevertheless remained in the generated staging distribution. R215 omits both entirely and keeps the NASA evidence HTML and scoped CSS byte-identical. It does not enable attribution or track users. The sole external reading action remains the FREE original Apollo 1 investigation, with no URL mutation. No new NASA media, invented map pins, tracking scripts, paid services or merchant links.

Before writing child outputs, build_r215.py checks SHA-256 of R214's manifest AND every parent file; NASA and rights evidence URLs; one free CTA; four chronology dates; unique HTML IDs, ARIA targets and fragment targets; allowed outbound hosts; and negative commercial/production flags. Duplicate HTML attributes, unsafe URL schemes, unknown domains, scripts, unreviewed images or geo coordinates hard-fail the build. The build emits a machine-readable link-custody receipt and denies release, creator attribution and commerce.

## Exact reproducibility

Parent R214 generated manifest SHA-256:
f4fb5bcea55c222a25e46b173c4ce273d88c523ed6f0bb82178203f0786465b3

Locally tested R215 generated manifest SHA-256:
24de2b0adf1169a6c3b91873468d3af2be8216bb945ee0be8a3a24fb26d51033

Commands (from repo root, with the verified R214 dist supplied):

    FV_APOLLO_R214_DIST=/absolute/path/to/r214/dist python experience2/apollo-r215/build_r215.py
    python experience2/apollo-r215/qa/gate_r215.py /tmp/apollo-r215-run-A
    python experience2/apollo-r215/qa/gate_r215.py /tmp/apollo-r215-run-B
    python experience2/apollo-r215/qa/perf_fixture_r215.py

**Executed locally:** PHP lint; normal/printed/late fail-open; absence of campaign JS; native details and one free reading link; two Chromium 144/Playwright runs with 11 contexts each, widths 320–1920, keyboard, touch, JS disabled, reduced motion, forced colors and CSS-simulated zoom; print answer-guide visibility; 11/11 identical screenshot digests between runs; ten unsafe HTML/link mutations plus six corrupted parent artifacts rejected. Real Chromium PerformanceObserver was also run on offline set_content fixtures at six viewport widths, NOT field CWV.

**Not executed/verified:** genuine axe-core, NVDA/VoiceOver, installed WordPress/Assembler/Jetpack, external URL browser navigation, actual browser zoom, hosted exact-head CI, independent QD, rights for promotional imagery, verified commercial offer or founder release approval. Chromium navigation to localhost/file URLs was blocked; local browser tests used PHP-rendered fixture HTML. The inherited canonical R198 source discrepancy is **unresolved**.

Historical custody: NASA Apollo 204 Review Board, https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — most probable electrical arc, but no conclusively identified ignition source. Separate NASA advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — no implied endorsement, image/logo/likeness commercial permissions not granted by historical citation alone.

## Conversion-first decision

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Hypothetical Apollo educator dossier (NOT sellable) | Original investigation → paid product | No approved SKU, rights, checkout or fulfillment | Validate product and actual merchant rights before any CTA | HARD HOLD | Commerce / Claude / Founder |
| Grok Apollo documentary (published asset unverified) | Social → Atlas | No verified immutable asset ID, post URL or Praxxis QA | Omit all campaign JS, keep attribution denied | LOCAL PHP/Chromium PASS; real creator campaign UNVERIFIED | Grok / Praxxis / Apollo / Claude |
| Free Apollo investigation | NASA evidence → original article | Link manipulation/ARIA drift risk | Strict build-time source, link and chronology gates | 10/10 semantic mutants and 11×2 browser contexts PASS | Apollo |
| Confirmed customer | Human qualified session → paid order → net revenue | No authenticated qualified sessions, orders, fees or refunds | 7/30-day cohort reconciliation only when actual records exist | Net revenue / 1,000 qualified sessions NOT COMPUTABLE, not zero | Analytics / Commerce |

**RELEASE: STAGING HOLD.** Grok owns videos/Shorts/social distribution; Praxxis independently reviews; Claude owns production analytics/commerce; founder authorizes launch. The proposed route remains Grok documentary → evidence Atlas → one free investigation → a future rights-cleared, original educator dossier ONLY IF approved and actually purchasable. Do not attach unrelated affiliate offers to Apollo 1 tragedy coverage. No live publishing, social posting, email, WP writes, spending or sales claims.
