# EX2 Private-Repository WordPress Playground Admission — 2026-11-06

## Concrete blocker removed from handoff packaging

GitHub repository `finalvestigestudios/final-vestige-site-layer` is **PRIVATE** (verified via GitHub repository metadata). Its source-controlled Blueprint cannot be fetched anonymously by the normal `?blueprint-url=https://raw.githubusercontent.com/...` mechanism. This is an additional constraint on the previously proposed free staging path. A link to the private GitHub HTML file is also not a valid Blueprint URL.

Official WordPress Playground docs permit an **encoded Blueprint in the URL fragment**, including Base64: https://developer.wordpress.org/playground/blueprints/tutorial/how-to-load-run/ . Unlike a hosted JSON URL, this enables a local, source-locked file to launch the existing Blueprint in the reviewer's browser without making the repository public or adding subscriptions.

## Concrete deliverables

- `make_private_playground_launcher.py` packages the exact pinned Blueprint into an offline ZIP containing `blueprint.json`, a **no-JavaScript** `launch_review.html` and a source manifest. A local user can extract the ZIP, open its HTML and use **Open isolated Playground review**. Source is embedded in the fragment; no public-hosted Blueprint file is needed.
- `test_make_private_playground_launcher.py` covers exact Git blob custody, malicious extra WordPress step, unpinned theme, missing historical record, unauthorized plugin destination, deterministic output, and URL-fragment Base64 round-trip.
- Pinned candidate: parent PR #1306 exact commit `1a183537f55cedf0ff85aea4d1f9859276739b4d`. Source Blueprint Git blob `455c6cccbf8a00e6ecc4c2524775010d7ee1762c`; SHA-256 `89a78c35471360880c6e0053ad2f8618b35fcc0c1a5b3a5efa87989482c8a2e8`. Assembler theme ref `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f`.
- Unmodified in the pinned source: seven chapters, **72** Hidden in the Margins items, five contextual Focus destination links, original Apollo and Franklin archival image URLs, source credits and the no-JS review marker. NYPL rights-pending image is not introduced.

## Reproduce (read-only)

```sh
cd experience2/home-flagship/playground
python -m unittest -v test_make_private_playground_launcher.py
python make_private_playground_launcher.py \
  --blueprint FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json \
  --output FV_EX2_private_review_local.zip
```

Extract ZIP locally and open `launch_review.html` on an Internet-connected browser. Do not publish the ZIP or link it from production. WordPress Playground needs access to download the pinned public Assembler theme from GitHub; the two archival image URLs remain external first-party resources and need actual response-body validation. When the Playground session starts, execute PR #1306's `verify_integrated_playground.py` against an authorized isolated HTTP(S) review address where possible; its localhost/host gate must remain enforced. A browser-only ephemeral Playground address is **not equivalent** to a localhost host and may require a separate documented host authorization. Never pass a production URL to the runner.

## Verified offline evidence (not WordPress acceptance)

Local generator fixture: 6/6 regression and adversarial scenarios PASS. Independent, extended packaging suite: 15/15 PASS. Chromium rendered the **no-JS offline launch page** at 320/390/768/1440px with no horizontal overflow and a >44px launch action (4/4 PASS). A 194,480-character fragment survived a Chromium `about:blank` navigation byte-for-byte. None of these checks boot WordPress; actual Playground import and full-page acceptance remain **NOT RUN** in this network-isolated environment. The local `file://` scheme was blocked by the execution environment, so Chromium launcher layout was evaluated using `set_content`, not a claim that the local file was navigable there.

## Release safety and independent requirements

- Never sync WordPress Playground data to live WordPress; do not install a preview plugin in production or change live page ID 6.
- WordPress.com Personal does not offer an independent native staging clone. `vestigefinal-tezws.wpcomstaging.com` is NOT an isolated clone.
- The URL fragment includes the unpublished Blueprint code. Fragments are not sent in the normal HTTP request, but browser history and the Playground application's own scripts can read them. This method is only appropriate for **no-secrets, no-customer-data** previews. Source-controlled candidate is public-content-only; the repo itself stays private.
- Actual WordPress/Assembler DOM and CSS, seven widths, 200% zoom, true no-JS, keyboard/touch, reduced-motion, four interactions/negative CSP controls, WCAG 2.2 AA with official axe, real image response bytes and SHA-256, Safari and lab Lighthouse remain release holds.
- The current candidate does **not** demonstrate signed-in Jetpack signup, confirmed leads, paid affiliate orders or realized net revenue. Do not infer conversions from Focus CTA visibility or URL state.
- No new affiliate links or claims. Apollo source identification and use are subject to independent archival image/rights review; no product endorsement. Franklin source capture remains subject to exact-source visual verification. NYPL capture excluded.
- PR #49 frozen; PR #158 Apollo R&D separate; #171 Mind/affiliate lane separate; #820 owned by Claude for analytics. No CMS writes, code merge, release or commercial activation.

## Founder-facing result

**BUILT:** source-locked local launch bundle generator and offline handoff. **TESTED:** packaging integrity + local Chromium launch-page behavior only. **LIVE:** no change. **VERIFIED REVENUE:** none. **NEXT GATE:** founder/QA launches the supplied isolated WordPress Playground file in an Internet-connected browser and records the actual rendering, failures and performance. Then an independent release decision—not an assumed pass.

### OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

Existing free **52-page Seven Day Focus Fieldbook** → source-rich homepage CTA → confirmed signup → verified paid order. Blocker: incomplete native WordPress/Assembler candidate review; additionally, private GitHub prevented anonymous Blueprint URL fetch. Change: no-cost local HTML/Base64-fragment launcher. Evidence: exact-blob source gate, 6 passing committed regression cases, 15 extended local cases, 4 mobile/desktop launcher layout scenarios and a 194,480-character fragment capacity check. Owner: interim homepage engineering and independent Site QA; Claude owns attribution/checkout; Grok/Praxxis own social acquisition. No confirmed revenue outcome.

**RELEASE HOLD — never imply native staging has already passed.**
