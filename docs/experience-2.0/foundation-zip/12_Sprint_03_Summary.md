# Sprint 03 — reusable Source Ledger + WordPress staging adapter

**What was built:**

1. New accessible, source-backed Research Desk / Source Ledger with six documented Apollo 1 records, official NASA archive IDs and source links, explicit evidence limitations and native expandable historical details.
2. JavaScript-enhanced, keyboard-reachable search and live match count, with no JavaScript required to see records, expand details or follow links. No external framework, network or tracking.
3. Source URL allowlist (HTTPS only), required text and provenance fields, HTML escaping, duplicate ID checks, unique per-instance DOM identifiers, and a multi-instance isolation test.
4. Scoped CSS/JS, standalone `index.html`, copyable Gutenberg static block and a separate WordPress staging shortcode adapter. No production code touched.
5. Actual Chromium test coverage at 360, 390, 768, 1024, 1440, 1920px with screenshots; search, empty result, native details, no-JS mode, absent script and duplicate instances. PHP syntax checked.
6. New WordPress architecture, deployment/rollback, editorial and QA plan.

**Open gates:** founder visual direction; real WordPress staging test; actual NASA asset delivery/reuse rights; real VoiceOver/NVDA/manual WCAG; server-rendered content update strategy; 75p CWV; separate release PR and hosted green CI. A passing isolated browser test is **not** production approval.
