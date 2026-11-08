# EX2 Page 6 exact-delta release admission — 2026-11-08

**Status: REVIEW ONLY / RELEASE HOLD.** This is a read-only, source-controlled correction for the *commercial and editorial safety blindspot* in draft PR #1587. It adds no page, chapter, artwork, affiliate link, analytics script, subscription service, WP write, deployment, or spend.

## Exact source custody and coordination
- Base: PR #1587 branch `qa/ex2-no-loss-wp-assembly-20261108`, exact base commit `c991f5f5a7288a81ce4b24ed7cb5ebf2b3abdc4d`.
- Frozen PR #49: `10495883299d53596992c26a8987f629b2904670`, **untouched**.
- Read-only WordPress `wpcom_user_sites(environment='all')`: production only, site `256784396` (WordPress.com Personal; native staging clone not available).
- Authenticated WordPress page 6, `context=edit`: published, modified `2026-11-05T12:07:24`, **150,710 raw characters**.
- Authenticated Focus page 1579: published, modified `2026-11-05T17:44:02`; existing Jetpack list and Fieldbook preserved.
- Existing `atomic_page6_review.cjs` pins Page 6 SHA-256 `1188d32a101896f12af9823dd7ca4b8a12b0c36684e82c069f23855a698e5669`; actual SHA verified in earlier sprint, **not independently recalculated by the V8 test adapter during this sprint**.
- Issue #150 homepage flagship and #820 conversion contract are controlling; Apollo #158 R&D and Mind #171 remain independent. Existing PR #1587 was inspected; no overlapping code modified.

## Actual blocker reproduced
The prior no-loss gate correctly preserves 72 Margins, seven chapter anchors, one chapter nav, one Jetpack block, four existing images and Focus destinations, but it compares only these counts and selected texts. **It accepted a source with an unapproved third-party tracking script, a merchant URL, removed commission disclosure, or unsupported brain claim**, while reporting `STRUCTURAL_PASS_RELEASE_HOLD`. This makes that gate inadequate as the final content-change admission.

A source derived from current authenticated WordPress Page 6 plus the five exact reviewed changes passed the existing structural gate. Then **11 of 15 deliberate invalid variants also passed the old structural gate**, despite changes outside the reviewed scope.

## Change
New `experience2/review/ex2_homepage_exact_delta_gate.cjs` composes two existing, independently reviewed gates:
1. `atomic_page6_review.cjs`: verifies IDs/status/modified timestamps, pinned Page 6 SHA-256, Focus source expectations, five intended reversible substitutions, and baseline inventories. It generates the only expected candidate.
2. `ex2_homepage_no_loss_gate.cjs`: independently confirms lossless Gutenberg/Jetpack/archive preservation.
3. **Exact UTF-8 equality** between the candidate and the expected five-edit candidate: even a single extra space fails. An unapproved script, unsupported merchant claim or altered legal disclosure cannot be admitted by preserved counts alone.

The successful result is **`EXACT_DELTA_PASS_RELEASE_HOLD`**, explicitly *not* release approval. CLI only reads three PRIVATE files and prints a redacted inventory receipt, never private source contents; no browser/network/WordPress calls. The optional injected `hashFn` is restricted to controlled synthetic tests; the CLI uses the native Node SHA-256 path.

## Evidence — actual WordPress source and protected candidate
- Exact GitHub file re-fetched and evaluated in isolated V8 with the existing source modules and authenticated current Page 6 + Focus, without placing full editor content in GitHub.
- Source-aware in-memory candidate: **150,877 characters** after five preapproved changes; old 150,710 characters. All 72 Margins, seven chapters, one native Jetpack block and four images preserved.
- **16/16** actual-source V8 cases: one expected candidate admitted for offline review; **15/15** invalid changes rejected. Prior structural gate incorrectly admitted **11** of the 15 invalid variants.
- Separate exact GitHub-fetched **source-controlled Node-compatible test file** executed under a V8 `node:test` adapter: **21/21 assertions passed** (test runtime is V8, not genuine Node CLI; native Node CI pending).
- No real browser screenshot, WordPress/Assembler staging execution, actual image response bytes, axe/WCAG 2.2 AA, or Lighthouse/CWV measurement was produced by this code-integrity sprint. **None is claimed.**

## Media / rights
Authenticated WP media read: NASA Apollo #473 (reported 78,346 bytes, 1041×810; NASA S67-19766 caption), Franklin #474 (466,043 bytes, 960×1526; public-domain-marked Commons 1869 printed reproduction), edited NYPL #1258 (5,553,669 bytes, 5667×3831; caption says U.S. public domain). These are **metadata, not transferred bytes or independent rights validation**. Exact mapping and modification rights for edited NYPL derivative remain unreconciled. No media changed.

## Commercial acceptance
**Offer → funnel step → blocker → change → evidence → owner:** Existing free 52-page Focus Fieldbook → historical homepage to /focus/ to a legitimately confirmed Jetpack lead, then independently confirmed paid purchase → structural-only gate allowed undisclosed merchant/script/copy edits → strict five-edit equality and source preservation → 16/16 authenticated-source V8 exercises, 21/21 source-controlled V8 adapter assertions → interim homepage engineer + independent Site QA; Claude retains production attribution, Jetpack, commerce; Grok/Praxxis retain social production and distribution.

No attributed sales, commissions, confirmed new leads, refunds, fees or qualified-human sessions were measured. Net revenue / 1,000 qualified sessions is **unknown, not $0**.

## Release architecture and remaining gates
Isolated **WordPress Playground/Assembler** or local WordPress clone with *public content only* is still required; WordPress.com Personal cannot provide a native clone. Test the combined candidate in WordPress core, keep the existing Gutenberg Jetpack block and 72 Margins, then confirm first-party image bytes, real responsive visual review, axe + manual WCAG 2.2 AA, keyboard/no-JS/touch/reduced-motion, Lighthouse/CWV, actual Focus Jetpack subscriber and delivery behavior (no test subscription without approval), rights, and separate CI/QD exact SHA acceptance. The old Focus query-parameter success spoof remains a release blocker pending PR #1451 integration. Never install on the public site, merge or publish without founder approval.

**Reproduction:** `node --test experience2/review/test_ex2_homepage_exact_delta_gate.cjs` (synthetic tests); `node experience2/review/ex2_homepage_exact_delta_gate.cjs PRIVATE_HOME_EDIT.json PRIVATE_FOCUS_EDIT.json PRIVATE_CANDIDATE.txt` (privately exported authenticated editor sources). Fail closed on mismatch. Do not publish input files.
