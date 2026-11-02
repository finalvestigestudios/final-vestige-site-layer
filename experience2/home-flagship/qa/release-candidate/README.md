# Final Vestige EX2 — canonical source and rights gate (DRAFT / HOLD)

This is an **additive release verification** stacked on unpublished private staging PR #225 (parent SHA `7741595191d733f779cc05586accb1e7a4926bb4`). Frozen v1 PR #49, WordPress homepage ID 6, and Apollo PR #158 are untouched. No new features, analytics, ads, fonts, dependencies, site writes or deployment.

## Why this matters
Previously, 179/179 integrated Chromium fixture assertions and private-staging PHP tests exercised **representative fixtures**, not the 35,173-character original complete homepage from GitHub. The new pure-JS verifier runs on the actual checkout, checks a real commit SHA and tracked-file cleanliness, and rejects unexpected/unsourced media, hidden no-JS evidence, broken anchors, external scripts, missing assets and unsupported affiliate claims. A separate **media rights HOLD** and **production release HOLD** always remain explicit: source PASS is not release approval.

## Run on exact checkout (Node 22, no npm install)
```bash
node --test experience2/home-flagship/qa/release-candidate/source_gate.test.mjs
node experience2/home-flagship/qa/release-candidate/source_gate.mjs --root experience2/home-flagship --expected-head "$(git rev-parse HEAD)" --report /tmp/ex2-source-audit.json
# Expected failure until release dependencies are resolved:
node experience2/home-flagship/qa/release-candidate/source_gate.mjs --root experience2/home-flagship --expected-head "$(git rev-parse HEAD)" --require-release
```
The normal source-only command exits 0 when structural checks pass, and `--require-release` deliberately exits 2 for HOLD. Do not mark any QA results as CI PASS without running tests on this exact SHA.

## Read-only public-site verification
Authenticated WordPress read from 2026-10-30 (19:05 PT run): the only connected site is **production** `finalvestige.com`, site ID 256784396, theme **Assembler**. No separate connected staging/test site was listed (not evidence that one does not exist elsewhere). Published page ID 6 modified 2026-10-30 09:14:14, contains **72 unique** `--i:0…71` Hidden in the Margins items. Focus, Dispatch and Jetpack markers intact. No WordPress modifications.

Media ID **1258**: NYPL original 1903 map 5667×3831 and **5,553,669 bytes**; existing 768×519, 1024×692 and 1536×1038 variants. The canonical source requests 1024px Jetpack and srcset rather than the original; exact live transfer bytes **not measured**. The WordPress caption claims US public domain, but is not independent license evidence.

NYPL's own transit research guide links **image ID 5003296** to the circa-1903 BRT street railway map. However, the exact catalog item still returned HTTP 403 to automated retrieval; **item-level rights remain HOLD**. NASA's official Brand Center cautions against implied commercial endorsement; the Apollo 1 crew photo remains solely documentary, never an Inspire3 promotion. Franklin Wikimedia source is declared PDM but rights reviewer signoff remains absent.

## Actual source read-back and checks
The exact 11 GitHub parent source assets and manifest were fetched at `7741595191d733f779cc05586accb1e7a4926bb4`; this same analyzer reported **19/19 source checks PASS**, **9/9 targeted injected-source mutations FAIL**, three ledger-matched images, 7 unique chapter targets, 8 native details, 6 CSS + 4 JS, no broken fragment links. All GitHub blob IDs and structured observations are in `CANONICAL_READBACK.json`. This is a live connector source audit, **not yet a run of the committed Node test script on the new SHA**, nor real WordPress staging/browser QA.

## Missing before release
Actual approved private WordPress staging with Assembler, browser-enforced CSP/cookies and loaded-media tests; rights clearance; exact-head Chromium full-page screenshots at 320–1920, 200% zoom, mobile Safari/VoiceOver/NVDA/axe/WCAG 2.2 AA; genuinely measured lab Lighthouse and field p75 LCP/INP/CLS; GitHub hosted CI and independent QD; founder art-direction and production release approval. Black Dossier remains a recommendation, not approved. Mind/affiliate Issue #171 remains separate. No step here changes production or waives HOLD.
