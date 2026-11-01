# HTTP-to-Chromium visual replay (DRAFT / HOLD)

**Parent:** PR #476, exact SHA de367f26a3be5e996773e7ddcbc831dd402470b4. An optional isolated staging visual lane, not a replacement for native WordPress admission or a new homepage chapter.

## Reproduced obstacle

On November 1, 2026 an actual Python HTTP loopback server responded normally, while Chromium page.goto to the same 127.0.0.1 URL failed with net::ERR_BLOCKED_BY_ADMINISTRATOR. Playwright request interception was never invoked before the block. The normal native WordPress browser gate therefore cannot run in this executor even if a local WordPress process is available.

## Added source-controlled workaround

The read-only replay_wordpress_stage_browser.py uses Python HTTP to capture the **server-rendered** homepage and its same-origin CSS/JS/images from an already-running local HTTP instance. It refuses redirects, external origins, unaudited images and unknown srcset. It verifies seven chapters, three investigations, 72 Margins records, two Focus links, and an explicitly nonfunctional local Jetpack boundary. Three archival image responses must match an independently approved local-URL/byte-count/SHA-256 manifest; no image-rights clearance is inferred. Chromium then renders the captured markup using set_content without making network requests; it captures responsive screenshots at 320, 390, 768, 1440, 1920, checks seven widths, a labelled 720-pixel zoom proxy and a no-JS fallback.

From this exact branch checkout (requires free Python packages playwright and beautifulsoup4 and /usr/bin/chromium):
- python -m unittest experience2/home-flagship/qa/playground/test_replay_wordpress_stage_browser.py -v
- When an isolated WordPress/Assembler server actually exists, run the replay script with --url http://127.0.0.1:19400/ --media-manifest /private/reviewed-local-image-urls.json --output /private/replay-evidence.
- Manifest format: {"images":{"http://127.0.0.1:19400/path/to/apollo.webp":{"sha256":"<64 lowercase hex>","bytes":78346}, "...franklin.jpg":{"sha256":"...","bytes":466043}, "...nypl.jpg":{"sha256":"...","bytes":5553669}}}. Verify exact localhost URLs and full original bytes independently. Never publish the images or private manifest.

## Actual local evidence

New adversarial tests: **7/7 passed**. Includes actual ThreadingHTTPServer -> Python capture -> genuine Chromium execution across seven widths and JS-off testing. Same-length altered media, external CSS, remote URLs, redirects, missing Margins and untrusted srcset fail closed. Prior 65 Python regression tests passed against source-equivalent PR #476 package. No actual WordPress/Assembler server, original media or native staging execution was available in this executor.

## Hard limits

Because set_content reserializes and inlines markup, this **does not certify native top-level browser navigation, CSP response headers, cookies, CORS, HTTP caching/timing, real 200% zoom, hosted Jetpack delivery, axe/WCAG 2.2 AA, Lighthouse/CWV or the WordPress.com host**. Use it only for an additional source-grounded **visual review**, never to override the existing full native browser gate. A server that merely imitates WordPress is not proof of WordPress execution. Official Assembler theme, original image bytes/rights, actual WordPress runtime, independent QD/CI and founder release approval remain outstanding.

No live CMS writes, no plugins/themes installed, no merge/deploy, no affiliate or chapter changes; PR #49 remains frozen. **Release: HOLD.**
