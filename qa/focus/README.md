# Focus Fieldbook — offline, read-only funnel preflight

This independent QA module does not touch WordPress or overlap the generic visitor readiness checker in draft PR #127. It analyzes only a sanitized read-only WordPress snapshot for Focus funnel consistency: homepage and navigation CTAs, Jetpack form count, designated PDF URL in landing and welcome message, and links from live navigation to retired draft pages. No network calls, subscriber imports, deployment, live CMS writes, or personal-data handling.

## Commands

    python -m unittest discover -s qa/focus -p 'test_*.py' -v
    python qa/focus/fieldbook_funnel_preflight.py /private/path/focus_snapshot.json --strict

The JSON file is LOCAL ONLY, never committed. Supply a sanitized object containing pages.focus, pages.home, pages.dispatch (status and raw Gutenberg content); navigation.content from nav ID 5; retired_pages mapping the two retired URLs to WordPress status; newsletter.subscriptions and newsletter.welcome_message; media.source_url and media.mime_type for the designated Complete Edition PDF; and optionally delivery_evidence booleans.

Use delivery_evidence flags only for independently observed public_form_submit, confirmation_received, confirmation_clicked, welcome_received, public_pdf_download, and mobile_rendered. A CMS match must NEVER be claimed as actual email delivery, public HTTP status, keyboard usability, or visual mobile success. P1 means a source-level inconsistency; HOLD means the external verification trail is incomplete. --strict exits nonzero on P1, not on missing real-world evidence alone.

## Current production snapshot finding — 2026-10-29

Published WordPress navigation ID 5 retains a Water Resilience Field Manual link to /collection/water-resilience-field-manual/, whose WordPress page ID 85 is draft. This is a VERIFIED CMS route/status mismatch, NOT a browser-confirmed 404. Claude should remove that legacy submenu link, retaining the parent Collection destination, after checking live editing state. Do not restore the retired water product.

Another non-blocking source observation: /focus/ includes a client-side query-parameter download-success heuristic that does not prove a confirmed opt-in. It must not be used as verification of confirmation or welcome-email delivery.

Redirect handoff: for retired free content, consider 410 Gone or a genuinely related maintained destination rather than misleadingly 301-redirecting water content to an unrelated focus guide. For the former paid product, preserve customer access/support obligations before making routing decisions. No live redirect change is included.

Before release, re-read the active site versions and review draft PR #127 and issue #129. Respect Claude's live edits and the established Decision Queue / QD approval process. No production deployment is included in this PR.
