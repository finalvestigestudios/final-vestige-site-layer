# EX2 homepage — computed CSS custody admission (RELEASE HOLD)

**Scope:** Companion to draft [#1847](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1847), not a rewrite of it or of frozen #49. No WordPress production writes, no plugin activation, no merge or deployment.

## Critical false-positive the existing gates do not catch
An integrated WordPress homepage candidate may keep the **exact original 72 Margins spans**, the **exact native Jetpack block**, the two Focus links and all seven chapter IDs in accessible HTML structure, yet a new stylesheet can hide them. The exact raw SHA and HTMLParser custody gates return **PASS**, because the hidden state is applied by the CSS cascade (not inline CSS/hidden attributes). A version that hides the Jetpack block would quietly eliminate the subscriber opportunity. This is a real admission hole, **not** evidence that production currently has that CSS.

## New isolated verification
- `tests/experience-2/verify_homepage_computed_custody.py` combines the existing fail-closed source/DOM gate with **real headless Chromium computed-style probes** at 320/360/390/768/1024/1440/1920 CSS pixels, both JavaScript enabled and disabled, with reduced-motion preference.
- Fail closed on a computed-hidden Margins strip or all records, computed-hidden original Jetpack wrapper, absent rendered Jetpack control, inaccessible Focus link, hidden flagship root or horizontal overflow.
- Visible counts are **not** confirmed Jetpack signups, sales or usable source rights. A Jetpack link returning to Page 6 is reported as an *inconclusive self-link*; real hosted interaction needs separate verification.
- External network requests are blocked. This cannot certify first-party image transfer, hosted styles that are not included in the supplied candidate, consent, third-party authentication, WordPress.com Atomic behavior, accessibility/WCAG, HTTP CSP, Lighthouse or field CWV.
- This script requires a **public-only rendered candidate HTML** file. Do not feed Gutenberg editor block syntax, subscriber exports, private WordPress DB, tokens or production cookies.

## Reproduction
```bash
python -m pip install playwright
# Chromium must be installed and reachable at /usr/bin/chromium.
python -m unittest discover -s tests/experience-2 -p 'test_homepage_computed_custody.py' -v
python tests/experience-2/verify_homepage_computed_custody.py \
  --baseline tests/experience-2/page6_public_inventory_20261109.json \
  --candidate /path/to/authorized-public-only-WP-rendered-proposed-home.html \
  --out /tmp/ex2-computed-style-custody.json
```
A candidate passes this **lab preflight only** when **both** the original raw/DOM comparison and the browser CSS tests pass. Standalone EX2 `index.html` is expected to fail the Page 6 preservation comparison; **do not replace Page 6 with it**.

## Executed local evidence (not exact-GitHub-HEAD execution)
Using synthetic 72-item/Jetpack/seven-chapter markup, locally reproduced companion tests passed **57/57** (38 inherited + 19 reported by local unittest discovery; duplicated inheritance in the local suite means do not call these 57 independent scenarios). Original intact baseline: static PASS and browser PASS. Seven CSS-only mutations: static PASS, browser **HOLD**, each replayed at 5 widths × JS on/off. Includes CSS `display:none`, `visibility:hidden`, `opacity:0`, `clip-path:inset(100%)`, `pointer-events:none` and overflow. Exact new GitHub files were committed but have **not** been run in a clean exact-head checkout or independent CI/QD.

## Read-only live WordPress observation (2026-11-09 Pacific)
Connected site ID 256784396 returns only production. Read-only Page 6 `context=view`, modified 2026-11-05 12:07:24, has all **72** Margins items, two Focus links and a native Jetpack wrapper. In that API-rendered representation, its subscriber action is a link to `?post_type=page&p=6`, not an inline email field. **Do not infer from that alone that the hosted subscription overlay is broken or that a subscriber was confirmed**. Browser-without-JS and genuine Jetpack confirmation/email flow remain release gates.

## Owner acceptance / limits
**Offer:** Existing free 52-page Focus Fieldbook. **Funnel:** historical entry → evidence → Focus / Dispatch → verified confirmed lead → independently verified paid order. **Blocker:** CSS can conceal original trust/lead pathway while static release gate says PASS. **Change:** executable computed-style gate. **Pass evidence:** synthetic Chrome negative controls; **conversion outcome:** unknown. Claude owns analytics/backend; Grok/Praxxis own campaign distribution; founder owns release and spending approvals.

Next: finish an **isolated** WordPress Playground/Assembler candidate preserving every Page 6 block; feed its genuinely rendered HTML into both gates, then execute axe WCAG 2.2 AA, 200% zoom, keyboard/touch/no-JS, first-party image byte checks, representative visual screenshots, lab Lighthouse/CWV, exact-head CI/QD, Jetpack provider-confirmed signup/email delivery and founder visual acceptance. WordPress.com Personal does **not** include a native clone; `*.wpcomstaging.com` default domain is not an independent environment. No WordPress install/activate without explicit permission, and no release until all independent gates are met.
