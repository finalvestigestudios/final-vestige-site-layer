# EX2 / Page 6 — combined saved-Gutenberg candidate builder

**Status: DRAFT / OFFLINE ONLY / PRODUCTION RELEASE HOLD.** This is not a
WordPress save, a hosted stage, a production deployment or WCAG certification.

## Why this is the next gate

PR #788 verifies an ephemeral browser-memory overlay of the two needed
corrections. It does **not** verify the Gutenberg **saved** representation that
would be required for an authorized release. This PR supplies the missing
deterministic, source-pinned *local Gutenberg candidate* assembly step: combine
the previously reviewed NYPL capture-withholding transformer and the existing
contrast-safe 72-record Margins CSS without changing any other page content.

No new chapters, artwork, advertising or visual directions. Frozen homepage
PR #49, Apollo PR #158, and Mind Issue #171 are unchanged. Black Dossier,
Museum After Hours and Observatory remain unselected options.

## Read-only actual-source baseline (2026-11-03)

Authenticated WordPress.com page ID **6** on site **256784396** was read with
context=edit, without the Automattician-only content_format parameter.
Returned status publish, modified **2026-11-02T17:48:13**.

Actual raw Gutenberg markup observed *in memory*, with no public copy saved:

| Source check | Actual value |
|---|---:|
| Raw markup string length | 150,727 characters |
| Gutenberg custom HTML block openings / closings | 5 / 5 |
| Margins record indices | all 72, in order (0–71) |
| First block style tags | 1 |
| Original fvMarginReveal keyframes in first block | present |
| NYPL unverified file references in one responsive image | 4 |
| NYPL reuse assertion | 1 |
| NYPL original catalog URLs | 2 |
| Jetpack subscription Gutenberg blocks | 1 |
| Focus Fieldbook textual occurrences | 5 |
| Script tags | 4 |
| Archive image controls | 4 |

A **separate JS in-memory source rehearsal** (not the committed Python, not a
WordPress save) applied the existing two narrowly specified transformations
to the current 150,727-character raw source: one NYPL image tag and unsupported
capture-specific rights claim withheld, two catalog links retained, 72 Margins
and original JS/Focus/Jetpack blocks preserved, and the safe CSS placed in the
**existing first Margins style block** just before its closing tag.
The rehearsal's resulting character length was **151,156**, with no additional
HTML blocks, scripts, or style elements. It **did not** modify WordPress.

The browser-memory test in PR #788 remains separate. **Do not treat this
in-memory JS rehearsal as a successful execution of this Python builder against
the actual production export or as a saved Gutenberg readback.**

## Source of code / rights

- Existing rights transformer:
  experience2/home-flagship/rights/withhold_unverified_nypl_capture.py
  (from draft PR #780). It preserves the text fallback and catalog links,
  replaces the unsupported reuse assertion with a candid rights notice and
  removes only the unverified NYPL responsive reproduction.
- Existing contrast CSS:
  experience2/home-flagship/accessibility/margins/margin_strip_contrast_safe.css
  (from draft PR #746; independently tested in later draft PRs #765 and #772).
- Existing joint hosted HTML/DOM/CSS preview: draft PR #788, base of this PR.
- Malbone NYPL catalog:
  https://digitalcollections.nypl.org/items/c745e730-d2a9-012f-5ecc-58d385a7bbd0
  (catalog ID 5003296). **The particular digital capture's reuse permission
  remains unverified.** Linking the source is different from reproducing it.
- No new media, third-party font, network request, tracking, affiliate URL
  or licensed graphic is introduced.

## Reproduce offline — only with a locally held, authorized raw export

Never commit the original page export or generated candidate to GitHub or
public CI artifacts. Never include subscribers, private posts, credentials,
comments, theme settings or a live production database in a test artifact.

1. Get a fresh read-only Gutenberg raw page-6 export and independently
   calculate its exact UTF-8 byte SHA-256. Check site/page/revision.
2. On a checkout at this PR's exact head, run the synthetic-only tests:

   python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_build_combined_page6_offline.py -v

3. Generate an **offline** candidate in separate private local paths:

   python -I experience2/home-flagship/qa/release-candidate/build_combined_page6_offline.py --source /private/page6-raw.html --expected-sha256 SHA256_FROM_SEPARATE_READBACK --output /private/page6-candidate.html --report /private/candidate-report.json

4. The script must refuse changed source, missing source controls,
   corrupted/duplicated Margins, missing Focus/Jetpack, ambiguous image
   source, alternate/duplicate stylesheets, external CSS, repeated repairs,
   overwritten files, or a mis-pinned SHA.
5. Review the **local** generated candidate in free isolated WordPress
   Playground or disposable local WordPress + Assembler using PUBLIC
   content and cleared media only; compare the saved Gutenberg DOM,
   interactions, 320/360/390/768/1440/1920 widths, no-JS, keyboard,
   reduced motion, 200% zoom, screen readers, real image transfers,
   axe-core, and repeatable Lighthouse. An isolated environment **cannot**
   certify WordPress.com Atomic cookies, redirects, Jetpack subscriber
   behavior or field Core Web Vitals.
6. No production install, edit, plugin activation, merge, release or CDN
   purge without exact release authorization and independent QD.

## Release decision

**HOLD**, even if synthetic CI passes. Outstanding: actual Python run against
a complete verified export, isolated Gutenberg save/readback and private
preview, manual WCAG 2.2 AA + screen reader/keyboard/touch/no-JS +
Safari/200% zoom, founder visual review, image-specific NYPL rights
decision, measured performance, exact-SHA independent QD, rollback plan
and separately approved production release. WordPress Personal does
**not** provide native WordPress.com staging; do not suggest upgrading
for this gate.

No production source is uploaded in this PR. Synthetic tests are engineering
checks, **not legal, accessibility or art-direction approval**.
