# Seven-chapter selective Gutenberg migration — SOURCE REVIEW ONLY / RELEASE HOLD
**2026-10-31 22:00 PDT.** Isolated review branch based on **PR #402 HEAD `457648947df082a634fafd127d95c4deff556083`**. No WordPress write, publication, install, merge, new chapters, fees, or frozen PR #49 change.

## Actual WordPress source, read-only
Connected WordPress.com site **256784396**, published homepage **page 6**, reported modified **2026-10-30T09:14:14**. Public-page raw Gutenberg input: **47,021 JS characters / 47,091 UTF-8 bytes**; independent SHA-256 **`52f3a353d092c025b2c527058d2ae695a3d3f2d21bbaf4722955c30f3b784cab`**. This hash is a snapshot, **not a permanent production constant**; re-read before any later test.

Read-only inspection located exactly one **`fv-studios-hero`** HTML block (4,288 UTF-8 bytes), one original H1, 72 unique `fv-margin-strip__item` records indexed 0–71, one **native Jetpack subscriptions Gutenberg block**, and two exact `/focus/` anchors. The second original Focus anchor is **decorative artwork** (`fv-focus-cta__art`, `tabindex="-1"`, `aria-hidden="true"`), *not* a second keyboard/AT signup CTA. Do not make untrue claims of two active signup controls.

## New source-controlled migration and its precise boundary
- `assemble_homepage_migration.cjs` requires independently reviewed SHA-256 digests of both current page-6 Gutenberg source and **the exact WordPress-only fragment**; refuses changed/ambiguous hero, any hidden protected blocks, duplicate H1, absent 72 records, malformed evidence chapters/cases, nested theme chrome, scripts/styles/forms within the injected fragment, missing disclosure, or changed/duplicated native Jetpack markup.
- It replaces **only** the identified `<!-- wp:html -->` block containing the original `fv-studios-hero` and `fv-studios-title`, leaving **all bytes before and after unchanged** (including the Margins, Focus Fieldbook CTA, existing WP Query/terms/feed, single Jetpack block and schema.org JSON-LD).
- `verify_homepage_migration.cjs` now rejects `hidden` / `inert` / `aria-hidden` / inline `display:none`, `visibility:hidden`, `opacity:0`, inert templates, closed details/dialogs, and protected elements faked inside scripts/styles. Narrow exception: the existing independently preserved *decorative* Focus artwork anchor described above. This is **source-negative checking**, not visual accessibility certification.
- Output is a private, write-once `0600` *review candidate* and SHA receipt, never written to WordPress; production source and subscriber data are not checked into GitHub.

## Exact live-source no-write dry run (executed)
Fetched **the current branch's actual verifier and assembler files** by Git blob and executed their exported functions in an isolated V8 Node-API compatibility shim against the **real page-6 raw public block content** and reconstructed **source-pinned seven-chapter fragment** from `experience2/home-flagship/index.html` (blob `70ebe0d8e122048343c99a3c6adc6f7ac498ed7f`). Fragment SHA-256 independently matched the earlier offline local package:
`a868423c033a179d1821bb9eb1cf7b5c6c07106097e18cce6afe58b79f908cc1`.

**Result: `SELECTIVE_GUTENBERG_CANDIDATE_REVIEW_ONLY_NOT_DEPLOYED` PASS**, candidate bytes **77,740**, SHA-256 **`9c6327faa11b733a853414562a6eddf45ee89105626d7766a052965b771418b4`**. Source integrity preserved: **15,511 original prefix bytes + 27,292 original suffix bytes**; one original hero removed; **one H1, seven chapter anchors, Apollo/Franklin/Malbone, 72 Margins, one Jetpack block, two original Focus anchors**. No page candidate or private source copy was uploaded to GitHub.

The first exact-live execution uncovered an **overzealous source gate** that rejected the genuine intentionally `aria-hidden` decorative Focus artwork anchor. We corrected the rule to preserve that exact original non-interactive anchor while still failing on hidden ancestors or a concealed primary CTA; rerun passed. This is a genuine live-source integration defect resolution, not a claim of browser acceptance.

## Local executable QA
Node 22 on isolated local equivalent, with the exact source-verified PR #382 WordPress-only fragment, executed **44/44** tests (29 selective-migration/visibility tests + 15 previous preservation tests) after correction. Their three final updated GitHub test source blobs match independently computed local `git hash-object` values:
- assembler `ba3f617af27afb95a637d09483c0c8db8637942e`
- verifier `e85a7c16acddacfa16601d49052649d262fab16d`
- tests `92069fd7dd60120fede4573eb7639fdbc9850fb9`

Reproduce from exact checkout after obtaining **PUBLIC page content only** into a protected local file (never import private database/users/settings/secrets), and use the release builder's source-pinned output:
```sh
FV_RELEASE_FRAGMENT=/PRIVATE/wordpress-page-fragment.review-only.html node --test \
  experience2/home-flagship/qa/release-candidate/test_homepage_selective_migration.cjs \
  experience2/home-flagship/qa/release-candidate/test_homepage_preservation.cjs

node experience2/home-flagship/qa/release-candidate/assemble_homepage_migration.cjs \
  --legacy /PRIVATE/public-page-6-raw-gutenberg.html \
  --fragment /PRIVATE/wordpress-page-fragment.review-only.html \
  --legacy-sha256 52f3a353d092c025b2c527058d2ae695a3d3f2d21bbaf4722955c30f3b784cab \
  --fragment-sha256 a868423c033a179d1821bb9eb1cf7b5c6c07106097e18cce6afe58b79f908cc1 \
  --out /PRIVATE/review-candidate.html --receipt /PRIVATE/review-receipt.json
```
The input source digest is valid **only for the exact WordPress snapshot documented above**.

## Source/rights/staging admission still OPEN
Original three-case art retains source custody limits from PR #329 and media fingerprint checks from PR #395. Franklin's **RMG museum catalogue URL is not a license for an RMG digital photograph**; the existing historical article cites a distinct Wikimedia Commons 1869 public-domain reproduction. Verify actual WP Franklin file **474** against the exact source. For NASA Apollo **473**, establish original media bytes and no commercial endorsement implication; for NYPL **1258**, obtain record-specific rights confirmation. Verify actual HTTP bytes and matching hashes, not just WP metadata.

WordPress.com **Personal** plan does not provide native staging clones. Continue with free isolated WordPress Playground or local WordPress + **Assembler** theme, using public-content-only sanitized import and sealed preview adapter from the existing R&D chain. This V8 test **does not prove the WordPress renderer, 7-viewport layout, real image loads, Jetpack email delivery, WCAG 2.2 AA, no-JS, reduced motion, mobile keyboard/touch, Lighthouse/CWV, host redirects/cookies or QD/CI**. No external JavaScript or new affiliate offers were added. Preserve the existing Focus Fieldbook and Mind's independent editorial review; avoid unverified Inspire3 claims.

**Release: HOLD.** Requires isolated WordPress/Assembler staging and first-party media transfers; a genuine Chromium/axe/Lighthouse report; image rights and SHA review; exact-head QD/CI; founder art-direction selection and explicit production approval. Frozen PR #49 remains untouched; Apollo PR #158 and Mind/affiliate Issue #171 remain separate.
