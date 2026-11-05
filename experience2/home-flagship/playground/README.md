# WordPress Playground — isolated, full-source Experience 2.0 seven-chapter review

**Status: PROPOSED REVIEW / NOT LIVE / NOT WORDPRESS.COM PRODUCTION.**
**Source commit:** `bdf73822422d2682be138cbad3fdfafee59cb8b8` (draft PR #1129).
**Assembler source:** `Automattic/themes`, `assembler` at pinned commit `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f`.
**Blueprint:** `playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json`.
**Native GitHub source:** `experience2/home-flagship/index.html` + six CSS + four JS files, all injected verbatim except the HTML `<main>` wrapper is swapped to `<div class="fv-hf__wp-content">` to prevent nested main landmarks in WordPress.

## What was created
A portable WordPress Playground blueprint containing **exact current source** for the seven-chapter candidate, including all original scripts and CSS. The blueprint installs the independently verifiable free Automattic Assembler theme from its pinned public GitHub commit, writes a local-only **mu-plugin** with the inlined source, and creates one disposable review page at `/fv-ex2-review/` as the local WordPress homepage. It makes no external WordPress.com API calls, writes no production content, and does not include user/subscriber databases, keys, or the original NYPL capture.

**Private repository constraint:** GitHub is PRIVATE. Do not pass a raw GitHub URL to the public Playground site; it cannot fetch protected branch content. Download the JSON while authenticated and load it as a **local Blueprint file** in the browser using WordPress Playground > New > Blueprint > import local file. The only required network access is to the public pinned Assembler theme source and the *existing public* Apollo/Franklin image origins. No paid account or subscription is required.

## Review sequence
1. Inspect the JSON source and check the pinned commit; open `https://playground.wordpress.net/` and import the local JSON using New → Blueprint.
2. Wait for Playground to load and visit `/` or `/fv-ex2-review/`. Verify both the Assembler site shell and all seven chapters render.
3. Capture screenshots at 320, 360, 390, 768, 1440, 1920 px. Include the first viewport and a full-page image for every width. Test actual browser 200% zoom at 320/390/1440, not only simulated CSS scale.
4. Run Chromium Playwright and complete-page axe; fail closed if axe is unavailable. Verify Tab order, visible focus, 44px Focus hit target, opening article, chapter anchors, 4 working enhanced interactions, 3 negative CSP controls, and the authentic Apollo/Franklin image HTTP responses with decoded bytes/hash.
5. Reload with JavaScript disabled and reduced-motion enabled; confirm no missing historical content or duplicate archival images, and no horizontal overflow. Record true browser observations, not hypothetical scores.
6. For commercial QA, verify the published `/focus/` path separately in a **network-capable anonymous browser**, without submitting subscriptions. The Playground has no real Jetpack. A click on a live origin link deliberately leaves the isolated instance—never mistake this for local conversion proof.
7. Request independent review and exact HEAD CI/QD before any release. Do not deploy this blueprint or copied mu-plugin to production.

## Limitations and non-claims
- This is WordPress in a disposable browser sandbox, **not** WordPress.com's Atomic hosting, cookie/redirect/CDN configuration, Jetpack, or real field CWV. The site has only this candidate page; it does **not** import published Page 6 or its 72 Hidden in the Margins records. Those must remain in the eventual production integration and must be independently checked at release.
- Assembler is pinned to a public Automattic source commit; its exact parity with the live site's Assembler version/global style overrides is unverified.
- The current candidate retains its original internal nav/footer; the Playground Assembler template may add separate site chrome. Record resulting duplication, do not silently conceal it. The transformed inner `<main>` prevents a nested main landmark without changing canonical design source.
- Public Apollo and Franklin imagery is *referenced*, never embedded. NYPL capture remains unlicensed and unbundled. Apollo imagery concerns crew/training, not evidence of hatch mechanics. Franklin typesetting is editorial, not facsimile.
- No WCAG, Lighthouse, image-transfer, genuine signup, visitor conversion, or monetary success is claimed from generating this blueprint alone.

## Original GitHub content receipts
- `index.html` — Git blob `8f4d64186c986a00ac48e23db7df2c05a610ceaa`, 38647 source characters
- `flagship.css` — Git blob `d856ae01a4156fb6bc60a8d7dbfa726f67f5124d`, 32312 source characters
- `chronicle.css` — Git blob `00bf26788c1eb735cf78b69c5071f75cb487f6bc`, 8030 source characters
- `chronicle-lens.css` — Git blob `97fb86e6469c98461f422d4a0a9629e757522146`, 4051 source characters
- `inquiry.css` — Git blob `28c747679969374bf1bcda386899cde03197db60`, 7553 source characters
- `observer-lab.css` — Git blob `2c214f22f7b6b0c0f34bc6154dd635c5499b90cc`, 10394 source characters
- `reading-trail.css` — Git blob `b86f944f25987c5324fdcf01d86b702d54e0de41`, 1713 source characters
- `flagship.js` — Git blob `e9a5afa346f28120aae62dfc1813666318d648d0`, 4826 source characters
- `observer-lab.js` — Git blob `f70567529114aa07ae5fb01a8a5b146dadb78804`, 2448 source characters
- `chronicle-lens.js` — Git blob `f22b5e3a4f0dfabfc29e0a9829d56dab4e697df2`, 2519 source characters
- `reading-trail.js` — Git blob `f5456b573418381734ad3c58ef4d8b63aeeae38a`, 5343 source characters

## Built vs tested
**BUILT:** local-only Assembler WordPress Playground importer, exact-source serialized plugin, 7-chapter content, isolated review page.
**TESTED:** 15/15 in-memory structural/source assertions on original connector-retrieved files; GitHub blob receipts.
**NOT TESTED:** actual Playground runtime, PHP parsing in WordPress, full-page Chromium/axe/Lighthouse, real source image delivery and guest Jetpack signup.
**LIVE:** no changes.
**RELEASE:** HOLD.
