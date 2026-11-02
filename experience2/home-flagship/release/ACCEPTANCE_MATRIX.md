# Acceptance matrix - flagship release candidate (updated 2026-11-02, polish round)

Legend: **PASS**, **FAIL**, **BLOCKED** (needs a human or a signed-in session), **NOT TESTED**.
Section A is real WordPress + real Chromium on the **local** WordPress/Assembler stage. Section B covers WordPress.com. Section C is synthetic/source-level. They are kept apart on purpose.

**Target:** WordPress (Playground CLI 3.1.61, PHP 8.3) + official Assembler 0.0.126, page seeded as ID 6, **inline delivery** (the proposed production mechanism). Chrome 156 via Playwright, axe-core 4.10.2 (wcag2a/2aa/21a/21aa/22aa + best-practice), Lighthouse 12.6.1. Raw results: `evidence/`.

## A. Local WordPress + real browser

| # | Requirement | Result | Evidence / note |
|---|---|---|---|
| A1 | Integrated homepage in WordPress with Assembler; one header, one footer, one `<main>` | **PASS** | `screenshots/` |
| A2 | Monumental, legible first arrival at 390 and 1440 | **PASS (engineer review)** | CTA in first view at 1440x900. Founder visual approval of the artistic direction is granted in the authorization; sign-off on the final rendering: **not yet recorded**. |
| A3 | Seven chapters, anchors land clear of the sticky nav | **PASS** | desktop and touch; the inquiry anchor previously parked under the nav on mobile and was fixed |
| A4 | Franklin document switching, case chooser, inquiry accordion, Observer Lab | **PASS** | mouse (desktop) and touch emulation (390) |
| A5 | Reading Trail progress/active-chapter states | **NOT TESTED in WordPress** | chapter navigation itself PASS; flagship chapters deliberately not content-visibility-skipped so the trail measures real positions |
| A6 | 72 Margins, Focus links, Jetpack block unchanged | **PASS** | byte-exact preserved blocks 0,2,3,4,5; live page re-fetched and identical to the snapshot; Dispatch section same height as live |
| A7 | No dev controls, banner or direction switcher; no development copy | **PASS** | one visitor-facing "draft review" sentence was found and replaced |
| A8 | No horizontal overflow at 320/360/390/768/1024/1440/1920; 200% and 400% reflow | **PASS** | zoom emulated as 640 and 320 CSS px |
| A9 | axe violations, whole page | **PASS** | **0 violations at all seven widths** in the final run. Earlier runs showed one intermittent `color-contrast` node on a rotating preserved Margins item (animation frame dependent; settled colours are #d8d2c7 on #0f100f, about 12:1) and a category-link `target-size` node (now fixed by CSS). |
| A10 | axe "incomplete" (needs a human) | **PASS for the flagship (pixel-measured); NOT TESTED for preserved sections** | `contrast_audit.py` measured real background pixels under every flagship text node, with all three case panels revealed and the page covered in a head pass plus a tail pass (Chrome blanks full-page captures beyond 16,384 px): **0 below WCAG 1.4.3** at 390 px (208 + 62 nodes) and 1440 px (236 + 72). One real failure was found and fixed earlier ("APRIL 1848", 4.3:1). Preserved production sections are not pixel-audited; axe reports no violations there. `aria-prohibited-attr` x2 remain in preserved blocks (Margins window, Enter-the-record grid). |
| A11 | Keyboard-only | **PASS after a fix found by independent reproduction (2026-11-02)** | The original harness measured each stop immediately after Tab, before smooth scrolling settled, so 15 of 40 stops were not measured in view and the earlier "all 40 visible" statement was overstated. A settled re-test (60 stops at 1440 and 390 px) found the flagship's own **skip link was rendered behind the site header** when focused (`z-index:200`, below the theme header): a WCAG 2.2 AA 2.4.11 failure. Fixed in this head (`z-index:100001`); re-test: 59 of 60 stops visible, unobscured, with an indicator at both widths. The one remaining stop is the **preserved** Margins scroller (focusable `div`, 1px outline), identical on the live page. See `INDEPENDENT_REPRODUCTION.md`. |
| A12 | Touch targets | **PASS (emulated)** | 0 flagship targets under 24 px, 3 under 44 px; category links 24 px (44 px on coarse pointers). A review found my first 44 px summary rule had flattened the accordion headers from grid to inline-flex; fixed and re-verified (`grid` again, plain disclosures keep their marker). |
| A13 | Reduced motion | **PASS** | no running flagship animations |
| A13b | Fragment navigation into skipped sections (`#dispatch`, the target of the site header's Dispatch link) | **PASS** | lands with the section in view and the Jetpack form visible |
| A14 | JavaScript disabled | **PASS** | text, sources, details, all three cases, Margins, Focus links, Jetpack markup **and the three archival photographs** (3/3 load; verified with and without `<noscript>` twins, which were therefore removed). An earlier "photos missing" FAIL in this document was a too-short-wait harness artifact and is withdrawn. |
| A15 | Focus Fieldbook accessible name (WCAG 2.5.3) | **PASS at DOM level; NOT APPLIED to production** | axe `label-content-name-mismatch`: 1 violation -> 0 after removing the button's `aria-label` (`evidence/focus_label_fix.json`). Production fix is optional operation 2. |
| A16 | Screen reader (NVDA/VoiceOver/Narrator), Safari/iOS, Android devices | **NOT TESTED** | none available in this environment |
| A17 | Image bytes and identity | **PASS** | transferred 76,876 / 301,260 / 129,395-282,367 B; identity vs NASA, Commons, NYPL originals 0.9999 / 0.9998 / 0.9982 |
| A18 | Image rights and credits | **PASS (documented basis); sign-off BLOCKED** | `IMAGE_RIGHTS_REGISTER.md`; NASA item-specific conditions need a named editor |
| A19 | Focus Popup | **NOT IN RELEASE** | per authorization; installed v0.1.1 unverified, not placed on page 6 |

### Mobile performance (lab; not field data; no production WordPress.com measurement exists)

| Mobile config | Perf | FCP | LCP | TBT | Transfer / requests |
|---|---|---|---|---|---|
| **Candidate, final build**, Lighthouse simulate, via gzip+cache proxy (front-end only, not production) | 82 | 1.30 s | 4.58 s | 84 ms | 644 KB / 14 |
| Candidate, previous release build (head `5f87f1b0`), same config | 75 | 1.63 s | 4.58 s | 278 ms | 648 KB / 19 |
| Candidate, final, simulate, direct Playground (uncompressed, ~2 s PHP-WASM TTFB; not production) | 69 | 3.08 s | 6.08 s | 176 ms | 984 KB / 15 |
| **Live homepage today, simulate** | 58 | 3.07 s | 9.21 s | 404 ms | 1,287 KB / 33 |
| Candidate, final, Lighthouse applied throttling (3 runs, proxy) | 66-68 | 3.1-3.3 s | 3.1-3.3 s | 780-847 ms | 644 KB / 14 |
| Candidate, earlier builds, applied throttling (6 runs) | 61-82 | 2.6-3.2 s | 2.6-3.3 s | 437-1,225 ms | 530 KB / 12 |
| **Live, Lighthouse applied throttling (3 runs)** | 66-71 | 2.1-2.4 s | 2.8-3.2 s | 941-1,684 ms | 1,302 KB / 33 |
| Candidate, final, my throttled load trace (5 runs, proxy) | n/a | 1.36 s | 1.47 s | n/a | 719 KB |
| **Live, same trace (5 runs)** | n/a | 1.86 s | 1.97 s | n/a | 1,387 KB |

Desktop (final, simulate, proxy): perf 99, LCP 0.98 s, TBT 0 ms, CLS 0.01 (live 96, 1.42 s). Direct Playground: perf 94, LCP 1.27 s.
Reading: **no LCP regression against today's homepage and about half the transferred bytes, but the 2.5 s target is not met in the stricter lab modes (P1 exception), and in applied-throttling Lighthouse the candidate's first paint is later than the live page's (3.1 s vs 2.1-2.4 s) while its LCP is about equal.** Blocking time is lower only in simulate mode (84 vs 404 ms); in applied throttling the ranges overlap. The model-based LCP did not respond to font, preload, CSS or `will-change` changes I tested, so it is reported, not tuned; run-to-run variation between builds is about +/-0.5 s. What did measurably help: `content-visibility` on the long preserved sections. Minifying saved only ~8 KB and was not adopted. Lighthouse accessibility is 100 through the proxy and 96 in other configs on the candidate and on the live page alike: the two causes are preserved-content items (Focus button label, fixed by optional operation 2; frame-dependent contrast on the rotating Margins strip).

## B. WordPress.com (private draft 1902, authorized)

See `dry-run/WORDPRESS_COM_DRAFT_VERIFICATION.md`.

| # | Requirement | Result |
|---|---|---|
| B1 | Inline `<style>`, `<script>`, `<noscript>` kept by the WordPress.com editor and renderer | **PASS** (raw and rendered, no `_content_warnings`) |
| B2 | Hazard characters (`>`, `&&`, `<`, regex, template literals, `&amp;`) stored unaltered | **PASS** (draft `block_hash` equals local SHA-1) |
| B3 | Draft private and unpublished | **PASS** (signed-out visitor gets "Page not found"; status draft throughout) |
| B4 | Page 6 untouched; Jetpack/Focus unchanged | **PASS** (six block hashes, `modified`, `content_hash` identical before and after) |
| B5 | **Exact candidate block (108,155 bytes) inserted in the draft** | **NOT DONE** |
| B6 | Assembler header/footer/layout, seven chapters, interactions and screenshots on the WordPress.com render | **BLOCKED**: in-app browser not signed in to WordPress.com; credentials are not entered by the assistant |
| B7 | Lighthouse of the draft | **BLOCKED** (private draft needs authentication) |

## C. Synthetic / source-level and review

| # | Item | Result |
|---|---|---|
| C1 | `unittest discover` (local Windows) | 71 of 77 pass; the 6 errors are harness portability (no `php`, Windows temp paths). Contract check: 21/21. |
| C2 | Hosted CI (`verify`) | **success** on `71f1f23b9346e40f164bc7bf21ee998ebba2fcb5`; the final documentation-only head is re-run on the PR. Source CI only, not a browser run. |
| C3 | Preservation, rollback copies | Original blocks 1 and 2 hash to their live `block_hash` values; apply/rollback parameters in `PROPOSED_PRODUCTION_CHANGE.json` |
| C4 | **Independent QD review** | **NOT PERFORMED.** An automated fresh-context review of `71f1f23b` found one real regression and ten smaller issues, all fixed or narrowed (`INDEPENDENT_REVIEW.md`); it is not QD acceptance. |

## D. Blockers

**P0 - before any go-live request is granted**
1. QD acceptance of the exact final SHA (a named human reviewer).
2. WordPress.com authenticated render of the exact candidate on draft 1902 (B5-B7): needs a signed-in browser session.
3. NASA item-specific reproduction sign-off (rights register).
4. Hosted CI green on the exact final head (re-run after the last documentation commit).

**P1**
1. Mobile LCP above 2.5 s in stricter lab modes (about equal to the live page); applied-throttling first paint later than the live page.
2. Screen-reader, Safari/iOS and real-device testing not performed.
3. Preserved-section contrast not pixel-audited; two `aria-prohibited-attr` notices in preserved blocks.
4. Phase 2 length reduction deferred (`PAGE_LENGTH_DECISION.md`).
5. Reading Trail states not tested in WordPress.

**P2**
1. Windows test-harness portability (hosted CI is the reference).
2. No affiliate-disclosure link in the Assembler footer (not needed while the page carries no earning links).
3. PR #49 `verify` failing (frozen, not this release).

## E. Verdict

**HOLD.** The experience is complete, verified on a local WordPress, and every defect I could measure was fixed. It is **not yet ready to request go-live authorization**: QD acceptance, the authenticated WordPress.com render of the exact block, and the NASA sign-off are outstanding. Of these, only the WordPress.com render can be completed by engineering, and only after you sign in; QD and the NASA sign-off need people.
