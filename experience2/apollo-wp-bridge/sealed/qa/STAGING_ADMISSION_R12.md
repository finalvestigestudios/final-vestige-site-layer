# Apollo Experience 2.0 — R12 authenticated staging admission (DRAFT / HOLD)

R12 adds a read-only HTTP admission probe and verifiable response-level source custody to the Apollo 1 private WordPress staging adapter. This branch is stacked on R11, not on homepage PR #49 or the independent Research Desk PR #158. It introduces no photos, geo pins, WordPress writes or production deployment.

## Exact provenance contract

After editor permission, environment opt-in, nonce and source-integrity checks, the private PHP response emits X-FV-EX2-Apollo-Source-Head, X-FV-EX2-Apollo-Fragment-SHA256, X-FV-EX2-Apollo-CSS-SHA256 and X-FV-EX2-Apollo-JS-SHA256. Each authenticated CSV/JSON export includes its own SHA-256. These values are derived from the exact pinned PR #215 source, SHA 74375657f2cdaac0710f94c6de6c24534ee06858, and its seven generated assets.

The new staging_admission.py probe performs GET requests only. It checks the actual staging page's sandboxed iframe, 403 denials for anonymous requests to the private page and all four exports, 403 for a tampered nonce, HTTP CSP/noindex/nosniff, six staged records in each major evidence component, source HTML/CSS/JS receipt digests, and four exact export downloads. It blocks finalvestige.com and ALL subdomains, requires HTTPS for external staging, refuses redirects, never sends editor cookies through configured proxies, and requires a private chmod-600 cookie file. The report contains no cookies, nonce URL or credentials.

## Reproduce in local offline environment

    python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p 'test_*.py' -v
    python experience2/apollo-wp-bridge/sealed/qa/browser_exact.py
    python experience2/apollo-wp-bridge/sealed/build_sealed.py --out /tmp/apollo-private-review.zip

For a SEPARATELY APPROVED genuinely distinct HTTPS WordPress staging host only, after an authorized release engineer installs the private staging plugin and creates a private review page containing the fv_ex2_apollo_sealed_preview shortcode:

    python experience2/apollo-wp-bridge/sealed/qa/staging_admission.py --origin https://YOUR-SEPARATE-STAGING-HOST --review-path /private-apollo-review/ --cookie-file /secure/editor-cookie.txt --report /secure/apollo-admission.json

Do not paste credentials, session cookies, or nonced URLs into GitHub or other reports. The probe never installs or activates a plugin and never changes WordPress content or settings.

## Local evidence and limitations

- 31/31 Python/PHP integration/security tests passed against the source-pinned generated PHP and a synthetic WordPress HTTP socket shim; the new probe also exercises tampered headers/CSP, wrong roles, production hosts, private cookie permissions and corrupted exports.
- 7/7 Chromium/Playwright widths passed (320, 360, 390, 768, 1024, 1440, 1920): keyboard skip, source navigation, filtering, no-JS content, touch, reduced motion and 200% zoom. Screenshots are reproducible via browser_exact.py.
- Lab LCP was observed at six widths (200–460ms); 1440 returned null. Lab CLS was zero. These are NOT hosted Core Web Vitals or p75 field results.
- Browser HTTP navigation to localhost is blocked in the current runtime (ERR_BLOCKED_BY_ADMINISTRATOR). Browser tests therefore use source-pinned in-memory CSP approximation; Python validates REAL localhost PHP HTTP headers and bytes, but browser-enforced HTTP/CSP remains unverified.
- A pinned and independently verified axe-core bundle was unavailable. The strict --require-axe release gate correctly fails closed. No axe certification is claimed.
- Safari/VoiceOver/NVDA, licensed NASA imagery usage, actual WordPress staging installation, production-adjacent transport, hosted CI on exact HEAD, independent QD and founder visual signoff remain outstanding.

RELEASE DECISION: HOLD. No merging, live WordPress changes, homepage work, paid services, or PR #49/#158 edits.
