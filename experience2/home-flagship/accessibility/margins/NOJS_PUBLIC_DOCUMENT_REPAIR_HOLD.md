# EX2 public-host Margins no-JS admission: document-local repair (RELEASE HOLD)

Date: 2026-11-03. Base: PR #758 exact `f17d3c5f2922d573bb6fd60e8607e74824c10df0`. Parent #752 is stacked on #746. Frozen #49 is untouched.

## Source-grounded failure receipt

[Run 41607672350](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41607672350) **finished with a failing hosted-browser job**, not a pass. The uploaded evidence (artifact 13218560311, GitHub SHA-256 `30bff739ff7604dc1eee3b4293797589dd9f151cae5a2c58e6d18d9ae8312dc4`) records:

- Five hosted viewport probes **completed**: 320, 390, 768, 1440, 1920; actual HTTP 200; exactly 72 margins records; CSS-active; no measured document overflow; all eight phases assessed. Candidate visible text measured **12.678:1**, with no blur; the tested 390/1440 axe color-contrast rule had zero violations/incompletes.
- Reduced-motion + JavaScript-enabled probe **passed** with exactly record 0 visible.
- **Reduced-motion + JavaScript-disabled probe timed out at 90 seconds.** The job correctly marked `hosted_in_memory_candidate: FAIL`, with `contrast_axe_instrumentation: PASS`; the release was HOLD. This does not establish the timeout's exact root cause.

## Isolated change in this PR

The no-JavaScript branch no longer uses Playwright's after-navigation `page.add_style_tag()` to install test CSS. Instead, a GET-only interception of the *anonymous top-level public HTML response* adds the exact checked local style once, inside `<head>`, **in Chromium's in-memory response**, before parsing. This avoids requiring page scripts to install the fix in the no-JS scenario. It checks HTTP 200 / HTML content type, exact public-host document navigation, UTF-8, reasonable source bounds, the known flagship and Margins markers, a unique head insertion, and absence of a previous test overlay. The original content is never written to disk, GitHub Actions, WordPress or an output artifact.

Nonessential no-JS subresources (scripts/images/media/fonts) are blocked in the no-JS reduced-motion-only case to isolate the CSS fallback; all five full hosted-width/axe cases remain unchanged. Both reduced-motion cases must still show *only* record 0; all seven child cases remain individually bounded, with a checkpoint after each and strict fail-closed admission.

This is a *test-harness correction*, **not** an implementation of the fix on WordPress. It also does not prove that an unmodified production browser can load that test CSS without an eventual authorized release.

## Safety, rights and release boundaries

The public document GET is anonymous, WordPress writes and non-GET requests remain blocked; the NYPL Malbone image path remains blocked for inspection; no subscriber, visitor, cookie, WXR/database or user data is archived. The live page remains published in its previous state. This is not a full page-load, image-transport, field CWV, Safari, screen-reader or 200% zoom certification. WordPress.com Personal lacks a native staging clone; use the free isolated WordPress harness and hosted read-only checks rather than asking for a paid upgrade.

Release HOLD still requires independent QD, founder authorization, manually verified WCAG 2.2 AA, production provenance reconciliation, NYPL image-specific rights determination, cross-device QA and budget-qualified hosted performance. The candidate CSS remains isolated in #746 and is **not** installed, merged or deployed.

## Subsequent exact-head CI finding and deterministic phase correction

[PR #765 initial run 41616460236](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41616460236) at commit `be2b24756606ce41ebf39e7b401821a597508d74` saved [artifact 13221337659](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41616460236/artifacts/13221337659) with verified SHA-256 `257c682e97754cc50c71bd528ff24df507405ce3f62ae26778d4608a987ac1f1`. Seven of seven child cases completed **without a timeout or errors**. Both reduced-motion scenarios (JS disabled *and* enabled) passed with only record 0 visible. The five hosted widths still reported 12.678:1 candidate contrast; pinned axe 390/1440 reported zero color-contrast violations. **However overall hosted candidate remained FAIL** because all five viewport records sampled item 0 instead of 71 at test phase `359.5` seconds. All other seven of eight samples matched.

The phase test itself was non-deterministic: it set negative CSS animation delays, let the animation continue on wall-clock time, waited 95ms, then ran expensive DOM/computed-style inspection. The intended 359.5s sample is only 0.5s before wrap, and the browser can legitimately progress into the next cycle while measuring. An independent **local synthetic Chromium reproduction** demonstrated that the wall-clock sampling crossed the same boundary; setting the Web Animations `currentTime` and calling `pause()` on each candidate animation instead produced `[71]` at 359.5s and `[0]` at 360.5s without reliance on elapsed time. The second commit corrects this methodological defect while keeping the 359.5s prewrap assertion strict. This is a harness timing correction, not a change to the candidate CSS or the published site.

**New exact-head CI must still qualify the combined fix; no PASS claim until all seven hosted cases and all eight deterministic phases pass.** No changes to frozen #49 or public WordPress.
