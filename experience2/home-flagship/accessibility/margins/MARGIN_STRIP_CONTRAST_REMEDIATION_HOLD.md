# Final Vestige page-6 Margins: contrast-safe rotating evidence candidate

**HOLD — isolated source-controlled remedy; NOT deployed or authorized.** Companion to hosted anonymous axe/interaction audit PR #739. The image-rights, publication-authorization, independent QD, and manual accessibility gates remain outstanding. Frozen PR #49 is untouched.

## Observed failure in real source
Read-only WordPress.com page **6** returned `status=publish`, `modified=2026-11-02T17:48:13`, and **72 original** `span.fv-margin-strip__item` records. Its first Gutenberg block uses a **360s** `fvMarginReveal` animation with **5s** staggering, `opacity:.46` and `opacity:.42` while `filter:blur(5px/4px)` is active. At normal 12–13px text sizes those transitional states can fail the 4.5:1 text contrast minimum. The separately reviewed hosted PR #739 axe audit flagged the strip at **390px and 1440px**; that evidence triggered this narrowly scoped remedy.

## Corrective design
`margin_strip_contrast_safe.css` overrides the text reveal with full-opacity, blur-free, **discrete visibility transitions**, while keeping the existing typography, antique parchment color, obsidian strip, 72-slot rhythm, hover/keyboard-focus pause, mobile breakpoints and reduced-motion first-record reading. The dramatic reveals elsewhere in the seven-chapter flagship remain untouched. This minimizes editorial disruption while eliminating the identified faded-text state.

**The patch is intentionally a separate stylesheet, not a WordPress modification.** If a specific release is eventually authorized, an editor can review placing it **after** the existing strip stylesheet on page 6 and run the exact hosted acceptance suite. Do not blindly paste it into production or replace the 72 fragments.

## Offline experiments and limits
`probe_margin_strip_contrast.py` embeds the source-inspected strip rules, then generates **synthetic text** in 72 slots. It checks original-versus-candidate timing, CSS computed colors and visibility, blur, document overflow, 10 phases including 360s wraparound, and 5 Chromium widths: **320 / 390 / 768 / 1440 / 1920**. Reduced motion is exercised with JS enabled and disabled; 11 independent source tests check guard conditions. The test includes no archive photographs, direct affiliate links, original historical passages, subscriber data, live passwords, WordPress credentials, or site writes.

Run:
```sh
cd experience2/home-flagship/accessibility/margins
python -m unittest -v test_margin_strip_contrast_safe.py
python probe_margin_strip_contrast.py --output CONTRAST_QA_RECEIPT.json --screenshots ./screenshots
```
The tests use Playwright and installed Chromium. Exact-checkout CI pins Playwright. A passing **fixture** is not a full homepage render, axe scan, VoiceOver/NVDA assessment, hosted WordPress.com compatibility check, Lighthouse measurement, or proof that the correction is already visible to site visitors. The JSON remains `release_gate: HOLD` even on fixture PASS.

## Release work still required
A separate authorized publisher must first reconcile current published revision 1914 and its NYPL reproduction against image-specific rights and founder release approval. Then repeat hosted PR #739's axe/interaction matrix with the fix, independent QD at exact SHA, keyboard and assistive-technology manual audit, Safari/touch and no-JS checks, and hosted performance measurement. Preserve the Focus Fieldbook, Jetpack signup, 72 Margins records and seven original chapters. **No prod release approval is contained in this PR.**

Handoff to Site QA: this is a CSS candidate for the *site-shell Margins* defect; coordinate before any edits to the live page and avoid concurrent WordPress writes.