# EX2 — Assembler saved-render evidence custody / 2026-11-03

**RELEASE: HOLD.** This is an isolated QA enhancement stacked **only** on PR #837 at exact head `1ff57f4ba414d276716ab6b3fb22c0580acec499`. Never merge, publish, install, or modify WordPress production/page 6 as part of this work. Frozen PR #49 at `10495883299d53596992c26a8987f629b2904670` is untouched.

## The concrete prior failures

Real synthetic WordPress/Assembler artifact in PR #823 (run `41692157470`) showed a 620px desktop canvas inside 1440px viewport, 72 unstyled invented Margins lines, and a serious whole-document navigation `list` axe issue. The CI timed out without no-JS or image-body completion. PR #837 saved an isolated CSS adaptation and keyboard-accessible test strip in a disposable Gutenberg draft, but **did not yet qualify its rendered output**. The current runner previously took screenshots only AFTER several structural assertions; failures could erase the screenshots needed to diagnose them. Its image requests checked HTTP bytes, not whether the browser actually decoded the archival images.

## Surgical QA improvements

1. Screenshot the *unaltered, saved* Gutenberg candidate at 320/390/768/1440/1920 **before** layout/anchor/Margins/axe assertions; produce an additional complete 1440px page screenshot. These are developer-only WordPress Playground images, not a deployed/live preview.
2. Capture 390px no-JavaScript screenshot. Verify CSS-computed Margins position, opacity and scrollability without relying only on DOM counts.
3. On 1440px, use actual Chromium `HTMLImageElement.decode()`, `naturalWidth`, `naturalHeight` and `complete` **and** a separately fetched complete HTTP response with status, MIME, byte length, SHA-256. Demand two distinct first-party archival file names. Cache duplicate responsive/decorative image requests so the test does not issue needlessly repeated downloads. Clear decode watchdog timers. Any failed decode, 404, HTML masquerading as imagery or empty body is a FAIL, never a green receipt.
4. Emit public-only media custody receipt to CI logs before whole-document axe so media proof is not lost when a known navigation issue blocks a pass. Whole-document axe and component axe remain fail-closed, and any failure remains a release HOLD.
5. Add ten dependency-free adversarial Node tests using a mock image/HTTP browser boundary; wire the tests into the existing isolated Assembler workflow. Tests validate instrumentation only; they cannot themselves certify network, theme, rendering, accessibility, rights or field Core Web Vitals.

## Evidence and hard limits

- Source under test: 11 original source-controlled flagship files via PR #816 plus isolated-only saved CSS/72 **synthetic** Margins and Jetpack stub via PR #837. Neither production page 6 export nor actual subscriber/Jetpack data is in the candidate.
- Test media: published Apollo 1 and Franklin source file URLs under `finalvestige.com` or WordPress image proxy `i0.wp.com`; the unverified NYPL Malbone capture is deliberately not admitted as media. Media rights are not established by loading images; NYPL capture-specific review remains unresolved.
- Predecessor artifact: #823 run `41692157470`, independently inspected. Browser-only layout bridge from #823 is **not** a saved CSS proof.
- Assembler theme version is fetched at workflow runtime, not pinned; archive sha and version must be recorded. The native WordPress.com staging clone is unavailable on the Personal plan. Playground is not WordPress.com Atomic/Jetpack parity, and `720px` CSS reflow is not physical 200% browser zoom.
- This branch does **not** fix the 620px layout or theme-navigation semantics. It forces evidence to be preserved and makes media/JS failures harder to conceal. Review screenshots/receipts from the new exact-head run before determining whether #837's saved CSS fixes layout.

## Gate for the next decision

A genuine **exact-head** GitHub Actions execution must finish the saved Gutenberg editor, verify draft deletion, render all five widths and 1440 full page, produce no-JS evidence, pass (or report specific) whole-document axe and browser media decoding. Then inspect screenshots manually for the three established art-direction principles, mobile composition, contrast and source-specific rights. Before any production release, separately test the real 72 Margins records, Focus Fieldbook/Jetpack signup, actual hosted image bytes, WCAG 2.2 AA manual/keyboard/touch/Safari/physical zoom, lab Lighthouse and independent QD, followed by explicit founder approval.

**No merge, no deploy, no plugin install, no production CMS/theme/navigation/settings edits, and no new subscriptions.**
