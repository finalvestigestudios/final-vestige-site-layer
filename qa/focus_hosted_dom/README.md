# Focus — actual anonymous public browser QA (HOLD, no deployment)

Independent test-only site QA lane for the single active Seven Day Focus Fieldbook Complete Edition. This is not a design or WordPress edit.

**Gap addressed:** Existing draft PRs #282 and #535 identify respectively a WordPress REST-rendered conditional gift-script syntax discrepancy and a saved-source #subscribe-blog no-JS anchor risk. Neither demonstrates the defect in an actual logged-out production DOM. #133 covers public HTTP/PDF; this proposal covers the DOM only.

**Read-only Chromium cases:** 390px normal JS, 390px no JS, 1440px normal JS; logged out; 200 same-host route; one native Jetpack subscription block; fragment CTAs resolve to an actual DOM element; first conditional gift script parses in actual page; relevant page errors; horizontal overflow. All tests prohibit POST and query-string signup simulation, never enter an email, click submit, add a subscriber, or fetch confirmation/welcome mail. Public-page-only screenshots and sanitized failure receipts are retained 7 days. CI is bounded to 8 minutes; script no-JS behavior is determined from the actual server DOM, not merely saved Gutenberg.

**Limits:** No signup/double-opt-in/welcome-email acceptance, no PDF download/checksum/52-page validation, no screen reader, full WCAG, mobile physical device or field CWV certification. Public-host document checks are not a WordPress.com staging clone or publication approval. The service may remain temporarily inaccessible from external runners; in that event preserve diagnostic evidence and hold rather than invent an HTTP/browser outcome.

**Release:** HOLD regardless of pass. All changes are new files in isolated QA paths. No changes to WordPress, lead magnets, retired water pages, navigation, plugins, branding, source PR #49, QD controls, existing Claude branches, paid services, or subscribers. Do not merge/deploy. Review with Focus Issue #129 and site QA Issue #126.
