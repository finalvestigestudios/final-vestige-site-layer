# Apollo Experience 2.0 — R401 source-custody acceptance integration (DRAFT / HARD HOLD)

## What changed
R400's opt-in installed-staging browser runner checked six source-card/link counts and three chronology anchors, but **did not call** the earlier substantive R392 NASA claim/limitation validator, R393 chronology topology validator, or R394 visibility/keyboard-availability validator. Thus a page with unchanged counts but altered NASA claim, rights disclosure, source role, chronology phase, or hidden free CTA could pass R400's structural check. R401 restores those previously reviewed validators **inside every R400 browser context**, retaining R400 network admission and axe/CSP/CSS restrictions. No changes to the R400 implementation, existing gallery, homepage PR #49, Research Desk PR #158, Claude engineering, or Grok/Praxxis TASK-008.

`qa/custody_overlay.py` is an isolated process-local wrapper. It checks Git blob IDs for R377 source custody and R392, R393, R394 and R400 code, then adds the exact semantic/topology/visibility checks. It fails closed in installed-staging mode for any changed or absent upstream source. It does not install a plugin, navigate external NASA links, write WordPress, change analytics, add commerce, or authorize deployment.

## Reproducible local QA

```sh
python -m unittest discover -s experience2/apollo-r401/qa -p 'test_*.py' -v
php experience2/apollo-r384/qa/contract.php
python experience2/apollo-r401/qa/custody_overlay.py \
  --fixture experience2/apollo-r384/QA/local-php-fixture.html \
  --out experience2/apollo-r401/QA
python experience2/apollo-r401/qa/pack_evidence.py
```

The PHP command creates an *offline fixture* from the reviewed R384 shortcode candidate. It is not WordPress installation. The Python unit suite also generates this fixture automatically if missing. R401's 10 red-team mutations were chosen to pass the R400 structural inspector while failing R401's evidence and accessibility checks. The integrated fixture runner covers seven Chromium contexts including 320–1920px, touch, no-JS and reduced motion; other inherited R384 QA covers forced colors, root-text enlargement, CDP roles, PDF and local LCP/CLS. R401's checks do not replace genuine axe-core, actual staging HTML/CSP/stylesheet network QA, independent screen readers, native browser 400% zoom or production p75 CWV.

### Exact dependency distinction
The locally available archival R392 and R400 test copies differ from the currently committed GitHub source, so this run returns `PASS_LOCAL_FIXTURE_SHADOW_DEPENDENCY_ONLY` rather than pretending to test the exact remote parent code. The R401 wrapper and tests are committed byte-for-byte; they are **not** a byte-identical execution of R392/R400 remote dependencies. In installed-staging mode R401 **requires the exact reviewed Git blob IDs** and will HOLD otherwise. Hosted exact-HEAD CI and real staging remain outstanding.

## Evidence and one optional conversion bridge
Apollo 1 evidence remains six historical questions supported by two underlying NASA publications: the 1967 Apollo 204 Review Board and NASA's retrospective of **102 deliberate tests conducted after the fire**, never presented as the original ignition source. No NASA photographs, logos, speculative Atlas map pins or invented relationships are included. Rights and non-endorsement disclosures remain required.

Proposed, not launched: approved Grok Apollo film + unique asset ID/approved UTM → NASA-source-backed gallery → **one** nonintrusive [existing free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) CTA → future paid educator kit only after rights, product, checkout, fulfillment and founder approval are verified. Grok produces/posts, Praxxis handles creator QA, Claude owns commerce/analytics, founder approves releases. No attributed paid orders, refunds, settlement fees or qualified 7/30-day cohorts are verified. Revenue per 1,000 qualified human sessions is therefore **not computable**.

## Release governance
**DRAFT / PRODUCTION HARD HOLD.** Installed WordPress/Assembler staging with real HTTPS/CSP, actual reviewed CSS delivery, genuine pinned axe-core, independent screen readers and native zoom, exact-head CI, independent QD and founder release approval are all still required. No merge, deployment, WordPress content/settings changes, affiliate activation, social posting, emailing, analytics installation, or spending.

Coordination: [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter #818, parent R400 draft PR #2711.
