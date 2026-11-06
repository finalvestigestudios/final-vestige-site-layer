# Apollo R159 — CSP/SRI external-assets staging candidate

**State: BUILT; OFFLINE PHP/CHROMIUM TESTED; NOT WORDPRESS TESTED; NOT LIVE.** Issue #150 / #820 / business charter #818. Standalone branch based on Apollo R158 at `23605b23a4b33eafabbc41650e513ae9142ff02a`. Does not modify the frozen homepage PR #49, Research Desk PR #158, or production.

## Concrete blocker and change
R158 emitted inline `<style>` and `<script>` from inside the shortcode. A WordPress site with `script-src 'self'` / `style-src 'self'` CSP could reject this, even though the R158 PHP/Chromium shim passed without CSP. R159 emits a regular stylesheet `<link>` and deferred JavaScript `<script src>`, each with SHA-256 Subresource Integrity. It uses WordPress `plugins_url(..., __FILE__)`, loads where the shortcode renders (including nested/reusable blocks after `wp_head`), verifies source bytes in PHP, and leaves six archival records in original HTML when JS is off or blocked. Missing/mutated inputs return only the historical investigation link. A second shortcode returns an anchor to the first, not duplicate IDs or scripts. No third-party host, tracking, data storage, CMS write, or commercial activation.

## Reproducible build (fresh checkout of this branch)
```bash
python experience2/apollo-r159/build_staging_package.py --repo . --out /tmp/fv-r159-a
python experience2/apollo-r159/build_staging_package.py --repo . --out /tmp/fv-r159-b
sha256sum /tmp/fv-r159-*/fv-apollo-r159-wordpress-staging.zip
php -l /tmp/fv-r159-a/fv-apollo-r159/fv-apollo-research-desk.php  # after unzip, if desired
python experience2/apollo-r159/test_csp_browser.py --package /tmp/fv-r159-a/fv-apollo-r159-wordpress-staging.zip --out /tmp/fv-r159-browser
```
For audited offline replay, `--r158-zip <verified R158 package>` replaces `--repo`. Base package SHA-256 is pinned to `8d7cef94b83917fa6b8eb555e1b2a077cafd324e1d7372a5ac5d4433a753c0c2`. Local R159 reproducible ZIP SHA-256: `08e633bcc07f8d29cd2aebac5c7b9d945d9040da5a6e35a4f2bed60815defbc3` (11,832 bytes). Source assets from R158 are unchanged.

## Recorded offline acceptance (2026-11-05 PT)
Real Chromium / PHP CLI with simulated WordPress APIs, six widths **320, 360, 390, 768, 1440, 1920**. Two independent runs: **138/138 assertions PASS per run; six screenshot SHA-256 hashes reproducible**, no unexpected Chromium errors. Includes search/filter, keyboard SourceDrawer, fragment focus, touch context, reduced motion, six sources without JS, external link preservation, duplicate shortcode behavior, server SHA-256 mutation fallback, and browser SRI mutation rejection. Offline PerformanceObserver last-LCP 88–104ms, CLS 0 (nonrepresentative lab values; NOT production CWV). Full machine receipts/screenshots are in the downloadable evidence bundle, not installed on WordPress.

**Critical limit:** This execution environment blocks Chromium navigation to HTTP(S) and file URLs (including route interception). The browser runner therefore substitutes only CSS/JS *transport URLs* with identical `data:` bytes and applies a restrictive `script-src data:` / `style-src data:` CSP. This verifies executable browser behavior, SRI refusal on unexpected bytes, and absence of inline code, but **does NOT prove same-origin `'self'` CSP compatibility**. Real WP staging tests must use origin-served assets and the site's actual response CSP headers.

**Not done:** axe-core is unavailable and was **not executed**; NVDA/VoiceOver manual audit, zoom, actual Assembler theme and nested shortcode behavior, restrictive production CSP (including nonce/strict-dynamic), real media access, field LCP/INP/CLS, hosted CI exact-head, and independent QA are not passed. No live deployment, plugin installation, post changes, Google Analytics additions, or purchases. SRI does not protect HTML semantics or replace source-rights clearance.

## Flagship / trust / conversion contract
Flagship: **Apollo 1: Fourteen Seconds, More Than One Failure**; Grok's history audience and secondary educators are the intended segment. Only visible next step: **Read original investigation**. A purchasable Apollo educator dossier remains a **hypothesis**, not an authenticated Payhip SKU; do not add a checkout CTA or imply NASA endorsement. NASA source photographs are contextual, not the technical proof; Apollo 204 Review Board findings are the documentary anchor. Archival imagery is **not cleared for product covers, paid packaging or advertising**. Source/rights guidance: https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/.

**Offer → funnel step → blocker → proposed change/experiment → evidence → owner:**
1. Educator dossier → checkout → no verified SKU/merchant acceptance/rights → audit existing inventory and checkout before CTA → **BLOCKED** → Claude/Growth + founder.
2. Grok Apollo long-form → Atlas → unverified `asset_id`, UTM and posted URL → reconcile TASK-008 in existing Praxxis/Grok Drive handoff → **NOT VERIFIED** → Grok/Praxxis.
3. Research Desk → evidence/navigation → inline CSP incompatibility → external SRI staging candidate → **BUILT / OFFLINE BROWSER PASS** → Apollo.
4. Purchase → net revenue → no verified attributable Apollo sales → reconcile merchant orders, refunds, fees, unique qualified sessions (7/30-day cohorts) → **NOT COMPUTABLE** → Analytics.

## Release hold
Actual WP staging with nested blocks, 320–1920, axe-core (0 violations and 0 incomplete), manual screen readers and 200%/400% zoom, recorded network/media/CSP responses, production-like field performance and offline rollback are mandatory. Independent QA + exact-head hosted CI + founder/Claude authorization precede any merge, install, external link activation, or live site write.
