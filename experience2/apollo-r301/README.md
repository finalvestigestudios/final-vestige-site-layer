# Apollo Evidence Atlas R301 — consent-neutral editorial continuation contract

**Staging-only / HARD HOLD.** Isolated child of Apollo R300 draft PR #2139 (not homepage PR #49 or Research Desk PR #158). Coordination [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). No deployment, WordPress writes, Grok post, analytics activation, merchant action, email, or cost.

## Actual change

The PHP component identifies its source-evidence scope with `data-fv-experience="apollo-1"`, `data-fv-funnel-scope="editorial-evidence"` and its **single** historical next action with `data-fv-funnel-step="evidence-to-investigation"`, `data-fv-cta="apollo-read-free-investigation"`, `data-fv-conversion-kind="editorial-continuation"`. This preserves the exact existing free article URL and visible text. Attributes are inert metadata, **not instrumentation**: they do not transmit anything, store an ID, track users, imply a purchase, or claim a completed lead. Claude owns any separately authorized event/consent integration; do not duplicate scripts or forward unverified UTM IDs. Attributed paid orders and net revenue are **NOT COMPUTABLE**.

## Reproducible acceptance

From an extracted R301 archive, without any other repository checkout, run:

```bash
php -l experience2/apollo-r281/apollo-source-experience.php
python experience2/apollo-r301/qa/source_controlled_browser_gate.py
```

With system PHP, Chromium, Python and Playwright installed, the source-controlled test renders the **actual PHP** twice in 10 contexts (320/390/768/1440/1920 × JS on/off). It asserts one on-site free investigation CTA per component, the unchanged destination, no scripts/forms, 12+ NASA source links per component, distinct CDP accessible-region names, native keyboard source disclosure and fragment focus, no duplicate IDs or horizontal overflow. It exercises an intentionally corrupted paid-order metadata negative control. This check stands alone: its PHP fixture is **included in this archive and GitHub**, fixing the prior R300 evidence ZIP's missing `apollo-r294/qa/local_http_fixture.php` dependency. No standalone WordPress or axe audit is claimed.

An extended, independent local Chromium script additionally checked 10/10 contexts, 20/20 CTA contracts, 40 keyboard operations, 20 source-focus routes, 20 policy negative controls, CSS-fail-open, and produced five reproducible full-page screenshots plus a normalized printable 13-page PDF with 70 annotations. The extended script and performance timings are local QA, **not** claimed as GitHub source-controlled. The fixed manifest and ZIP may be rebuilt twice and checked by SHA-256. Offline PerformanceObserver data are lab diagnostics, not field LCP/CLS/INP.

## Historical and commercial source boundaries

The original [NASA Board narrative](https://www.nasa.gov/history/Apollo204/narr.html) distinguishes January 27 oral authority from January 28 convening; [proceedings](https://www.nasa.gov/history/Apollo204/proceed.html) record January 31 receipt of a memorandum dated January 28; the [archived memorandum](https://www.nasa.gov/history/Apollo204/15.html) is a related Board record, not independent eyewitness corroboration. [NASA's brand guidance](https://www.nasa.gov/nasa-brand-center/) bars misleading endorsements and restricts promotional use of protected marks. No source text, links, rights inference, NASA imagery, geo pins, or promotional claims changed in R301.

**One proposed pathway:** authenticate an already published Grok Apollo `asset_id` and permitted mobile URL → Atlas / inspect NASA sources → free Apollo investigation → separately approved rights-cleared Apollo-relevant offer. No approved payable Apollo product or authenticated creator asset has been evidenced, so no paid CTA was added. One relevant CTA is retained, not an endless attention loop. 7/30-day commercial reporting requires qualified-human sessions, leads (if applicable), verified settlement, fees and refunds; **net realized revenue per 1,000 sessions cannot currently be calculated**.

**Release HARD HOLD:** genuine axe-core, independent NVDA/VoiceOver, installed WordPress/Assembler/synced blocks, native Chromium HTTP/CSP, field p75 LCP/CLS/INP, exact-head hosted CI, NASA editorial/rights, independent QD and founder authorization.
