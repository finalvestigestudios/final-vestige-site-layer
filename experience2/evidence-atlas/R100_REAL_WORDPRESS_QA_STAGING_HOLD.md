# Apollo R100 — Genuine, Disposable WordPress Core Acceptance (STAGING HOLD)

**Tracking:** Experience 2.0 Issue #150. Starting point is R99 draft PR #834, exact parent `ac31878c0586dd1352b3d370dd63356af5be4486`; Research Desk original PR #158 remains untouched.

## Engineering purpose

The R99 preview was verified with a PHP-based *WordPress hook contract shim*, not with an installed WordPress instance. That distinction matters: WordPress authentication, native `template_redirect` integration, shortcode registration, plugin activation, and actual WP headers/cookie behavior need independent verification before any hosted-platform claim.

R100 adds a dedicated **real WordPress core integration lane**. A GitHub-hosted disposable Ubuntu runner installs pinned WordPress core 6.8.3 into an ephemeral filesystem and MariaDB service, creates two synthetic accounts, activates the hash-pinned R99 private plugin **there only**, and drives genuine localhost HTTP routes in Chromium. No production, hosted WordPress.com, site settings, homepage branches, or paid services are touched. The runner's temporary WordPress installation necessarily writes its own isolated setup database; it is destroyed with the runner. The tests themselves do not write WordPress posts, pages, options, or settings.

## Scope and acceptance

- Source chain rebuilds through R92/R93/R94/R97/R98/R99 twice; archives must be byte-identical before installation.
- WordPress functions are from real installed WordPress, not shims. `fv_apollo_r99_review` shortcode exists; unprivileged shortcode displays the safe fallback; no public-facing post is created.
- Anonymous and subscriber requests to private HTML/JSON/JS must return 404. An editor-capable administrator can access all seven source views.
- Actual `template_redirect` responses must include no-store, noindex, CSP and appropriate MIME, and reject array parameters, path traversal, unknown or unlisted assets.
- A modified CSS byte must be rejected under the source-pin SHA-256, then access restored after the test reinstates original bytes (ephemeral fixture only).
- Real Chromium 320, 390, 768, 1440 and 1920 px, JS on/off, touch simulation, reduced motion, source content/no overflow/no unexpected external HTTP, native cross-document Enter navigation.
- Separate axe contexts allow diagnostic script injection while ordinary browser contexts inspect the **unchanged strict response CSP**. Six axe passes across mobile/desktop hub/atlas/gallery.
- Local LCP/CLS instrumentation reported as **lab values, not real-user Core Web Vitals**; native Chromium PDF checked for NASA URLs and six photo-specific rights warnings. QA evidence contains screenshots and SHA-256 receipts.

## Honest limitations

This workflow, even when green, proves only **real disposable WordPress core**. It does not prove Assembler theme rendering or hosted WordPress.com behavior, physical devices, NVDA/VoiceOver, third-party NASA photographic rights, independent editorial judgment, or release authorization. `S67-19766` remains a provisional crew-portrait association. No photos or speculative map pins are introduced. No deployment, activation on live WordPress, changes to PR #49, or publication is authorized. A failing or pre-runner workflow is **not** a QA pass.