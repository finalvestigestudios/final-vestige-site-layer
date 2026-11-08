# Apollo R217 — NASA source-record crosswalk and atomic fragment custody

**DRAFT/STAGING ONLY — do not merge, install or deploy.** This branch stacks only on Apollo R216 PR #1598, not frozen homepage PR #49, homepage lead branches or Research Desk PR #158. Coordinates through #150 and conversion charter #818 / #820.

## Why this exists

The earlier Atlas verified that links pointed to an allowed host and that a pinned HTML artifact existed. R217 additionally reconciles the **actual displayed** `data-source-id` link to the NASA source ledger, the Research Desk custody records, and the dated ChronologyRail. It disallows offsite URL changes even when another nasa.gov page would otherwise pass a hostname check. It rejects an altered Jan 27 accident date, an altered April 1967 retrospective report period, invented geography, NASA rights/endorsement claims, or a second paid CTA.

The PHP shortcode now verifies the SHA-256 of the **actual string it returns**; this closes the verify-then-re-read HTML fragment gap. The new `source-url-crosswalk.json` is separately SHA-pinned at runtime. This does not guarantee atomic delivery of the separately served stylesheet, fix inherited R198 ancestry or imply server-wide protection.

## Executable files

- `build_r217.py` pins parent R216 manifest SHA-256 `a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128`, validates each parent file, generates crosswalk receipt and a new PHP/fixture rendering shim. All generated artifacts remain local rather than tracked.
- `qa/gate_r217.py` runs PHP syntax, normal/print/late fallback, modified-byte helper rejection, six runtime ledger tamper checks, 7 extra adversarial source/rights/geo checks and the inherited 15 HTML + 4 CSS mutation checks; Playwright tests 320–1920px keyboard/touch/no-JS/reduced-motion/forced-colors/print and produces screenshots, LCP/CLS fixture metrics.
- `README.md` is the staging handoff.

## Reproduce

Use Python, PHP CLI, Playwright and installed Chromium at /usr/bin/chromium. Provide exact R216 `dist/` from the pinned staging archive at `experience2/apollo-r216/dist/`; this directory is **not** committed to GitHub.

```sh
python experience2/apollo-r217/build_r217.py
python experience2/apollo-r217/qa/gate_r217.py /tmp/apollo-r217-A
python experience2/apollo-r217/qa/gate_r217.py /tmp/apollo-r217-B
```

Check parent and resulting manifest SHA-256, compare screenshots, and preserve QA receipts. The previous R216 runner confirmed a localhost HTTP 200 but browser navigation was blocked by administrator policy; in that environment Chromium uses rendered PHP `set_content`. Do not claim live HTTP navigation, installed WordPress, NVDA/VoiceOver, real zoom, hosted CI, genuine axe-core, production LCP/CLS or WCAG certification from this fixture.

## Sources, commerce, roles

Technical source: NASA Apollo 204 Review Board, https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; reviewed photo catalog S66-58038, S67-15717 and S67-21294; advertising and brand restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Photo dates do not establish a specific ignition event. Citing NASA sources is **not** permission for commercial media use or implied agency endorsement.

Single landing-to-action path: future verified Grok Apollo long-form/Shorts → evidence Atlas → NASA findings/source crosswalk → existing **free** Apollo investigation. Original educator dossier remains a **hypothetical product**, not a sellable SKU. Grok owns creation/posting, Praxxis independently checks published assets and attribution against TASK-008, Claude owns production analytics/commerce, founder controls all release/paid approval. No published Apollo Grok asset_id, approved Apollo product, rights-cleared offer, merchant-confirmed sale, or qualified-human denominator has been established. Net revenue per 1,000 qualified sessions: **NOT COMPUTABLE**, not zero.

**HARD HOLD:** inherited R198 source-chain mismatch, installed WP/Assembler/CDN acceptance, independent QD, actual browser navigation, genuine axe-core, screen readers, hosted exact-head CI, verified creator and offer provenance, and founder approval. Nothing deployed, merged, posted, emailed, monetized, tracked with new scripts or purchased.
