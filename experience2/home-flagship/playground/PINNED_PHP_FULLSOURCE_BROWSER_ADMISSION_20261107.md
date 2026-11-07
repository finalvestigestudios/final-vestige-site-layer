# EX2 pinned private WordPress-preview payload — full-source offline Chromium QA (November 7, 2026)

**DRAFT — RELEASE HOLD.** Parent #1461 at e24fdbd7bb28f8ef3aaf266debe06c65af034587. Frozen #49 at 10495883299d53596992c26a8987f629b2904670 was untouched. Source of truth #150 and conversion coordination #820.

## Real advance over prior synthetic fixtures
The engineer extracted the **actual HTML, CSS and JS embedded in the pinned private WordPress Playground MU-plugin**, verified the ZIP's SHA-256 and the plugin's recorded PHP custody hash, and rendered the complete seven-chapter visitor experience in disconnected Chromium. This is **actual packaged source**, NOT an operating WordPress/Assembler site, live Page 6 or a hosted staging environment.

Pinned review ZIP SHA-256: 9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d (from #1393).
Extracted HTML 50,742 bytes, SHA-256 baf26bcaddbf1b86b90f0065e1d68fbd856be03027ecd9d14ebc0ada60a21b1d.
Extracted CSS 71,874 bytes, SHA-256 2a085ef8a1878818ff16f515679396cbdf7e6b307955011f7fc7353014bb50b2.
Extracted JS 15,270 bytes, SHA-256 a95c37eb75ac2c7a22cf00f13d3a10bd958bc63d22fa3c4584557714565e7aef.
The first five CSS module blob SHA values match GitHub at PR #1461; bundled reading-trail CSS and JS contain concatenation/separators, so the entire package (rather than each standalone file) is the attested source.

## Executed evidence — offline only
- **28/28 Chromium configurations PASS**: widths 320, 360, 390, 768, 1024, 1440, 1920 × JS on/off × CSS zoom 1x/2x. No observed document-root horizontal overflow or uncaught JS exception. The 2x CSS zoom is a reflow stress test, not proof of native browser zoom or WCAG conformance.
- **7/7 chapter links target existing elements** in every configuration. Exactly **72 Margins** records and **five Focus Fieldbook links** preserved in every case.
- **At least one first-screen unobstructed Focus link in all 28 modes** (two in each 1x mode, one in each 2x mode).
- **No-JS meaning preserved**: all three historical exhibit cases visible without enhancement, while JS selects one case.
- **4/4 real browser interaction tests PASS**: Franklin case button, 1848 chronicle lens, Observer Frame B, and native chapter-anchor navigation.
- **3/3 adversarial controls correctly rejected**: lost Margin #72; replaced Focus destination; broken chapter target.
- First-screen and fullpage screenshots generated at 320/390/768/1440/1920, 200% CSS zoom first-screen at 390/1440. All external requests were blocked, thus **archival image transfer bytes unverified**. These are not production screenshots or an exact WordPress acceptance result.

### Reproduce
Use the source-controlled verify_pinned_wp_payload_browser.py in this branch with Python Playwright and /usr/bin/chromium. Supply the exact pinned local review bundle from the #1393 recorded artifact:

python experience2/home-flagship/playground/verify_pinned_wp_payload_browser.py --bundle /path/to/fv-ex2-local-cli-preflight-guarded.zip --out /tmp/fv-ex2-qa

The script refuses a differing ZIP/PHP and writes JSON, screenshots, and a nonzero exit on failed checks. No network, test subscribers, production CMS changes or activation. CI and QD have not accepted this PR. A separately attached evidence archive contains the locally executed script, results and screenshots; exact committed runner still requires independent checkout rerun.

## Evidence / source / rights review
- Apollo 1: WP media #473; source metadata 78,346 bytes. NASA S67-19766 depicts the **crew**, not the hatch or ignition cause; editorial use without agency endorsement.
- Franklin: WP media #474; source metadata 466,043 bytes. Commons image from an **1869 printed reproduction** of the 1847/1848 Victory Point record, not an original 1848 photograph; hero is labelled **editorial typesetting, not a facsimile**. Museum object record linked.
- NYPL map: WP media #1258; metadata 5,553,669 bytes; the unpublished candidate does **not reproduce** the rights-pending scan and instead includes an original chronology illustration and catalog link. Date of the historic map alone does not establish rights for the digital image.
These sizes are WP metadata, not browser transfer measurements. Independent media provenance and rights remain open.

## OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
Existing free 52-page **Seven Day Focus Fieldbook** → historical homepage → accessible Focus link → independently verified Jetpack lead → real order → realized net revenue. Blocker was absence of a full-source responsive/browser proof for the actual protected WordPress preview payload. Change is 28-state source-attested Chromium QA with real interactions and controls. Evidence as above. Interim homepage engineering and independent Site QA own this admission; Claude owns subscriber/checkout/attribution; Grok and Praxxis own primary social acquisition. No claimed new leads, sales, commissions, qualified human sessions or net revenue; net revenue per 1,000 qualified-human sessions is not computable.

## Release governance — HOLD
Connected WordPress account currently exposes only production #256784396; WP.com Personal does not offer a native staging clone. Use free **isolated** WordPress Playground or local WordPress/Assembler with PUBLIC content only, no subscriber/secret/database import. An isolated clone is not equivalent to WP.com Atomic hosting. WordPress-native acceptance, real media bytes, Jetpack/browser signup, WCAG 2.2 AA (axe unavailable here), native 200% zoom, keyboard/touch/reduced-motion, Safari, Lighthouse/CWV, hosted CI, QD and founder visual review are outstanding. Do not merge/deploy/publish/install, edit production settings, modify frozen #49, activate merchants, send emails or spend.