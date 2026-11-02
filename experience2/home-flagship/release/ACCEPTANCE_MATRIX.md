# Acceptance matrix - flagship release candidate (2026-11-02)

Legend: **PASS**, **FAIL**, **BLOCKED** (cannot be done by engineering alone), **NOT TESTED**.
Section A is real WordPress + real Chromium on the integrated page. Section B is synthetic or source-level. They are kept apart on purpose.

**Test target:** WordPress (Playground CLI 3.1.61, PHP 8.3) + official Assembler 0.0.126, composed page seeded as page ID 6, **inline delivery** (the proposed production mechanism). Chrome 156 via Playwright. axe-core 4.10.2 (tags wcag2a/2aa/21a/21aa/22aa + best-practice). Lighthouse 12.6.1. All raw results are in `evidence/`.

## A. Real WordPress / real browser

| # | Requirement | Result | Evidence / note |
|---|---|---|---|
| A1 | Complete integrated homepage renders in isolated WordPress with Assembler | **PASS** | `screenshots/first-arrival-*.webp`, `full-page-1440.jpg`, `full-page-390.jpg`. 1 header, 1 footer, **1 `<main>`**, no duplicated chrome. |
| A2 | Monumental, legible first arrival (390 and 1440) | **PASS (engineer review)** | At 1440x900 the primary CTA is in the first view after a hero-rhythm fix (it was below the fold). Founder visual approval: **BLOCKED** (not obtained). |
| A3 | Seven chapters present and coherent | **PASS** | All seven anchors resolve; chapter nav lands every target at the same offset; the inquiry chapter was parking under the sticky nav on mobile and was fixed. |
| A4 | Franklin 1847/1848 document switching | **PASS** | desktop (mouse) and mobile (touch emulation): `aria-pressed` follows Original / Addition / Both. |
| A5 | Historical investigation chooser (Apollo 1 / Franklin / Malbone) | **PASS** | Exactly the selected case panel is visible, each of the three; arrow-key navigation works. |
| A6 | Observer Lab behaviour | **PASS** | Frame A/B toggles, answer disclosure opens/closes by keyboard. |
| A7 | Reading Trail edge-fade/progress states | **NOT TESTED in WordPress** | Existing source tests only; chapter navigation itself is PASS. |
| A8 | All 72 Hidden in the Margins entries | **PASS** | 72 unique indices 0-71 in the render; preserved blocks byte-exact (`production_preservation.json`); live page re-fetched and unchanged since the snapshot. |
| A9 | Jetpack subscription content preserved | **PASS (render)** | Markup identical to live; the Dispatch section is exactly the live height (444.08 px). **Submission, confirmation and delivery: NOT TESTED / BLOCKED** (the local form is deliberately inert; testing it means subscribing a real address to the production list). |
| A10 | Focus Fieldbook links | **PASS** | 4 `/focus/` links rendered (2 in the preserved block, 2 in the flagship). |
| A11 | Installed FV Focus Popup v0.1.1: shortcode, form, confirmation, download delivery | **NOT TESTED / BLOCKED** | The installed v0.1.1 source was not available; the draft v0.1.0 source was read (fail-closed: if the Jetpack form is absent the `/focus/` link stays visible, no timers/exit-intent/form listeners). Production read on 2026-10-31 found the shortcode on **no** page. End-to-end needs real Jetpack. |
| A12 | No dev controls / no direction switcher / no studio banner | **PASS** | No `.fv-hf__studio`, no direction attribute, no "DESIGN CANDIDATE / NOT LIVE" text. A visitor-facing leak ("draft review ... in this study") was found and replaced. |
| A13 | No horizontal overflow at 320 / 360 / 390 / 768 / 1024 / 1440 / 1920 | **PASS** | all seven. |
| A14 | 200% zoom and 400% reflow | **PASS** | Emulated as 640 and 320 CSS px viewports, no overflow. (Browser zoom UI not driven.) |
| A15 | axe: violations **inside the flagship** | **PASS** | 0 nodes at all seven widths. |
| A16 | axe: violations on the whole page | **FAIL (pre-existing, outside the flagship)** | 0-2 nodes per width, all in preserved production content: `color-contrast` on a rotating Margins strip item (320/360/390), `target-size` on a category-tag link in the lead block (1024+). Both exist on the live page today. |
| A17 | axe: incomplete (needs human review) | **NOT TESTED (manual)** | `color-contrast` 270-300 nodes per width (144-158 inside the flagship: text over gradients/imagery axe cannot judge); `aria-prohibited-attr` x2 (preserved Margins window, preserved Enter-the-record grid). Reported separately from violations, not counted as pass. |
| A18 | Keyboard-only | **PASS** | 40 tab stops sampled, 0 without a visible indicator; skip link first; Enter on a chapter link moves focus to the target section; focus never lands under the sticky nav once smooth scrolling settles. |
| A19 | Touch targets | **PASS (emulated)** | 0 flagship targets under 24 px, 3 under 44 px (was 17-18 under 24 px). Real devices: **NOT TESTED**. |
| A20 | Reduced motion | **PASS** | no running flagship animations, `scroll-behavior:auto`. |
| A21 | JavaScript disabled | **PARTIAL** | Evidence text, boundaries, sources, 8 `details`, all three cases, 72 Margins, 4 Focus links, Jetpack form: **PASS**. The three archival **photographs are not fetched** (Chromium does not load `loading="lazy"` images with scripting off) and only their captions show: **FAIL (P2)**. |
| A22 | Screen reader (NVDA/VoiceOver) | **NOT TESTED** | Not available in this environment. |
| A23 | Safari/iOS, Android devices | **NOT TESTED** | |
| A24 | Archival image bytes and identity | **PASS** | Transferred: Apollo 76,876 B, Franklin 301,260 B, Malbone 129,395 B (1440@1x) to 282,367 B (390@3x); all HTTP 200, image/webp. Identity vs originals (normalised cross-correlation): NASA S67-19766 0.9999, Wikimedia Commons Franklin file 0.9998, NYPL image 5003296 0.9982. |
| A25 | Image rights and attribution | **PASS (documented basis) / sign-off BLOCKED** | NASA: editorial use, credit + non-endorsement line added. Franklin: Commons public-domain-marked 1869 reproduction, distinguished from the museum object. NYPL: item states "believes ... public domain under the laws of the United States", requested credit "From The New York Public Library" added. No image replaced, none fabricated. Editorial/legal sign-off was not obtained. |
| A26 | Lighthouse (lab) | see table below | Not field Core Web Vitals. |
| A27 | WordPress theme/template compatibility | **PASS** | Official Assembler 0.0.126, public-safe page/header/footer templates, page ID 6 selector parity. **WordPress.com production behaviour: NOT TESTED / BLOCKED** (no staging on Personal). |
| A28 | Inline `<style>`/`<script>` in a `core/html` block survives on WordPress.com | **NOT TESTED / BLOCKED** | Needs one draft page in production (founder authorization). Existing blocks already carry `<style>` and a JSON-LD `<script>`. |

### Lighthouse (lab, simulated throttling, median of 3)

| Config | Perf | A11y | LCP | FCP | TBT | CLS | Transfer |
|---|---|---|---|---|---|---|---|
| Candidate, mobile, direct Playground (uncompressed, 0.9-1.6 s PHP-WASM TTFB) | 57 | 100 | 6.16 s | 3.08 s | 531 ms | 0 | 989 KB |
| Candidate, mobile, via gzip+cache proxy (isolates front-end cost; **not production**) | 75 | 100 | 4.58 s | 1.63 s | 278 ms | 0 | 648 KB |
| **Live homepage today, mobile (same config)** | 58 | 100 | 9.21 s | 3.07 s | 404 ms | 0 | 1,287 KB |
| Candidate, desktop, direct | 95 | 96 | 1.19 s | 0.61 s | 87 ms | 0 | 1,125 KB |
| Candidate, desktop, via proxy | 99 | 96 | 1.00 s | 0.43 s | 22 ms | 0 | 784 KB |
| **Live homepage today, desktop** | 96 | 96 | 1.42 s | 0.60 s | 0 ms | 0 | 1,843 KB |

Reading: the candidate is **not a regression** against today's homepage (lighter, same or better LCP), but **mobile LCP is above the 2.5 s target in the lab, as it is on the live page** (**FAIL vs target, P1**). Dominant cost is render delay (about 4.1-4.9 s of the LCP): the theme's 341 KB Inter variable font, 4x CPU style/layout on a very large DOM. Mobile TBT (248-541 ms, 4x CPU) is dominated by one long task of 345-500 ms attributed to `reading-trail.js`: its first `getBoundingClientRect()` call is the first thing to force the page's initial synchronous layout (about 19,000 px of DOM plus about 80 KB of inline site CSS), so that is the page's layout cost rather than the script's logic and moving it would not remove it. INP cannot be measured in lab; TBT is reported instead. **Field CWV: not measured** (no field data was used or invented).

## B. Synthetic / source-level

| # | Item | Result |
|---|---|---|
| B1 | `unittest discover` on `experience2/home-flagship/tests` (local Windows) | 71 of 77 pass; **6 errors are harness portability** (no `php` binary on this machine; four temp-directory write errors specific to Windows). Not product failures; hosted CI is the reference run. |
| B2 | Hosted CI on #550 `6ef459ec` and #565 `91ca7a7d` | `verify` success on both, `chromium` success on #565 (read from the API today). |
| B3 | Hosted CI on **this branch's exact head** | **NOT RUN YET** at the time of writing; recorded in the PR once opened. No pass is claimed. |
| B4 | `verify_archival_attribution.py` | `PASS_SOURCE_LINKS_ONLY` (its own output says rights_cleared=false by design). |
| B5 | Byte-for-byte preservation of live blocks 0,2,3,4,5 in the composed body | PASS (`verify_preservation.py`, live drift check: identical to the snapshot). |
| B6 | Original index-1 block rebuilt from the public snapshot hashes to the live `block_hash` `1c97fec5...` | PASS (rollback copy is verifiably the live bytes). |
| B7 | **Independent QD review** | **NOT PERFORMED.** No QD PASS is recorded or implied. |

## C. Blockers

**P0 - must clear before any release**
1. Independent QD review and green hosted CI on the exact final head (neither recorded yet).
2. Founder approval of the visual result on this integrated page.
3. WordPress.com dry run of the inline block (A28) on one private draft page; read `_content_warnings`.
4. Editorial/legal sign-off for the three images (A25).

**P1**
1. Mobile LCP above 2.5 s in lab (same as today's page). Candidate fixes: subset/preload the Inter font, shrink the DOM below the flagship (D1), defer the below-fold sections.
2. Focus Popup unverified; leave it unplaced (A11).
3. Pre-existing production accessibility: Focus CTA button `aria-label` ("Get the free Seven Day Focus Fieldbook") does not contain its visible text ("Get the free Focus Fieldbook"), WCAG 2.5.3, Lighthouse `label-content-name-mismatch`; Margins strip contrast; tag-link target size.
4. Screen reader, Safari/iOS, real-device touch (A22, A23, A19).
5. Manual review of the 144-158 incomplete flagship contrast nodes.

**P2**
1. Archival photographs absent with scripting disabled (A21). Fix: a `<noscript>` eager twin for each image, which requires updating six existing source tests that pin "exactly three `<img>`, all lazy".
2. Windows test-harness portability (B1).
3. The #580 CI lane runs Node 22 against a CLI that declares Node >= 24.18.
4. No affiliate-disclosure link in the Assembler footer (not needed while the page carries no earning links; required before any).
5. PR #49 `verify` is failing (frozen; not this release).

## D. Recommendation

**HOLD for publication. READY for founder visual review.**
The page is complete, rendered in real WordPress, preserves everything it must, and has zero axe violations inside the flagship at seven widths. What stops publication is not rework: QD, exact-head CI, founder approval, the WordPress.com dry run and image sign-off have not happened and cannot be done by engineering alone.
