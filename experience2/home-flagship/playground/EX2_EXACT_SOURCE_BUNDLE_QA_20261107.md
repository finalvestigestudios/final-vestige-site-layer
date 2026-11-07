# EX2 exact-source bundle custody and release triage — 2026-11-07 UTC

**Review only — HARD RELEASE HOLD.** Parent: draft PR #1351 at `6bad43a36d7473f1061adb25bb9f63e15710f4a7`. Frozen PR #49 unchanged. No WordPress production writes, merge, deploy, email send, test subscriber, analytics install, affiliate activation or spending.

## Concrete issue closed in source control
Prior offline ZIP evidence is not, by itself, proof of testing the **current exact GitHub checkout**. An independently extracted #1345 ZIP carried an archival provenance test at blob `0bbf840b7923324f16e3369f7549828f6b50d76f` that reads an untracked `review/blueprint.json`. That fixture was absent in a clean reconstructed tree; this archived test produced **ERROR in setUpClass (exit 5)**. The actual **current** PR #1351 tree already contains a different, improved archival test at blob `6450a77e0197b861e3cb937c36de25a787e063bd` which reads the committed Blueprint. We must not mistakenly "fix" that already-correct current file.

The archived provenance module was `25dc7d5beebc316436901a7cbebc395e2acfb3ad`, while current GitHub is `f55049ce88254bd855e98a95e1c43eeed98b33de`. These two version mismatches demonstrate why stale attachment-based passing tests are not exact-head qualification.

## New guard
`verify_exact_source_bundle.py` pins **13 immutable Git blob IDs** independently re-fetched from PR #1351, including the Blueprint `137c74a476005684a28f5ff9a36e75c6b03268f7`, WordPress Page 6 public-content-only manifest, PHP/Chromium admission, live drift and archival image provenance sources. It rejects any missing, mutated or older file, writes a machine-readable audit report on request, and **never returns release approval**. Even with 13/13 exact files it exits **2 = custody PASS, release HOLD**; exit 1 signals stale or incomplete sources. No network access or CMS write is performed.

Run from a FULL exact checkout:

```sh
python3 experience2/home-flagship/playground/verify_exact_source_bundle.py --selftest
python3 experience2/home-flagship/playground/verify_exact_source_bundle.py --out /tmp/ex2-custody.json
```

## Actual local verification, carefully scoped
- New source-custody self-test: **4/4 PASS** (good, byte mutation, missing file, duplicate pin invariant) on a locally identical functional implementation. GitHub readback matched the intended new file content.
- Stale/partial independently reconstructed workspace: **6/13 matching**, 7 missing/stale, **correctly rejected**. This is NOT a clean GitHub checkout; do not use it to pronounce the repository broken.
- Exact pinned Blueprint blob + recovered source checks (non-WordPress): PHP API stubs **19/19**, native admission self-test **20/20 (staging_run=false)**, page-drift unit **6/6**, and drift checker **expected exit 2 / RELEASE_HOLD_LIVE_CANDIDATE_DIFFER**.
- Static Chromium on exact pinned Blueprint: **15/15 modes, 105/105 chapter interactions**, 320–1920 px. It is NOT rendered inside WordPress/Assembler; external media was blocked. Existing before/after visuals and this fresh replay are in independent evidence, not staged performance.
- The recovered offline provenance ZIP had four prior passing tests only when its generated local fixture existed. That result cannot substitute for current exact-head native test execution.

## Required next gates
1. Execute this custody guard in the complete exact GitHub checkout; replace the stale evidence ZIP as the source of truth.
2. Execute current exact GitHub verifier sources from that checkout.
3. Run actual isolated WordPress Playground/Assembler with candidate, then authoritative browser inspection at 320/360/390/768/1440/1920, reduced motion, 200% zoom, keyboard/touch/no-JS where possible; real Apollo/Franklin response bodies and hashes; official axe and manual WCAG 2.2 AA; lab Lighthouse/CWV.
4. Reconcile published Page 6 (seven chapters/72 Margins, 4 Focus links, eight images incl. NYPL) vs candidate (seven/72, five Focus links, two images excluding NYPL) before replacing any page. Review image-source rights and preserve Focus/Jetpack.
5. Obtain independent CI/QD on exact release SHA and founder visual/release approval. WordPress.com Personal has no native staging clone; free Playground is a *different environment* and does not certify hosted Jetpack or field CWV.

**Conversion-first interpretation:** Offer = free 52-page Focus Fieldbook → source proof and visible contextual CTA → confirmed subscription → verified paid order. Blocker = stale QA could falsely certify a release and damage the live conversion path. Change = byte-exact source gate. Evidence = GitHub file-blob readback and adversarial local tests. Owner = interim homepage engineering/independent QA; Claude owns actual signup, attribution and checkout engineering; Grok/Praxxis own social acquisition. **No verified new lead, order, affiliate payout or net revenue.**

## Integrity declaration
This PR adds verification only; no homepage, WordPress page, affiliate link, or public artifact changed. All passing numbers above are scoped to the actual environment used. Release remains **HOLD**.
