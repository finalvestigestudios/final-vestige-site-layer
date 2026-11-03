# Experience 2.0 — integrated rights-safe Malbone and Margins contrast candidate

**DRAFT / PRODUCTION HOLD.** This is a read-only **integration** gate for two existing, separate homepage remedies. It changes no live WordPress content and creates no new chapters, commercial links or image assets.

## Sources, base and evidence

Base: PR #786 exact SHA fd47353075ed611ab71f8012a5032091da5fbb95, already stacked on rights-safe PR #780. The runner imports the *existing* #786 Malbone mutation and request denial code, and the original contrast-safe Margins CSS from PR #746/#765. No forked copy of those corrections is introduced.

The authenticated published page 6 source was previously read on November 3, 2026 with SHA-256 c9a6cd57582cce2801620381212193d54b9e6446236b24aff1880a12ff1d3b7e. The source fingerprint is a historical readback, **not** a present-day source-lock certification.

## What actually gets tested

An anonymous real Chromium browser retrieves https://finalvestige.com/ at 320, 390, 768, 1440 and 1920 CSS px. Every non-GET request and the disputed NYPL capture fetch are blocked. In browser memory only, the test selects the actual published Malbone evidence case, removes the withheld image, updates the source caption and rights notice, inserts the already-reviewed fallback formatting, and adds the already-reviewed contrast-safe Margins stylesheet **after the published CSS**. Production WordPress is never written.

Each case must retain HTTP 200, correct host, seven chapter anchors, all 72 Margins, Focus CTA, two NYPL catalog links, archive-image elements 3→2, and source details; it must lose the unsupported public-domain assertion and image URL, retain a legible bounded Malbone fallback, show exactly one fully opaque unblurred historical record under reduced motion, and introduce no horizontal overflow.

At 390 and 1440px a pinned local axe-core 4.10.3 checks the Margin strip's color-contrast rule (both violations and incomplete results must be zero). Candidate-case viewport screenshots are hashed and retained with minimal JSON receipts. Every source test and browser admission fails closed on missing required evidence.

## Honest limitations

This is an **ephemeral rendered DOM comparison**, not a saved Gutenberg/Assembler roundtrip, an actual WordPress staging environment, a full WCAG 2.2 AA review, true 200% zoom or Safari certification. It cannot determine p75 field LCP/INP/CLS or prove any particular image's reuse permissions. JavaScript-disabled behavior of the **combined persisted** candidate remains untested, even though independent tests have exercised constituent no-JS behaviors. Actual owner approval for publication has not been given.

WordPress.com's Personal plan lacks a native staging clone; the wpcomstaging.com alias is NOT a separate staging site. Isolated WordPress Playground can test development behavior but cannot certify production hosting. Never export subscriber records, credentials, production database, secrets or private media into a developer clone.

## Release controls

**HOLD** until independent exact-SHA QD, save/readback of both changes in isolated WordPress/Assembler, source-specific NYPL rights decision, manual keyboard/touch/zoom/assistive-tech/Safari audit, measured performance, and founder-approved release/rollback. PR #49 is frozen. Apollo #158 and Mind #171 remain separate. Historical investigations and their links, the 52-page Focus Fieldbook, native Jetpack signup and all 72 Margins remain protected. No subscription purchases, production edits, merge or publish.

Run the committed source tests first. The dedicated workflow then pins Playwright/Chromium and axe-core, records exact head, runs combined actual-host browser checks, and archives even partial results. A browser failure is an admission **FAIL/HOLD**, never a successful release.
