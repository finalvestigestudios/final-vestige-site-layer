# Published-page first-party route registry guard (DRAFT QA only)

This is a **local, offline, read-only** source-level regression guard. It tests whether the static first-party `<a href>` destinations in the saved Gutenberg markup of published **pages** correspond to published WordPress pages/posts. It also identifies references to two retired water-marketing campaigns. It never contacts the public website, WordPress, Jetpack, email providers, or any subscriber. No network requests, CMS writes, deployments, or third-party services are permitted.

Run on a **locally exported, sanitized** WordPress snapshot containing only public published pages and posts:

```sh
node --test qa/page_routes/published_page_route_guard.test.cjs
node qa/page_routes/published_page_route_guard.cjs /path/to/sanitized_published_routes.json
```

Expected JSON shape:

```json
{
  "site_origin": "https://finalvestige.com",
  "pages": [{"id": 1579, "status": "publish", "link": "https://finalvestige.com/focus/", "content": "<a href=\"/dispatch/\">The Dispatch</a>"}],
  "posts": [{"id": 42, "status": "publish", "link": "https://finalvestige.com/2026/10/30/an-investigation/"}]
}
```

Supply the **complete** published pages and posts inventory, not a small partial export. Do **not** commit the live content export, private files, subscriber information, tokens, or credentials. The tool does not retrieve that export itself. Always check that the reported page/post counts agree with the authenticated WordPress inventory.

`CLEAN_SOURCE` means there were no unmatched static page links in the supplied snapshot. `REVIEW_SOURCE` means inspect a candidate; a permalink may redirect correctly or be a virtual route. `INVALID_INPUT` means the test cannot run. Plugin routes such as `/portal/`, media, feeds, and account endpoints are excluded from route-registry claims. JavaScript-created anchors, server-rendered theme templates, redirects, server-side rewrites, live HTTP, keyboard access, viewport rendering, actual signup confirmation, welcome receipt, and the Focus PDF file bytes are **not tested**. Missing routes are never described as confirmed 404s.

**2026-10-30 independent WordPress authenticated census:** 79/79 published pages fetched successfully, 61 published post canonical URLs in destination registry, 427 first-party `href`-like occurrences counted in saved markup using a broad source regex (not rendered anchors; the standalone guard intentionally counts only static `<a>` tags), zero retired-campaign references among those 79 page bodies, and zero unresolved route candidates in the tested registry. The 61 published posts separately passed retired-campaign source checks in #129. The 79-page result is an independent, positive *CMS-source* regression observation; it is **not** a claim that a public URL, mobile interaction or checkout works. No homepage/Nav/Claude content was changed to obtain this result.

This work is intentionally separate from draft #127 (site readiness, menu density) and draft #159 (dated permalink inconsistencies **inside posts**). Claude owns live WordPress editorial changes; QD/Decision Queue and explicit approval govern all live changes. Never merge/deploy this draft automatically.
