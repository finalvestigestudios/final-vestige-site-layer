# Focus no-JS anchor audit (read-only)

Use this small offline guard against an **authenticated, local, private** export of a WordPress page's saved `content` (`context=edit`). It reports same-page fragment links whose `id` is missing from **saved static HTML**, even if a JavaScript helper constructs the anchor later. It neither fetches nor uploads anything and never prints source content.

```sh
python3 -m unittest discover -s qa/focus_nojs_anchor -p 'test_*.py' -v
python3 qa/focus_nojs_anchor/focus_anchor_guard.py /private/wordpress-focus-page.raw.html
```

A flagged anchor is a **browser acceptance candidate**, NOT proof of a live defect. A Jetpack block may inject extra markup at render time. To confirm, inspect the actual logged-out page with JavaScript **disabled** (mobile viewport, keyboard and pointer), click the CTA, confirm the scroll destination and visible form. If truly missing, ask Claude/WordPress editor to add one permanent static `<span id="subscribe-blog"></span>` immediately above the existing native Jetpack subscription block; do not add a second signup form or edit WP from QA.

Context: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129. Preserve the unique Focus Fieldbook magnet, confirmation/welcome tests, PDF checksum gate, and all QD release holds. This test is not deployment approval, end-to-end signup verification, or accessibility certification.
