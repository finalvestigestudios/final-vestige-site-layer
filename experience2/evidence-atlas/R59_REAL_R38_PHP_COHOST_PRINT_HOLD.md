# Apollo R59 — actual original R38 PHP cohost and complete print custody (STAGING HOLD)

Scope: Issue #150. Stacked on R58 PR #562 at `65c8f8dac74ed66b9af7c4d3f3a9ec95a1b52e86`. Independent of homepage PR #49 and original Research Desk PR #158. No WordPress, homepage or deployment writes.

## Genuine defect reproduced and repaired

Before R59, searching the actual R38 Research Desk for `S67-19766` left **only 1 of 6 research records visible in Chromium print media**, with **0 source-custody values visible**. The Atlas already restored its own hidden sources on paper; the cohosted Desk did not. A visitor printing an active search would therefore silently lose five records and all six closed native custody drawers.

The R59 fix is **strictly scoped to the Apollo suite print stylesheet**, leaving every original Research Desk byte and NASA record untouched. It restores all six original Desk cards, their 30 provenance values and six original findings, prints the source URLs, and changes Desk ink to legible black on white. It preserves six Atlas records, all 54 Atlas custody values and six source-register citations, even after filters. Interactive on-screen behavior is unchanged.

## Real original source / PHP execution

Read the actual PR #158 and the later **R38** branch sources. The following five original R38 Git blob identities were matched to the local bytes before each run:

- Research Desk PHP: `44a43c63ba262de4193295563f5762df6e731077`
- Research Desk template: `4842afb84b4c993cfc4861ce7f5a7a4d7b451871`
- Original Desk CSS: `7b0972fc3a920ded08f9783fddcfc9c609c7ff06`
- Original Desk JS: `57f4a639d4c37fc4355b10fe7dec085bf87c6eb7`
- NASA custody crosswalk: `ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea`

New `tests/php_real_cohost_r59.php` invokes the **original R38 shortcode**, the source-built Atlas shortcode, and the pinned Apollo suite shortcode together using a minimal CLI WordPress API contract fixture (not WordPress core). No synthetic Desk markup is substituted. Four conditions passed: raw top-level shortcode, private staging page ID with nested block markup, non-allowlisted page, and nonsingular view. The first two had all three CSS and both JS handles enqueued before a simulated `wp_head`; the latter two did not falsely claim prehead loading. All four delivered real six-plus-six source records when callbacks were invoked.

## Browser QA, 2026-11-02 UTC

`python tests/browser_r59_php_cohost.py --output <review-dir>`

- **16/16 genuine original R38 + Atlas Chromium cases**: 320, 360, 390, 428, 768, 1024, 1440 and 1920 px, JavaScript on and off; reduced-motion enabled, touch emulated at mobile widths.
- **8/8 filtered print regressions**: Desk 6/6, Desk custody 30/30, original Desk fulltext 6/6, Atlas 6/6, Atlas custody 54/54, source citations 6/6; Desk print color `rgb(17, 17, 17)`.
- Original Desk search, Atlas year filter, both-direction source links, keyboard focus restoration, no-JS native drawer operation and complete no-JS source access all passed.
- No page errors, unexpected external requests, embedded photograph binaries or horizontal overflow observed.
- Two Chromium screenshots (390 and 1440 px) reproduced byte-for-byte on consecutive captures:
  - `r59-real-r38-390.png`: SHA-256 `54787a0c7d4df372d5bc96ba9ab545794bbdabb7d6744894c4dda3c663e6e14e`
  - `r59-real-r38-1440.png`: SHA-256 `f6c04d4f0b94ff9805a41d6bb3a9e8e1e127ece2c2596c76d04dc9319a79cd9b`
- Local cohost-fragment LCP **108–140 ms**, CLS **0** across eight script-enabled widths; **not hosted Core Web Vitals**.
- Python component tests: **94 run, 93 passed, 1 skipped** (original PR #158 independent fixture absent from this selected bundle); Atlas native tests: **11/11 passed**; PHP lint and Node syntax passed.

`tests/build_r59_bundle.py` requires the five original source hashes, validates the Chromium receipt and screenshots, packages the source-built staging candidate, and verifies every included file hash. Two independent builds produced a **byte-identical 91-file ZIP**, SHA-256 `80e6d319bda8de68448ca0c38f1aef120bce8123fa553039c1aab711378ccb33`. The archive contains no NASA image binaries and performs no network or CMS writes.

## Source and release custody

All six proposed NASA photographic uses remain individually unreviewed. Record 01's catalog association `S67-19766` is still **provisional**; the linked NASA page does not display that catalog identifier. There are **no** fabricated map pins or relationship edges.

**HOLD**: This tests exact original components and real PHP callbacks in a deliberately limited WordPress API simulator. It is **not** installation or visual acceptance inside WordPress/Assembler, and cannot establish genuine asset loading in that environment. Verified axe-core, screen-reader acceptance, hosted LCP/CLS/INP, independent QD, rights approval and CI on the exact commit remain outstanding. Do not merge or deploy. No production WordPress content/settings writes and no edits to PR #49, PR #158 or homepage branches.

## Reproduce

1. Check out this branch with the complete `experience2/research-desk/` original R38 directory.
2. Run `python -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py'` and `python experience2/evidence-atlas/test_atlas.py`.
3. Run `python experience2/evidence-atlas/tests/browser_r59_php_cohost.py --output /tmp/fv-r59-qa` with PHP, Python Playwright and Chromium installed. The tool will **fail instead of substituting fixtures** if exact original R38 files are absent.
4. Build reproducible review package with `python experience2/evidence-atlas/tests/build_r59_bundle.py --output /tmp/fv-r59.zip --qa /tmp/fv-r59-qa`.

Release gate remains closed pending authentic private WordPress/Assembler acceptance and independent reviews.
