# Final Vestige Experience 2.0 — archival gallery lazy-load admission correction

**2026-11-01 / DRAFT / RELEASE HOLD.** Isolated branch stacked on PR #420 exact commit `f0dde3509bc47633256e0067ab320565068c446f`. No production WordPress, theme, navigation, plugin, subscription, merge, deployment or frozen PR #49 writes.

## Source-grounded release-verifier defect

The source-controlled homepage `index.html` (Git blob `70ebe0d8e122048343c99a3c6adc6f7ac498ed7f`) contains **exactly three archival `<img loading="lazy">` elements** inside the Apollo, Franklin and Malbone case panels. `flagship.js` (blob `1888dbb5f77c348c43ddf2dbd276626459f19290`) sets inactive case panels `hidden=true` during progressive enhancement. Before this PR, `verify_playground_browser.py` (blob `f7b8c94d8692890b69cb46753490c59c22a92fc1`) demanded `e.complete && e.naturalWidth>0` for **all three** images after initial page load and **before switching to Franklin**, with no scroll-to-reveal. That admission sequence can falsely fail correct lazy-loaded hidden images even when the underlying WordPress stage and media are healthy.

## Surgical correction (not a redesign)

- New `archive_gallery_transfer.py` explicitly selects **Apollo, Franklin, Malbone** in that order, asserts the selected panel is actually visible, and scrolls **each image** into view before waiting for natural browser decode. It does **not** alter `loading=lazy`, force eager loading, rewrite URLs or mock network traffic.
- Requires exactly three images in the flagship, one per expected case, meaningful alt text and **no stray external `srcset`** surviving the first-party WordPress rewrite.
- Each decoded `currentSrc` must have the **exact isolated-stage scheme/host/port and `/media/<approved-name>` path**. HTTP response final URL must also remain on that same path/origin (redirects elsewhere rejected).
- Continues to require successful **real HTTP 200**, original expected byte count, decoded dimensions and independent pre-approved SHA-256 through PR #420's `verify_media_payload`. Does not generate its own purported trusted digest.
- Restores the Apollo default at the end so existing Franklin chooser, reading-lens, Observer Lab and keyboard chapter navigation tests retain stable preconditions.

## Verification performed / boundaries

Local Python 3 standard-library fake-Playwright regression runner: **6/6 passed**, including genuinely hidden simulated lazy cases, missing/extra case imagery, empty alt, external srcset, production-origin and redirected media, bad HTTP, same-size altered payload and missing independent media identity. The exact two new GitHub file blob identities were cross-checked against local `git hash-object` values. The modified actual WordPress browser runner was re-fetched at its new blob identity; the four existing interaction checks remained present.

These are **mocked protocol and source-sequence tests**, not an assertion that the WordPress installation, real photo downloads, third-party license checks, axe, Safari or Lighthouse passed. Actual localhost/Playground Chromium navigation still returns `net::ERR_BLOCKED_BY_ADMINISTRATOR` in the current execution container, and original media SHA custody/Assembler installation remain unavailable here. Lab checks and founder visual signoff stay **HOLD**.

## Reproduce against exact checkout

```bash
python -m unittest discover -s experience2/home-flagship/qa/playground -p 'test_archive_gallery_transfer.py' -v
python -m unittest discover -s experience2/home-flagship/qa/playground -p 'test_integrated_admission_checks.py' -v
python experience2/home-flagship/qa/playground/verify_playground_browser.py \
  --url http://127.0.0.1:8080/ \
  --trusted-media-manifest /private/independently-reviewed-originals.json \
  --axe-js /private/verified-axe-core.js \
  --output-dir /private/fv-integrated-stage
```

Execute the browser command **only** against a real isolated WordPress/Assembler instance with the complete public-content-preserving page-6 candidate, no subscriber/credentials export, independently authenticated original images, and a legitimate axe-core file. Host-specific Jetpack and real-user CWV need separate review. Never run this admission against `finalvestige.com`.

**Release decision: HOLD — no staging execution, independent QD approval, CI green or production authorization.**
