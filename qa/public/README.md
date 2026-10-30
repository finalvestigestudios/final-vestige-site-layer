# First-party HTTP smoke checks (independent QA, not deployed)

This script is deliberately separate from the *offline WordPress snapshot* checkers in draft PRs #127 and #130. It makes **at most four bounded public GET requests** against Final Vestige's own domain (plus two optional legacy URL checks), using only the standard library. It does **not** sign up subscribers, follow emails, call WP REST write endpoints, interact with WordPress sessions, or publish content. Redirects to other domains are blocked.

Run on a machine with ordinary HTTPS/DNS access:

```sh
python3 qa/public/public_readiness_probe.py
python3 -m unittest discover -s qa/public -p 'test_*.py' -v
```

Optional read-only legacy URL classification: `python3 qa/public/public_readiness_probe.py --legacy`. A prior water URL resolving to HTTP 200/301/404/410 is merely an observation: **do not 301 unrelated water content to the Focus Fieldbook**. Preserve any former paid buyer entitlements while devising routing.

Exit codes: `0` means **all four public GET source checks passed**, `1` means at least one returned a definitive HTTP/content failure, and `2` means one or more could not be verified (e.g., local DNS blocked). No output is a browser, visual/accessibility, form submission, actual confirmation, welcome-email delivery, or 52-page PDF count certification. The PDF check validates `application/pdf`, `%PDF` header, EOF marker, and 599,946 downloaded bytes matching WordPress media ID 1737. Published page checks require an HTTP 200 HTML document containing expected copy.

Any source or site change could alter expected text or media size; verify the current WordPress values before updating these constants. This is **DRAFT code only**, not a deployable WordPress payload. No merge without review/QD/Decision Queue approval.
