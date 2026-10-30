# Final Vestige — visitor-path cleanup (read-only QA release candidate)

This folder contains a **safe, offline** navigation guard and a **proposed, page-scoped CSS** correction. These are review artifacts, **not** a WordPress deployment. Nothing in the branch calls a CMS write API, modifies the production branch, or bypasses the site's QD/Decision Queue process.

## Findings (read from WordPress Oct 29, 2026)

1. **P1: Old guide remains in public navigation.** Published WordPress navigation ID **5** still contains a "Water Resilience Field Manual" child link to \`/collection/water-resilience-field-manual/\`, while WordPress page ID **85** is in **draft** status. It is a potential dead-end and contrary to the founder's directive to retire water-guide promotion. This finding comes from WordPress source data, not a browser-level 404 test.
2. **P1: Focus email autofill contrast.** Founder screenshot shows pale autofill background with nearly-white email text on \`/focus/\`. Published page 1579's CSS forces light \`-webkit-text-fill-color\` but has no autofill-background rule. Stage the proposed \`focus_autofill.css\` after existing \`#fv-focus-css\` email input styles, only after authorized review and a fresh page read. Do not alter Jetpack's actual subscription form.
3. **Healthy path:** Home, Dispatch, Collection and Library pages all link to \`/focus/\`; WordPress newsletter sending is enabled. The founder confirmed a successful signup journey and receipt of the welcome email. Protect these working features.

## Run tests (local only)

\`\`\`bash
python -m unittest discover -s qa/site -p 'test_*.py' -v
\`\`\`

Focused tests in this change: **14/14 passed locally** (10 retired-navigation checks; 4 CSS contract checks). The source and test files committed to GitHub match locally tested Git blob IDs. These checks do **not** replace browser verification of contrast or site links.

## Navigation snapshot format

\`\`\`json
{
  "navigation_markup": "<!-- wp:navigation-link ... /-->",
  "inventory": [
    {"id": 85, "link": "https://finalvestige.com/collection/water-resilience-field-manual/", "status": "draft"},
    {"id": 1579, "link": "https://finalvestige.com/focus/", "status": "publish"}
  ]
}
\`\`\`

\`retired_navigation_guard.py\` takes this sanitized JSON and flags navigation links to draft/private/trashed content; it ignores offsite and email links. It can also write a **local proposed markup** removing exactly one link to an unpublished target:

\`\`\`bash
python qa/site/retired_navigation_guard.py snapshot.json \
  --propose-remove /collection/water-resilience-field-manual/ \
  --output navigation-proposal.html
\`\`\`

It refuses missing/ambiguous targets and refuses to overwrite an existing output. **It never writes to WordPress.**

## Controlled production checklist (separate work; not authorized by this PR)

- Re-read WordPress navigation ID 5 and compare to the original snapshot; if changed, regenerate proposed edit.
- Remove only the obsolete child \`wp:navigation-link\` block under the "The Collection" submenu. Preserve navigation to \`/focus/\`, all other links, and all subscriber settings. Verify mobile navigation and any menu caching.
- Re-read page 1579's style block and insert scoped CSS patch **only after** the existing email input rule. Check Chromium autofill, typed text, focus contrast, keyboard operation, and narrow/mobile view. **Do not force-enable** Jetpack's signed-in disabled email field.
- Confirm \`/focus/\` signup → confirmation → welcome → PDF remains operational, and check that no retired-water links remain in navigation.
- For already unpublished URLs, evaluate 301 vs 410 with real analytics/backlinks; never automatically redirect unrelated water content to the Focus page simply to preserve a conversion.
- Do not merge/deploy under the governed Site Layer release workflow until all approval gates are satisfied; keep work separated from Claude's homepage PR #49.

## Limitations

The guard checks a supplied CMS inventory and explicitly serialized \`wp:navigation-link\` nodes, not every dynamic route, template, custom HTML link, redirect rule, or actual HTTP 404. The CSS rule is a proposal; headless unit tests cannot prove the exact browser autofill rendering. Both require live browser verification after authorized application.
