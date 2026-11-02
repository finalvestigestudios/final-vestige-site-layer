# Experience 2.0 — staging candidate decision and actual-browser admission matrix

**Status: HOLD / UNPUBLISHED / NO CMS WRITES.** This is a release-engineering review, not a homepage design change or production permission. Applies to the complete existing seven-chapter Experience 2.0; no further standalone chapters should be added until integration is demonstrably reviewable.

## Canonical source and ownership

- Immutable frozen v1 PR #49: `10495883299d53596992c26a8987f629b2904670`. **Never modify this branch.**
- Seven-chapter visual prototype, Reading Trail: PR #217 head `c1c00acfa79664163214e1f424a8868e64aa2ee3`.
- Private staging alternatives: PR #224 `340393aefa8bc745985d17e1c2447ddafecaa92b` and PR #225 `7741595191d733f779cc05586accb1e7a4926bb4`.
- Source/rights gate: PR #231 `196e6bbc63ac7b3bab5197bfb2bd4392a044f360`.
- Apollo Research Desk PR #158 is independently owned; Mind & Perception issue #171 is editorial/affiliate, not a homepage checkout integration.
- Existing production WordPress page ID 6, 52-page Focus Fieldbook, Jetpack signup and 72 Hidden in the Margins entries must remain unchanged. No merge or WordPress operation is authorized here.

## Which staging renderer? Prefer PR #225; do not install either yet.

PR #212's unpublished preview ZIP exposed source assets as directly addressable .txt/.css/.js in the plugin webroot. **Neither that ZIP nor production WordPress is an acceptable staging test target.**

PR #224 and #225 both remove such public assets and require nonproduction WP, opt-in, editor capability, nonce and an Ajax renderer. However, they differ in meaningful reviewed behavior:

| Acceptance property | PR #224 sealed variant | PR #225 private variant |
|---|---|---|
| Packaged HTML/CSS/JS | Compressed PHP constant | Guarded PHP data payload |
| Exact asset manifest | SHA-256 check on decompressed assets | SHA-256 check on decoded assets plus exact key-set match |
| Unexpected CSS `</style>` | **Not explicitly rejected** before inline substitution; breaks HTML style boundary | Explicit fail-closed rejection |
| Unexpected JS `</script>` | Backslash substitution rewrites source bytes | Explicit fail-closed rejection |
| Executable remote refs | Rejects relative `src="./` / `href="./` leftovers; no general remote script src rejection | Explicit final check against script `src` and stylesheet links |
| Local genuine HTTP/PHP status/nonce tests | Primarily CLI PHP and fixture Chromium | HTTP PHP router, negative authorization/nonce/tamper cases; Chromium fixture |
| Browser-enforced CSP | Unverified | Previously unverified; new **meta-CSP subset** rehearsal below |
| Actual WordPress/Assembler staging | **NOT TESTED** | **NOT TESTED** |

**Recommendation:** keep PR #225 as the single primary provisional staging candidate. Hold PR #224 as an unmerged alternative; require equivalent CSS/script boundary and remote executable checks before considering it for deployment. This is a technical comparison, **not** a permission to install #225. The PR #225 media policy is not permission to use archival photographs commercially.

## Independent new local verification: nine adversarial tests

Run `python -m unittest discover -s experience2/home-flagship/qa/integration/private-preview/tests -p test_adversarial_csp.py -v` from any complete checkout containing the required PHP, builder and test file. Playwright's Python API, `php` CLI and Chromium must be installed; failures do **not** silently skip the browser case.

Tested locally October 30, 2026 with **PHP 8.4.24** and **Chromium 144.0.7559.96**. **9/9 PASSED** on a *small generated 11-asset fixture* using the **exact PR #225 PHP and builder bytes**. Blob SHA-1:

- PHP `fv-ex2-private-preview.php`: `52e03f839f7bc5fc4f8fc1e2ee53bf5102b9b8bc`.
- Builder `build_private_preview.py`: `0f138071a5df27609d216d507421c9d343890a99`.
- New adversarial test `test_adversarial_csp.py`: `bf8eeeb6b889db7e56acdbcd1b08c6d500e686b3`.

**Positive controls:** composer's 6 nonce-authorized CSS + 4 ordered body-tail JS assets assemble correctly. **Negative controls:** recomputed-hash CSS-style breakout, recomputed-hash JS-script breakout, extra signed asset, duplicate CSS declaration, foreign remote executable script, missing source asset are all rejected before publishing HTML.

**Real Chromium** at 390 and 1440 CSS pixels enforced a **meta CSP** with a fresh nonce: all four source-authorized inline scripts executed; a separate injected inline script did **not** execute, and Chromium emitted a CSP violation. The test runs with reduced-motion emulation. This is a real browser security assertion, but the fixture does not represent the actual page's visual layout and does not prove HTTP header-based CSP, iframe sandbox, cookies, image loading, WordPress behavior, accessibility or Core Web Vitals. Chromium in this execution environment blocks `file:`, `data:`, localhost and test-domain navigation, so synthetic `set_content` is the only tested rendering path.

### WordPress staging availability: independently checked

Authenticated WordPress `user-sites` listing with **`environment=all`** returned **exactly one accessible site**: public production `finalvestige.com`, blog ID `256784396`, theme `assembler`. No staging or test site was available through this account's connection. This does not prove there is no separate staging site outside the connection. **Do not upload the staging plugin to the production installation.**

## Exact staging requirement, no substitutions

The next authorized test needs a **separate access-controlled WordPress installation** (staging, development or local) with the Assembler theme and an editor-capable reviewer; an explicitly permitted, non-public deployment path; ability to set `WP_ENVIRONMENT_TYPE=staging` and define `FV_EX2_ALLOW_PREVIEW=true`; and an approved route to install the **exact ZIP built from a clean, recorded Git checkout**. A public page, draft on production, fake staging screenshot, or simply adding a shortcode to production does not satisfy this requirement. Keep test site noindex and behind access control. It must not deliver newsletters, analytics or checkout links to visitors.

Actual staging run must record: checkout HEAD, source-file SHA-256, ZIP SHA-256, exact installed plugin bytes, temporary test URL, WP/PHP/theme versions, timestamp, authenticated test identity class (no private passwords), screenshots and failure logs. **Do not claim a ZIP's supplied 40-character `expected-head` is independently attested by either builder:** both accept a caller-supplied label; confirm `git rev-parse HEAD` and clean tracked source in the real checkout, then cross-check the manifest.

### Acceptance matrix — no release without executed results

1. **Access:** anonymous, subscriber, editor without flag, wrong nonce, production environment, tampered data, direct payload URL; expect 403/503/blank and zero source leakage as appropriate. Check actual browser `frame-ancestors`, iframe sandbox and cookie behavior.
2. **Full exact source:** only seven chapter targets, original three image records, real citations, article/reader landmarks, native details, no-JS fallback, correct art-direction, observer/lens/reading-trail behavior and no external executable sources.
3. **Browser composition:** 320, 360, 390, 600, 768, 1024, 1440, 1920 px; 200%/400% reflow, touch, keyboard, reduced motion, mobile Safari, screen reader and axe; capture *whole-page screenshots* and before/after differences on the same genuine staging URL.
4. **Network/media:** all three first-party image requests, loaded pixel dimensions, actual transfer sizes, srcset choice and network errors recorded from genuine staging HTTP, not the uncompressed NYPL original's file size. Image failures must leave source text available. Do not infer commercial reuse rights from uploaded WordPress captions.
5. **Measured performance:** Lighthouse report (URL, device, throttling, build ID and raw JSON) and **real field** p75 LCP, INP, CLS when enough actual sample data exists. Do not invent values or treat synthetic DOM screenshots as CWV evidence.
6. **Release governance:** image-by-image independent rights signoff (NYPL individual item pending; NASA non-endorsement context; Franklin source custody), exact-SHA hosted CI, independent QD PASS, source cleanliness, explicit founder visual signoff and separately scoped production authorization.

### Production and editorial protections

The homepage's archival chapters and original source links remain central; the observer section may point editorially to the published Puységur work and existing Focus Fieldbook. No unverified Inspire3 earning claims, direct affiliate checkout URLs, merchant pitches or undisclosed offers are authorized. No additional recurring cost, production CMS write, merge, plugin activation, theme/menu edit or publication occurred in this test sprint.

**Decision: HOLD.** This document resolves a staging-candidate selection question and adds independently executable security evidence. It does **not** resolve the missing actual staging environment or allow launch. Track homepage in Issue #150, GitHub Actions dispatch in Issue #75 and ruleset/branch controls in Issue #191.
