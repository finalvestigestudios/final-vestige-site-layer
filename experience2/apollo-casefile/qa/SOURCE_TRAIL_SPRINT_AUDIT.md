# Apollo Evidence Studio: source custody / Research Desk delivery (2026-10-30)

**UNPUBLISHED STAGING ONLY.** Built on Apollo custody PR #189 at 939ab52c45f85203f190da79c9903be07a94d92b, itself stacked on gallery PR #185 and casefile PR #181. Separate Research Desk plugin PR #158, frozen homepage PR #49, all homepage design branches, live WordPress and its settings remain unchanged.

### Implementation and original sources

- Six historically bounded NASA source custody records now deterministically generate actual CSV and JSON files from the SAME versioned source manifests as the casefile HTML. Each record includes exact Board locator, claim certainty, what is and is not established, NASA image catalog ID, verified image date/credit/source link, source-policy URL, explicit image-reuse hold and no geographic coordinate. Board records, contextual photo descriptions and subsequent NASA response are distinct.
- Real Research Desk download panel with native disclosure explaining evidence/rights boundaries. Gallery → source and claim → stage links now open the correct native details with keyboard focus. Visiting a filtered-out claim hash resets the optional claim filter and focuses the restored card. All source content remains present with JavaScript unavailable and when observer initialization fails.
- The links in the generated standalone HTML to CSV/JSON are relative and work only when all files are served from the SAME directory; final WP staging must independently confirm stable asset URLs, caching and actual downloads.
- No NASA photographs/logos embedded or downloaded; this is not NASA endorsement or asset-level rights clearance. No invented map pins, geospatial relationship edges, paid services, external tracking or outbound dependencies.
- Official documentary sources: NASA Apollo 204 Board report https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; NASA findings https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html ; subsequent NASA response https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/ ; NASA image/media guidelines https://www.nasa.gov/nasa-brand-center/images-and-media/ . Six individual NASA photo catalog pages remain linked in records.json. All claims are sourced to Board reconstruction, NOT photo telemetry.

### Reproducible verification actually executed

From the casefile directory: run python render.py, python qa/source_trail_gate.py and python qa/source_trail_playwright.py (requires Python Playwright and Chromium at /usr/bin/chromium). Also executed PASS: python qa/verify_determinism.py, python qa/verify_claim_custody.py, python qa/verify_browser.py, python qa/verify_claim_browser.py, python qa/a11y_audit.py, python qa/measure_perf_lab.py, python qa/verify_accessibility_tree.py.

- Generated HTML 80,859 bytes SHA256 **3e55bf0d80011d894131ce619a2ad88590b708425498f16a92e904e96e81f4b6**; CSV 6,737 bytes SHA256 **8fe343e80e560af6ec021144e38ae8edbad558fba531bf1ff45ccf06c90c1ed0**; JSON 9,706 bytes SHA256 **60941d48649f68add5ab5d5ca47be68ab7eb7a56a859de2e33de937caaf92c85**. Repeat build hash identical.
- Actual installed Chromium/Playwright in-memory browser at **320/360/390/768/1024/1440/1920**, no overflow, native/source and category/claim deep links, keyboard focus and touch at 390, search/filter/empty/reset, 200% zoom, disabled JavaScript and missing/throwing observer, reduced motion, complete static content.
- Local DOM/target audit checked **126 visible interactive controls per width, across seven widths**, with **zero** target sizes smaller than 24px, missing accessible names, duplicate IDs, broken ARIA relations or unsafe source links in the inspected states. Real Chromium AX-tree smoke verified native disclosure expanded-state exposure at five widths. **No axe-core run or WCAG certification**.
- Synthetic local set_content PerformanceObserver LCP samples (not page navigation or field CWV): **320=236ms, 390=120ms, 768=116ms, 1440=168ms, 1920=136ms**, CLS 0; no real network photos/fonts. HTTP navigation returned **BLOCKED_BY_ADMINISTRATOR**; no INP/p75 result.
- Seven source/content/exports committed Git blob SHA-1s were independently re-read at first commit **36fe80b769cea7fb805b20bdfd7f0ab43019f06b** and matched the actual locally tested code/file content.

### OPEN release blockers

Verified axe-core bundle unavailable; network DNS retrieval blocked, so automated axe is **NOT RUN**. Manual NVDA/VoiceOver/iOS Safari and real mobile touch/forced colors remain outstanding. NASA each-image reuse, third-party credit and recognizable-person rights NOT cleared. No WordPress Assembler integration or downloadable hosted asset links, production/theme field LCP/INP/CLS, hosted CI on exact final SHA, independent QD or founder art-direction/release approval. All deployment on HOLD.
