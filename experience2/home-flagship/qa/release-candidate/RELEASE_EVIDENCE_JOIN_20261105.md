# EX2 P0 — one current-head release-evidence decision, not another visual prototype
**2026-11-05 · DRAFT / HOLD · Issue #150 / conversion #820 · parent PR #1102 @ `6ecf23df341fa638d519f7ccb10214022ad0f66f`.**

## What this addresses
The seven-chapter homepage has an actual **old** successful isolated WordPress/Assembler staging run: PR #637 @ `f9f9fc243ceed7df09a1674f533a9cf12c7a7c53`. Its Chromium, keyboard, axe, image and Lighthouse receipts **do not qualify the changed current candidate**. PR #1102 adds a separate GET-only anonymous /focus/ gate, but neither test automatically proves the other ran at the correct source and context. A developer could correctly report local WordPress success yet overlook that the conversion destination is unverified; conversely, one guest screenshot is not a functioning historical homepage.

This companion **does not add another chapter, design, subscription or production asset.** It joins already-existing *measured* receipts, refuses stale/synthetic evidence and outputs an immutable release HOLD. No new analytics or UTMs; no paid services; no writes to production. It is deliberately independent of frozen v1 PR #49 and Apollo #158.

## Measured inputs — do not make them up
Use an exact, clean current Git checkout, official Assembler in a disposable localhost WordPress Playground, and run the **existing** private renderer, Gutenberg save/readback, complete-page Chromium/axe, keyboard/touch, image HTTP body, and Lighthouse gates. Separately run PR #1102's unauthenticated GET-only guest browser against **https://finalvestige.com/focus/**, without filling/submitting an email. Save its output outside the repo. Then:

```bash
# Both /tmp directories below must contain REAL independent receipts for THIS run.
# Guest `result.json` must be from the live-guest mode, NOT a synthetic fixture.
node experience2/home-flagship/qa/release-candidate/release_evidence_join_cli.mjs \
  --head "$(git rev-parse HEAD)" \
  --stage /tmp/fv-ex2-current-head-stage \
  --guest /tmp/fv-focus-live-guest \
  --out /tmp/fv-current-head-release-evidence.json

node --test experience2/home-flagship/qa/release-candidate/release_evidence_join.test.mjs
```

The join requires five full private WordPress widths 360/390/768/1440/1920; actual image HTTP-body PASS and axe executed with zero detected WCAG-tagged violations at each; no-JS results; exact stage SHA; the independently generated isolated run, Lighthouse numeric 390/1440 lab receipts, and keyboard/touch usability SHA. Guest must show visible labeled email+submit forms at 320/390/768/1440, no self-link-only substitute, real public URL, and a locally fresh result (<24h). Every failure produces a *specific* code instead of silently inheriting #637's old success.

**Output is a source-attested, sanitized boolean-only decision; always `release: HOLD`.** An exit code of zero means only that this narrow local/guest evidence pack is complete. It NEVER authorizes publishing, certifies WP.com hosting, proves a signup was confirmed, or establishes real-world WCAG conformance.

The guest receipt in PR #1102 does not contain signed remote provenance; this join uses **local file mtime only**, which is manipulable and insufficient as forensic proof. A qualified reviewer must independently inspect the guest run/screenshot and actual network response before accepting its finding. No subscriber IDs, emails, URLs with query tokens, raw Lighthouse payloads or private cookie/session files are included in the merged receipt. WP.com theme/settings and production database are never copied.

## This run's independent read-only source check
Authenticated WP.com `environment=all` lists **only one site**, production #256784396, no second staging. No Personal-plan paid upgrade is requested. Page 6 was last modified `2026-11-04T14:39:24`; still contains seven archival chapters and all 72 Margins fragments. Page 1579 edit context contains `wp:jetpack/subscriptions` with `Send me the fieldbook`; its REST view renders an anchor back to `?post_type=page&p=1579`, no email input. This is an **API representation mismatch, not proof the anonymous frontend is broken**. The direct public browser remained unavailable in this environment. WordPress's own Oct 2026 documentation confirms both form and button-only-modal Subscribe Block presentations exist. The live guest test must adjudicate the actual configuration.

Independent creator acquisition remains with Grok/Praxxis via TASK-008; Claude owns production attribution and merchant verification. Dispatch already has a *separate* draft PR #1079 regarding premature download success for arbitrary `?subscribe=` values. Do not duplicate or modify Dispatch's remediation here. NYPL capture rights remain independently unresolved; a CSS/axe PASS is not rights approval. No verified paid FV product, purchase, consent-confirmed new lead or net revenue established.

## This PR's test evidence and limitation
- Three new source-controlled files: pure receipt contract, read-only local CLI, and 28 native-Node *intended* regression cases (1 positive + 27 destructive negative scenarios).
- The exact committed contract and test bodies were independently retrieved from GitHub and executed in **V8 compatibility replay: 28/28 PASS**. Blob IDs: contract `68b2a8320a11b66d7c5b3f2813698f144b22c249`; tests `17a26ab8c764241ab38a188264f89219d4b5fea8`; CLI `d6a9fbb86ca4c217fd9c573f0ae606c1320145cf`.
- **Not** a native Node run, actual current WordPress/Assembler staging run, live anonymous guest browser, WCAG 2.2 AA certificate, Lighthouse measurement, current QD, or GitHub Actions PASS. The automation environment has no functioning container/Chromium runtime and public browser navigation is blocked; earlier #637 genuine measurements remain stale for this HEAD.

**Offer → funnel → blocker → change → measured outcome → owner:** Free 52-page Focus Fieldbook → evidence-first hero CTA → anonymous Jetpack opt-in → historical WP stage PASS can be mistaken for live conversion readiness → source-attested multi-receipt fail-closed release join → 28/28 V8 mutation contract tests, CURRENT runtime/browser acceptance NOT RUN → homepage engineering + Claude Jetpack verification; Grok/Praxxis acquisition. Paid purchase and net-revenue-per-1k-qualified-human-sessions: **NOT COMPUTABLE**.

**Final release decision: HOLD.** Required independent gates remain authenticated/current WordPress/Assembler, live guest render and delivery, official media rights, exact-head QD/CI, manual accessibility, founder art direction and explicit production approval. Do not merge/deploy/publish or alter live WordPress until approved.
