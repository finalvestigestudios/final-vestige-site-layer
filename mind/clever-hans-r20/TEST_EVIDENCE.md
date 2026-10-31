# R20 actual source audit and release evidence — 31 October 2026, Pacific

**Status: PASS of LIMITED OFFLINE SOURCE CONTRACT; NOT CI GREEN; RELEASE HOLD.**

Audit provenance: fetched ALL 10 requisite current source files from authenticated GitHub connector in isolated new branch feature/mind-clever-hans-zen12-control-20261031-r20, at exact evaluated QA/branch commit **b8d9ba9b49530d8d1ed6a4f21c77c4a0f5207c58**. Dynamically evaluated the committed *actual* qa.cjs auditor in isolated JavaScript V8 and passed the real readback texts as an object to its exported audit and mutationChecks functions.

**Final executed result: 104/104 source checks passed (0 failed); 18/18 deliberate source mutations detected.**

Honest QA progression: first executed readback pass 102/104 (2 false-positive source test strings: mention of autoplay in prose and case-sensitive approval sentence). Corrected QA tests and reran 104/104; initially 17/18 mutation tests caught because article contained more than one real Focus URL and the mutation replaced only the first. Corrected mutation to replace all occurrences and reran **104/104 + 18/18**. All QA file changes itself isolated within new branch. README added AFTER the audited commit; README is narrative documentation only, no modification to audited 10 blobs.

## Authenticated GitHub blob SHA provenance of executed source test

- investigation.blocks.html: 5f1f3dcee2bec29f4aa76323eaa1c1695dc2c4ea
- zen12-independent-guide.md: c0bd82e980b5d79bd92ee19cddcd91903d870b52
- zen12-pilot-A.blocks.html: 757109eb11c79556f8940c8b6ceafcfef1f42871
- zen12-pilot-B.blocks.html: cbe676284587a03eacbc0e5e3d52b6c597a70157
- video-poster.svg: ad927427da9c9fb2c457fe3cc4d04623997abfff
- zen12-film-draft.vtt: aa2d60551c11f855944e5ed4d6853423207a9043
- mind-archive-draft.blocks.html: f6952e3791c79a6e209a22badeb2090ec0cd8887
- EVIDENCE_MATRIX.json: c64b377c8ecca2b1601054424d57ebf88246a1d8
- ATTRIBUTION_EXPERIMENT.md: db572d560f7567e44bf57e11da5b409d022d1808
- qa.cjs: 536c13fdd7b2fe669dd7f48de48bd3169b8f0fc7

These are Git blob SHA IDs, not file SHA-256 hashes.

## Source tests actually checked

104 checks include: all expected file presence; four no-JS WordPress Custom HTML wrappers, unique H1 per page and labelled structure, responsive/reduced-motion/keyboard focus rules, no executable scripts, no external active merchant links, no extra email forms, no third-party tracking pixels, article historical controlled numbers and counterevidence, real Focus and Puységur internal links, actual merchant product and checkout citations with qualified efficacy, full free baseline, two disabled disclosed offer slots per A and B, exact A/B editorial byte equality except original optional film block, B player hidden/source-less without actual autoplay, caption script/provenance, SVG original non-network poster, four Mind hub streams, 60 unique claims / 17 exact sources, account acceptance FALSE, earning URL NULL, tracking OFF, film UNHOSTED, A/B experiment OFF, no invented price/commission. Adversarial mutations included tampering with historical counts, link removal, changed disclosures, enabling purchase/video, adding merchant links, form and trackers, fake approval, unknown source IDs, external SVG and false unique-user language.

Native GitHub compare against exact unchanged main **77a87635eb613ce6de268aee11350fa8242efa0f** returned all **11 new files**, 0 existing files modified, renamed or deleted (before adding this evidence log). All paths start mind/clever-hans-r20/. Any additional final evidence file also starts in that directory and does not change previous code or content.

## Explicit NOT TESTED

Node CLI after checkout was **NOT executed** (the committed audit itself was run as an export in isolated JS V8). GitHub hosted Actions exact checked README commit eead8dafce22bfd68b245c875728b4d8121c67a1: **0 check runs**, combined status **pending**, total status count **0**. No hosted CI pass is claimed.

No live WordPress Gutenberg save/render, published /mind/ route, staged CMS, 360/390/768/1440/1920 browser pixel/keyboard/assistive-tech, 200/400% zoom, caption synchronization, MP4 production/playback, network traffic budget/Lighthouse/CWV, GA/Jetpack analytics integration, merchant click, opt-in A/B experiment or conversion measurement were performed. No source check substitutes for any of those release gates.

No WordPress CMS/navigation/settings, homepage PR #49, art Issue #150, Mind hub PR #172, QA Issue #126, Dispatch Issue #174, subscriber records, existing Jetpack funnel, newsletter email, merchant link, affiliate tracking, merge or deploy was altered.

**Blockers:** written account-specific Inspire3 acceptance & permitted exact SKU outbound/tracking/channel/creative terms, official final checkout state and contract, independently reviewed science and FTC disclosures, produced/hosted accessible first-party 42-second film and timed captions/transcript/on-video disclosure, genuine staging/browser/a11y/security/performance QA, founder explicit CMS release approval and separate affiliate activation authorization.

## Replication

After obtaining a repository checkout at an appropriate commit:
    node mind/clever-hans-r20/qa.cjs --mutation

That CLI is supplied, not claimed as having been run in this session. A review should independently run it in CI and compare output with the exact blob readback evidence above.
