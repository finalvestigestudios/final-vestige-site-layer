# EX2 — First-screen Focus form geometry, obstruction and accessible-name admission

**Read-only engineering review — 2026-11-08 PT; release HOLD.** Base: draft PR #1695 at `45c20ce4cb913753e170aa9bcac9227fa22434bb`. Frozen #49 at `10495883299d53596992c26a8987f629b2904670` unchanged. No WordPress, checkout, subscription, tracking or website writes.

## Reproduced verifier defect

`verify_guest_optin_readonly.py` used Playwright `locator.is_visible()` to report a Jetpack email field as visible. **That method does not require the field to be inside the 900px viewport, uncovered by a fixed overlay, visibly opaque, enabled, or given a persistent accessible name.** The test could mark a visually obstructed or unusable high-intent /focus/ form `OBSERVED_IN_BROWSER`.

This branch adds `verify_optin_viewport_geometry.py`: read-only DOM rectangles, computed visibility/opacity, center hit-testing with `elementFromPoint`, enabled state, and label/ARIA reference presence. It emits field geometry only, **never email values, placeholders, names or form submissions**. The exact existing guest verifier now records this evidence on all three routes and refuses to pass /focus/ **at mobile widths 320, 360 or 390** unless at least one enabled, labeled email field is fully in view and unobstructed. A visible-but-offscreen field is no longer counted as first-screen conversion readiness. This is a strict *UX review gate*, not proof of a Jetpack confirmation or universal WCAG compliance.

The geometry test independently executed real local Chromium against **13 synthetic scenarios**: five healthy widths (320/390/768/1440/1920) and eight negative controls (offscreen, fixed overlay, opacity zero, disabled, placeholder-only without real label, visibility hidden, off-right, no form). **13/13 passed locally.** This exercises the new helper; no production site screenshots or live visitor interactions were executed. The full guest harness still cannot be labeled LIVE PASS.

## Business observation, not conversion attribution

Fresh connected WordPress.com/Jetpack aggregate read for the seven days ending November 8, 2026: homepage **945** pageviews; /focus/ **77** pageviews; /dispatch/ **2** pageviews. Thirty-day aggregation: homepage **1,046** pageviews; /focus/ **82** pageviews; /dispatch/ **16** pageviews. The focus/home ratios, 77/945 ≈ 8.1% and 82/1046 ≈ 7.8%, are **not** click-through or conversion rates: they combine independent page totals, repeat views, uncertain human/bot traffic, and visitors entering either page through other routes. No attributable Grok `asset_id` funnel, confirmed paid order, refund or net revenue data was available from these counts. Current Jetpack follower snapshot reported **email=0, WordPress.com=3**; do not reconcile them into a confirmed-lead figure or claim a sale.

Authenticated WordPress editor contexts still contain a native Jetpack block on Page 6, Focus 1579 and Dispatch 523. The public crawled Focus page (November 8) visibly lists an email input and a “Send me the fieldbook” button, so the previously observed **REST fallback link is not itself evidence of broken public form rendering**. Real guest Chromium visibility, form submission, email confirmation, accessibility (axe/WCAG 2.2 AA), and Lighthouse/CWV remain unverified. Do not submit a synthetic subscriber.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

**Offer:** existing free 52-page Seven Day Focus Fieldbook; no merchant recommendation inserted.

**Funnel:** authentic history and evidence → contextual Focus CTA → usable Focus form → Jetpack confirmation → verified direct lead → independently verified paid sale/net revenue.

**Blocker:** apparent DOM visibility can hide actual first-screen obstruction; additional URL-based false-success on Focus remains under separate draft #1681.

**Change/experiment:** static source-controlled read-only guest viewport gate. Hypothesis: requiring an unobstructed labeled mobile form catches conversion friction missed by simple source/visibility checks. Test before any live UX change and compare confirmed funnel measurements once privacy/attribution engineering exists.

**PASS/FAIL:** 13/13 local synthetic Chromium geometry controls PASS. Hosted guest viewport/axe/Lighthouse/CWV/Jetpack confirmation NOT TESTED; release HOLD. No net revenue claim.

**Owner:** interim homepage QA owns geometry/test artifact; Claude owns actual Jetpack confirmation and attribution; Grok/Praxxis own social content and asset IDs; founder owns release/spend. Continue protecting all seven chapters, 72 Margins, Franklin folio, sources, Fieldbook and native Jetpack block.

## Reproduce in authorized isolated checkout

```bash
python -m py_compile tools/experience-2/verify_guest_optin_readonly.py tools/experience-2/verify_optin_viewport_geometry.py tests/experience-2/test_optin_geometry.py
python tests/experience-2/test_optin_geometry.py
# Hosted guest run requires reachable public DNS. It is READ-ONLY: all non-GET/HEAD/OPTIONS aborted.
python tools/experience-2/verify_guest_optin_readonly.py --out ex2-guest-viewports
```

Do not interpret screenshot-service links or synthetic localhost test pixels as actual first-party guest Chromium proof. Do not run a WordPress production install, editor update, publish, plugin activation or site migration; WordPress.com Personal has no native staging clone. Never sync subscriber databases through Playground.

**Gate:** require independent source SHA review, real mobile and 200%-zoom inspection, actual image bytes/rights, accessible Margins for reduced motion (#1674), fixed Focus false-success (#1681), hosted Jetpack confirmation and independently verified net conversion. No production release authorized.
