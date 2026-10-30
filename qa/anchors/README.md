# Focus in-page CTA fragment check (read-only, draft QA)

Use `python3 qa/anchors/focus_fragment_probe.py` from a machine with **real** DNS/HTTPS. It requests only `https://finalvestige.com/focus/`, with a 10-second timeout, 1 MiB response limit and strict first-party HTTPS redirects. No form submissions, authentication, external links, WordPress writes, or personal information are used.

An offline fixture may be used with `--html-file /private/path/sanitized.html`. Run tests with `python3 -m unittest discover -s qa/anchors -p 'test_*.py' -v`.

Purpose: five Focus page secondary CTAs use `href="#subscribe-blog"` while the stored Gutenberg content has no explicit matching `id` or block anchor. **This does not prove an actual frontend defect:** Jetpack, theme rendering or client-side JavaScript may supply the target. `REVIEW_RENDERED_ANCHOR` means inspect the real DOM, scroll behavior, keyboard focus, and mobile viewport using an anonymous browser before suggesting a site edit. `PASS_SOURCE` means only that the downloaded HTML contains an anchor, **not** that clicking, mobile rendering or signups work. `INCONCLUSIVE_FETCH` likewise is not a site outage.

The primary signup/confirmation/welcome journey has been founder-verified (GitHub issue #129); this test must never overwrite that status or claim it checked email delivery or PDF accessibility. No production changes are authorized by this PR. Keep separate from the HTTP/PDF smoke test in PR #133 and the editorial crosslink checks in PR #140. Do not merge without QD/Decision Queue review.
