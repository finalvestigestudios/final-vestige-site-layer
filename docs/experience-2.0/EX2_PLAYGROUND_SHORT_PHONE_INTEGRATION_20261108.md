# EX2 — private WordPress Playground short-phone integration (2026-11-08)

**DRAFT / RELEASE HOLD / NO PRODUCTION OR STAGING INSTALL.** This closes the stale-stylesheet packaging gap recorded in PR #1601; it is not a fresh chapter or a second visual design. Stacked on PR #1601 at `34c08c140f4f77158ea86d34f98f2e733094885e`. Frozen PR #49 at `10495883299d53596992c26a8987f629b2904670` remains untouched.

## Offer → funnel → blocker → change → evidence → owner

- **Offer:** the existing 52-page Seven Day Focus Fieldbook, secondary to actual historical evidence.
- **Funnel:** historical homepage / evidence-room primary action → contextual Focus → independently confirmed Jetpack lead → **verified** sale or merchant-reported paid affiliate conversion. No revenue, actual signup or conversion uplift is inferred.
- **Blocker:** the source-controlled short-phone correction in #1601 was **not** bundled into the private Playground PHP inline stylesheet, so staging could silently show the old CTA below the 320×568 fold.
- **Change:** deterministically rebuild the *previously protected* five-member Playground Blueprint ZIP with the exact approved CSS delta added inside `FVPG_CSS_END`. Update internal custody SHA and an explicit HOLD note. Make no other PHP/HTML/JS/Blueprint changes.
- **Evidence:** local PHP 8.4 syntax lint; simulated WordPress hook/shortcode callback produces the real PHP HTML; Chromium 144.0.7559.96 checks **92/92 PASS** at 320×568, 360×640, 390×667, 768×1024, 1440×900, 1920×1080, each with JS on/off, reduced-motion requested and external network disabled; **five** negative controls rejected. Test files and SHA receipts were checked against this PR's exact GitHub blobs.
- **Owner:** interim homepage engineering; Claude owns any production Jetpack/attribution integration, Grok/Praxxis own creator acquisition.

## Exact private-artifact custody

| Artifact | SHA-256 |
|---|---|
| Parent protected Playground ZIP from prior PR #1515 study | `8db20aac81deba544d057abfe28fe3baaf71639f74f421a210676fbb0b36e56b` |
| Parent review PHP | `7fe27aecc6f5f2b8033ab826dcb5146b6e31ae4dbcaf2a7825859b48dc5b51ee` |
| CSS delta from PR #1601 | `dfa8d6c922ab066f5fde3e81b5d4fbb70f05978d4cade0eb0befcfd7e528308a` |
| Rebuilt private Playground ZIP | `7416678c39d4d08914e19182b980df5e2d3fdec43208a01a983d2b57edc42bed` |
| Rebuilt review PHP | `4b05a6c2a70ea7a8de8624d7be8ebfbcffc6e5124882dfcb3c2e297f8dd960f9` |

The private ZIP is **NOT** checked into the repository and contains no subscriber data, secrets, WordPress production database, or Jetpack subscriber export. The builder only changes `REVIEW.txt`, `SOURCE_CUSTODY.json`, and the PHP preview's scoped **inline CSS**. `blueprint.json` and the separate private browser receipt PHP are byte-identical to their parent versions; the HTML and JavaScript remain unchanged. No new archival imagery, external analytics, vendor URL, affiliate claim, script, or purchase CTA.

## Measured before/after in the **actual PHP-generated fixture**

| Viewport / behavior | Old evidence CTA top–bottom | Bundled CTA top–bottom | Interpretation |
|---|---|---|---|
| 320 × 568, JS ON | 583–627 | **513–557** | Primary evidence CTA now fully inside first screen |
| 320 × 568, JS OFF | 583–627 | **513–557** | Same correction without JS |
| 360 × 640, JS ON/OFF | 541–585 | **474–519** | More breathing room for the CTA |
| 390 × 667, JS ON/OFF | unchanged | unchanged | Non-target viewport preserved |
| 768/1440/1920 | unchanged | unchanged | Tablet/desktop preserved |

The same fixture preserved seven chapter links, 72 Hidden in the Margins records, both evidence images and contextual Focus actions. No document-level horizontal overflow or browser page exceptions were observed in these configurations. **This is not WordPress core, Assembler, Jetpack, axe, screen reader, real image transfers, or an independently measured Lighthouse/CWV result.**

## Reproduce on an isolated developer machine

Use only the **privately supplied** parent review ZIP, never a live site. Obtain the exact PR #1601 CSS from the *end* of `experience2/home-flagship/flagship.css` (the one `/* FV EX2 — compact short-phone first-screen composition.` block and its trailing newline). Verify the delta SHA above.

```bash
python experience2/home-flagship/playground/rebuild_playground_short_phone.py \
  --parent /private/fv-ex2-official-playground-web-review.zip \
  --delta /private/mobile-first-fold.css \
  --out /private/fv-ex2-short-phone-review.zip \
  --receipt /private/build-receipt.json
python experience2/home-flagship/playground/test_rebuilt_playground_short_phone.py \
  --parent /private/fv-ex2-official-playground-web-review.zip \
  --delta /private/mobile-first-fold.css \
  --runner experience2/home-flagship/tests/verify_php_playground_renderer_browser.py \
  --out /private/browser-evidence
```

Requires installed PHP, Python Playwright and Chromium. No GitHub Actions pass can be assumed from offline execution. Official WordPress Playground supports local Blueprint ZIPs via its CLI; that path is *next*, not a completed test. See https://developer.wordpress.org/playground/blueprints/bundles/.

## Archival / rights reconciliation

Read-only WordPress Page 6 on 2026-11-08: last modified `2026-11-05T12:07:24`, 150,710 editor-source characters, seven chapters, 72 Margins, **one native Jetpack subscription block** and four `img` tags. This protected candidate is a **standalone** demonstration and keeps two archived `data-fv-archive-img` images. It must **never** be appended to or used to replace production Page 6: that would duplicate chapters/Margins or lose the Jetpack block (PR #1587).

WordPress media metadata (not transfer receipts): NASA Apollo 1 photo ID 473 / 78,346 bytes; Franklin Victory Point Note ID 474 / 466,043 bytes; NYPL Brooklyn map ID 1258 / 5,553,669 bytes. No actual image bytes were fetched in this offline fixture, and the NYPL edited derivative stays excluded from the protected candidate pending item/derivative and jurisdictional rights reconciliation. No new visual assets were added; NASA credit/no-endorsement and Franklin source disclosures must remain intact.

## Release decision — HOLD

The WordPress.com Personal plan cannot create a native WordPress.com staging clone. Only accessible connected site is production ID 256784396. **Do not install or activate this ZIP on that site.** The `wpsandbox.wordpress.net` entry in the host allowlist is the *actual* WordPress Playground web runtime (not a WordPress.com production staging clone). An isolated local official Playground with the Assembler theme remains the next necessary acceptance environment. Run actual WordPress core, theme, and native block integration; real first-party media network receipts; axe + manual WCAG 2.2 AA, keyboard/touch/no-JS and browser zoom; lab Lighthouse/Core Web Vitals; and authorized Jetpack testing without fake subscribers. Then require independent CI/QD and founder's exact release approval before any production action.

This PR is a reviewed, reversible preview-package update, **not** production approval.
