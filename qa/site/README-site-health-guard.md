# Independent Final Vestige site health guard

This is a **review-only**, non-production QA utility, not a WordPress plugin or deployment payload. It uses a sanitized read-only snapshot captured from the connected WordPress.com Atomic site on **October 29, 2026**.

**Purpose:** Catch changes that might silently remove the working Focus Fieldbook acquisition path, route visitors to draft content, hide the entire site from search, or leave temporary development plugins unreviewed. It never disables a plugin, updates WordPress, calls an API, or spends money.

## Run

From the repository root:

~~~bash
python -m unittest discover -s qa/site -p 'test_site_health_guard.py' -v
python qa/site/site_health_guard.py qa/site/snapshots/wordpress-2026-10-29.json
python qa/site/site_health_guard.py qa/site/snapshots/wordpress-2026-10-29.json --strict
~~~

The 16 Python unit tests passed locally against the exact committed source and test blobs. \`--strict\` returns nonzero only for P0/P1 findings; review-only warnings remain informational. Re-fetch and **sanitize** a fresh production snapshot before repeating this guard for live drift; this stored snapshot is not real-time.

## Verified October 29 baseline

| Signal | Evidence | Disposition |
|---|---|---|
| Published pages | 79 | Inventory only |
| Published posts | 61 | Inventory only |
| Nav links | 34, zero links to unpublished WordPress page/post URLs | Pass for CMS-controlled routes only |
| Critical routes | \`/\`, \`/focus/\`, \`/dispatch/\`, \`/free-resources/\` published | Pass |
| Retired guide | Unpublished water-manual page not in navigation | Pass |
| Preparedness | Draft page 1868; not yet in navigation | Correct staging state |
| Site visibility | \`is_private=false\`, \`privacy.blog_public=1\` | Pass for WP setting only |
| Plugins | 19 installed, 18 active | Inventory |
| Pending plugin updates | Site Kit by Google and WPCode Lite | Review, not automatic update |
| History Lab helpers | One-Shot Controller, Secret Bridge, Vector Activator, Vector Attach Probe active | Ownership/necessity review; **not proof of a vulnerability** |
| Site identity | WordPress site name "FINAL VESTIGE"; icon and logo IDs are 0 | Brand consistency review; theme may render logo separately |

The snapshot deliberately omits usernames, email addresses, API keys, comments and subscriber information. \`review_plugin_names\` flags only specific transient-sounding components for a human decision. There is no automatic deactivation.

## Scope and limitations

- This checks explicit \`wp:navigation-link\` blocks against WP inventory. A dynamic route may still exist without being a WordPress page; a missing WP match is **not** a confirmed 404.
- The Exchange uses dynamically served \`/portal/\` routes from FluentCommunity/Final Vestige Community Layer. The plugins are active, but **we did not successfully perform a public browser GET**. Test routes on an actual browser before claiming failure.
- WordPress visibility settings do not establish Google indexing or crawling health.
- GSC Wizard's connected trial is inactive; it refused tool use with \`payment_required\`. Do **not** purchase a subscription merely for this audit without approval.
- The actual CDN, WordPress cache and mobile theme should be checked in a real browser.
- The site's live Focus subscription and welcome email are founder-tested; do not modify those settings.
- No changes to homepage PR #49, Preparedness issue #136, community plugin, or deployment settings.

## Suggested next steps

1. Owner review of active History Lab helper plugins and update compatibility; get explicit production approval before deactivation/upgrade.
2. Validate The Exchange \`/portal/\` paths in a logged-out browser.
3. Approve a canonical Final Vestige Studios site icon/logo/identity before settings changes.
4. Repeat this check after major navigation/content updates (including eventual Preparedness launch).
5. Keep independent findings in [site operations issue #137](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/137).

**No production changes are made by running this utility.**
