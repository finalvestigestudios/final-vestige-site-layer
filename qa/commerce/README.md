# Independent source-only affiliate QA — DRAFT / HOLD

Run `python -m unittest discover -s qa/commerce -p 'test_*.py' -v` from the repo root. Python standard library only. No network or WordPress writes. Optional `python qa/commerce/affiliate_source_audit.py /path/to/sanitized_snapshot.json` reads a local JSON object with `pages` list of WordPress page records (`id`, `slug`, `status`, `content`, `meta`). Do not commit live user data or credentials.

This guard distinguishes **Awin creative image /cshow.php** source URLs from **affiliate outbound /cread.php** clickable anchors. On a real page, banner image downloads may be requested when the image is rendered; lazy loading changes the timing. Merely finding the source URL does **not** prove the request happened, that cookies were set, or that consent was violated. A browser network/consent trace is the required next gate. Actual Awin merchant eligibility, program terms, redirects, revenue, paid sales, refunds, and campaign attribution are not checked. Direct merchant information/free-trial links are reported as possible attribution leaks, not automatically defects.

No production activation, tracking beacon, plugin, tag, merchant click or signup is authorized. Claude retains WordPress release and analytics ownership; QD/founder release gates apply. This branch is independent of homepage PR #49 and existing Site QA PR #127.
