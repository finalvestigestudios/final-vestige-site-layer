# EX2 accessibility tree and keyboard admission — 2026-11-07 (review only)

**Status: OFFLINE BROWSER SMOKE PASS; WORDPRESS / AXE / WCAG / LIGHTHOUSE / QD / RELEASE HOLD.**

**Exact source:** Parent PR #1469, commit `a14d3b529bca41a527e0ab583280467bc30ee0c9`. Source ZIP SHA-256: `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`. This branch adds the independent executable `verify_pinned_wp_ax_keyboard.py`, importing `make_fixture()` from the parent's source-attested Chromium runner. No changes to PR #49, WordPress, production theme, media, navigation, subscribers, tracking or existing seven-chapter source.

## New verifiable admission dimension

PR #1469 covered 28 responsive enhancement/zoom configurations and mouse/pointer interactions. This companion uses **Chromium CDP `Accessibility.getFullAXTree`**, not DOM-only counts, to catch empty accessible names and missing source headings on the same pinned payload. It tests three widths (390/768/1440) × JavaScript on/off × reduced motion on/off = **12 AX-tree browser configurations**.

Every configuration passes: all user-action links and buttons have accessible names, all seven chapter links are present, at least one accessible Focus action remains, one H1 and expected evidence headings survive, all **72 Margins items** and **five Focus destinations** remain in the document, IDs are unique and no uncaught JS exceptions occurred. Under reduced motion the Margins items are static and displayed.

The six successful **keyboard-only actions** (not synthetic clicks): native evidence-chapter Enter with JS; native evidence-chapter Enter without JS; Franklin case via Enter; case End moves focus and pressed state to Malbone; ArrowRight moves the documentary lens to its April 1848 addition; ArrowRight moves the Observer Lab to Frame B. Three intentionally broken states were **correctly rejected**: blank Focus action name, removed chapter anchor href, and duplicate historical heading ID.

Run from this directory, with the *private* original Blueprint ZIP already available on the review machine:

```bash
python -I verify_pinned_wp_ax_keyboard.py /private/path/fv-ex2-local-cli-preflight-guarded.zip --out /tmp/ex2-ax-review
```

The runner refuses altered source bundles, blocks all network requests and writes JSON plus two 390px keyboard-only screenshots into the designated local output directory. Chrome is the locally available `/usr/bin/chromium`; other machines must adjust the browser executable path. The local verified source blob for the Python test is `6ebedd740878d1f4cf8a5c06c6cfc37736cfc6a8` (Git blob SHA), and local test SHA-256 is `5ad7f53ae493b6ae65a4aa20fbf44f5ef4cacc5edbf1772c99d4e9e10640f0a3`.

## Boundaries and release blockers

- **Not WordPress-native:** Source is real pinned seven-chapter PHP bundle, but Chromium directly renders extracted HTML/CSS/JS. Actual Assembler, WordPress plugin filters, hosted caches and Jetpack are not exercised.
- **Missing main landmark in the isolated payload is not a production finding.** The WordPress theme may wrap the block in `<main>`; test this *in the real WordPress-rendered page* before deciding whether a change is needed. Never add a nested `<main>` blindly.
- **No axe-core available:** This smoke cannot qualify WCAG 2.2 AA; the independent axe release gate remains HOLD. Manual screen-reader verification, 200% zoom, forced colors and keyboard/touch review are still required in WordPress. Passing six keyboard actions does not imply WCAG compliance.
- **No real media requests:** All requests were blocked deliberately. Media **bytes/MIME/decode** must be verified using isolated, authorized WordPress/Assembler. Current WordPress metadata read only: Apollo #473 78,346 bytes / NASA S67-19766; Franklin #474 466,043 bytes / Victory Point note from later 1869 printed reproduction. NYPL #1258 5,553,669 bytes remains an **editorial source credit, not an embedded image**, pending final clearance. These are metadata values, not transferred-byte observations.
- **No CWV evidence:** Lighthouse, field INP/LCP/CLS, hosted Jetpack signup, confirmed leads, paid orders and net revenue were not measured.
- **Staging environment:** Connected WordPress lists only production site ID 256784396; Personal plan has no native staging clone. An isolated public-content-only Playground/Assembler instance remains the appropriate no-subscription route; cannot certify host-specific Atomic behavior.
- **GitHub workflow failures/QD:** Existing Actions are not green, and no exact-head independent QD PASS exists.

## Offer → step → blocker → experiment → evidence → owner

**Offer:** Existing free 52-page Seven Day Focus Fieldbook. **Step:** Evidence-rich homepage → named Focus CTA → functional form → confirmed lead → independently reported paid order. **Blocker:** Inaccessible or mislabeled source controls could lose high-intent visitors; WordPress / Jetpack acceptance is still absent. **Experiment/change:** Add CDP accessible-name and keyboard negative-control acceptance to the protected full-source review. **Pass/fail:** 12/12 offline AX configurations, 6/6 keyboard actions, 3/3 negative controls PASS, but commercial outcomes and production behavior **UNKNOWN**. **Owner:** Homepage interim engineering and Site QA for staging UX; Claude for Jetpack and revenue attribution; Grok/Praxxis for social acquisition and asset IDs.

**Release decision: HOLD.** No production writes, merge, deploy, installs, subscriber actions, links published, affiliate activations or spending authorized.
