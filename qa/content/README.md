# Read-only published-article crosslink QA

This is an **offline candidate-finding tool**, not a crawler or a deployable plugin. It never connects to WordPress, alters posts, or claims a missing HTTP redirect. Keep the JSON snapshot private, sanitized, and free of subscriber data.

## Run

    PYTHONPATH=qa/content python -m unittest discover -s qa/content -p 'test_*.py' -v
    python qa/content/canonical_crosslinks.py /private/path/sanitized_content_snapshot.json

Provide a JSON object with three arrays:

- **published**: each entry has a published canonical URL and kind ("post" or "page").
- **sources**: each entry has the canonical published source URL and its public HTML string.
- **retired_or_draft_urls**: optional list of known retired or unpublished original paths.

The tool only reports noncanonical internal links for unique, date-stamped published post slugs and links to explicitly supplied draft paths. It deliberately ignores external links, fragment-only links, common dynamic WordPress/portal routes, and unknown URLs rather than calling them broken.

A NONCANONICAL_POST_LINK_CANDIDATE differs from the canonical dated permalink. WordPress **may redirect it**. A DRAFT_DESTINATION_CANDIDATE similarly needs HTTP confirmation. Every finding includes http_status_verified=false. These are review leads, never proof of a visitor-visible 404.

## Evidence (October 29, 2026)

WordPress read-only source inspection found two published article links using slug-only paths:

- The Cisterns Beneath San Francisco links to /the-morning-san-francisco-lost-its-water/.
- The Morning San Francisco Lost Its Water links to /the-cisterns-beneath-san-francisco/.

Both published canonical post URLs have /2026/08/16/ in their paths. The old short paths might redirect, but no public HTTP or browser confirmation was available in the QA environment. Correct them only through Claude's editorial workflow after checking redirects and current revisions.

The script is independent of QA PRs #127 (WordPress preflight), #130 (Focus funnel), #133 (public four-route GET/PDF probe), and #134 (navigation guard). It does not affect the Focus subscription, WordPress pages, routing, deployment, or CI.
