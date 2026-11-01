# Apollo Experience 2.0 — R48 source-identity bridge (STAGING / HOLD)

R48 closes a Research Desk/Atlas co-hosting gap **without changing PR #158, the homepage, or WordPress**. When both components share one page, optional Atlas shortcuts appear only after the Research Desk passes exact six-source catalog, original NASA URL and record-ID matching. A Research Desk search that hides a destination is cleared before navigating; the target receives keyboard focus. A missing, duplicated or altered Desk withdraws only the optional links. The original six NASA references remain readable with and without JavaScript.

R48 also pins all six original catalog/URL pairs within the Atlas enhancement so a DOM change that mutates an external source link **and** its citation cannot pass a mere mutual-consistency check. Server-side shortcode template SHA-256 is updated to 6530e0557b760a34659767313600edaa9c4c9d5b4bc394fbdc610d7170c5dfb4. This is a build/DOM-drift guard, not a defense against malicious executable scripts.

### Reproduction

- python -m unittest discover -s experience2/evidence-atlas/tests -p 'test_*.py' -q
- python -m unittest discover -s experience2/evidence-atlas -p 'test_atlas.py' -q
- python experience2/evidence-atlas/tests/browser_r48_smoke.py
- php -l experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php
- node --check experience2/evidence-atlas/atlas.js

Actual Chromium uses real PHP-rendered Atlas shortcode HTML plus Git-blob-pinned PR #158 Research Desk JS (blob 32e757cc4dc8708397ff65ac21e89dd319781d), **but synthetic Research Desk HTML generated from the R37 NASA custody register**. Full actual joint WordPress/Assembler co-installation is NOT tested. Chromium HTTP/file navigation was blocked by administrator policy. A separate repeatable extended browser QA package includes 19 Chromium configurations/adversarial results, 390/1440 screenshots, and set_content-only LCP/CLS lab observations; these are NOT production CWV data.

Six individual NASA photo-rights reviews remain pending, so zero photographs are embedded. No invented geo pins, map edges, image licenses or causal links. No external requests, geolocation, analytics, paid services, deployment, WordPress content/settings write, or release approval.

**RELEASE HOLD:** authentic WordPress/Assembler staging with both real plugins and original image rights, pinned axe-core, NVDA/VoiceOver/Safari, hosted LCP/CLS/INP, exact-head CI, independent QD and founder signoff. Preserve frozen homepage PR #49 and independent homepage branches.
