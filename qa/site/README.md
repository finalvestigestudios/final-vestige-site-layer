# Final Vestige: read-only WordPress production preflight

This quality gate is intentionally independent of WordPress theme code, deployment branches, CMS content, and Claude's editorial work. It **never connects to production or writes** to WordPress. Only a sanitized snapshot JSON file is required. It does not claim to replace browser/mobile testing, backups, CI, security review, or QD approval.

## Run

```bash
python -m unittest discover -s qa/site -p 'test_*.py' -v
python qa/site/wordpress_readiness.py /private/path/site_snapshot.json --strict
```

Snapshots are intentionally **not** committed. Build the JSON from authorized read-only WordPress responses, using only these fields:

```json
{
  "navigation": {"content": {"raw": "<!-- wp:navigation-link ... /-->"}},
  "settings": {"identity": {"site_icon": 0, "site_logo": 0}},
  "monitor": {"monitor_active": false},
  "backup": {"backups": {"last_attempt_failed": false}},
  "scan": {"threats": []},
  "homepage_html": "<a href=\"/watch/films/\">Films</a>",
  "landing_pages": {"https://finalvestige.com/watch/films/": "Films will appear here as they are released."}
}
```

Do not export passwords, e-mail addresses, user records, customer information, analytics identifiers, cookies, or API tokens. `--strict` exits 1 only for P0/P1 checks. P2/INFO represent recommendations, not proven defects in browser rendering.

## Initial verified evidence (WordPress read-only, October 29, 2026)

- WordPress site `finalvestige.com` is active; site status reported **up**. This is not an independent browser/load-test result.
- WordPress backup state is **active**, latest attempt at `2026-10-29 08:46:21` reported `finished` without failure.
- Security scan at `2026-10-29T08:46:21Z` reported zero active threats; a prior FluentCommunity vulnerability was marked fixed. Do not infer all vulnerabilities are absent.
- WordPress uptime monitor status: `monitor_active=false`.
- Identity settings: `site_icon=0`, `site_logo=0`; actual theme rendering and browser favicon still require visual inspection.
- Published navigation ID 5 has **two identical `wp:jetpack/subscriptions` blocks** in its raw markup, plus a separate `Subscribe` navigation link. Check the rendered result; remove duplicate forms only after coordinating with the active editor and getting site-level authorization.
- Published navigation currently contains **14 top-level items**, potentially crowded on mobile.
- Homepage currently links prominently to `/watch/films/`; this destination describes future films instead of actual available releases. Change the homepage CTA or enrich the destination with available material after editorial review.
- The site activity log showed active Anthropic/ClaudeAI editing on October 29. **Do not directly modify WordPress navigation, live editorial content, global styles, or theme settings while that workstream is active.**

## Coordination / release gate

This branch is **inert** and should be handled as a draft PR. It must never merge to the protected production branch or publish to WordPress automatically. Verify a clean branch diff, local unit tests and PR CI, then obtain the repo's regular QD/Decision Queue approval. Findings are a prioritized handoff, not proof of user-visible failure without rendered-site verification.
