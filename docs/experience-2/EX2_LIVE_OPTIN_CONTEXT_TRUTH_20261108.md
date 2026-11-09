# EX2 live opt-in context: WordPress REST != anonymous browser (2026-11-08)

**Draft review only.** Base: PR #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`. Freeze PR #49 `10495883299d53596992c26a8987f629b2904670` remains untouched. No production CMS write, merge, post, subscription, affiliate link, analytics, or expenditure.

## Actual independent authenticated observations

Read-only WordPress.com site 256784396, using editor **and** rendered-view contexts on each of three published pages:

| Page | Native Jetpack block in EDIT source | VIEW REST content | What it proves |
|---|---|---|---|
| Homepage Page 6 | one | Jetpack fallback **link** to `?post_type=page&p=6`, no HTML form | Editor continuity; **not guest form runtime** |
| Focus Page 1579 | one | Jetpack fallback **link** to `?post_type=page&p=1579`, no HTML form | Existing signup must be tested in browser |
| Dispatch Page 523 | one | Jetpack fallback **link** to `?post_type=page&p=523`, no HTML form | Same context limitation across routes |

REST block render is a separate code path. It does **not** demonstrate an outage: the public HTML can render the Jetpack form differently. Never count a REST Jetpack block or fallback as a successful confirmed lead. The anonymous browser input, keyboard behavior, mobile render, email confirmation, welcome delivery, and attributed purchases are **not yet verified**.

Additional editor-source reconciliation: Page 6 retains seven chapters, 72 historical Margins, links to /focus/, and an existing single Jetpack subscription block. Focus Page 1579 retains the 52-page PDF link and reader disclosures. Dispatch links back to Focus. **Focus still contains a URL-query-only gift reveal**, the exact defect being addressed separately in review PR #1681 (do not duplicate or deploy it here).

## What is committed
- `tools/experience-2/audit_live_optin_context.cjs`: pure read-only source contract. Takes six current authenticated JSON snapshots (page ids 6/1579/523 in `edit` and `view` contexts); always reports **HOLD** absent independent hosted browser evidence. Never exports or checks subscriber addresses.
- `tests/experience-2/test_live_optin_context.cjs`: fifteen local scenarios, including thirteen negative or abuse controls; 15/15 passed using the exact committed blob and an independent JS assertion shim.
- `tools/experience-2/verify_guest_optin_readonly.py`: production-host anonymous Chromium inspection tool, **no form submit**, no email entry, no cookies imported. Checks actual field visibility, chapter/Margins preservation, overflow and screenshot evidence at 320/360/390/768/1440/1920 widths and 390px no-JS. Network operations are fenced to GET/HEAD/OPTIONS. Runs only on `finalvestige.com` or explicitly flagged localhost fixture. No axe or hosted CWV is claimed. **Hosted runner not executed in this sprint** because this container's public DNS/network requests fail.
- This report is a non-sensitive inventory, not an exported copy of WP editor content, subscribers, secrets or customer data.

## Run on a networked, authorized QA host
1. Collect the three WordPress pages' raw editor and rendered REST responses through read-only account access. Store six JSON snapshots locally; never commit them.
2. `node --test tests/experience-2/test_live_optin_context.cjs` then `node tools/experience-2/audit_live_optin_context.cjs home-edit.json home-view.json focus-edit.json focus-view.json dispatch-edit.json dispatch-view.json` (source audit exits **2** while release is held).
3. With Python Playwright and Chromium already available: `python tools/experience-2/verify_guest_optin_readonly.py --out out/optin-guest` (output goes in ignored local folder; do not upload visitor data). Fixture testing `--offline-fixture` at `127.0.0.1:8765` is **never** hosted acceptance.
4. Inspect screenshots and screenshot failures; independently run axe WCAG 2.2 AA, real 200% zoom, image network byte inspection, Lighthouse mobile/desktop on the hosted domain, Jetpack confirmation and welcome-email testing with founder-approved test account. Do not trigger test signup without approval.

## Conversion-focused decision
**OFFER** — free 52-page Seven Day Focus Fieldbook, no new commercial claims.  
**FUNNEL STEP** — evidence-led homepage -> Focus/Dispatch CTA -> real guest Jetpack field -> confirmed lead -> verified paid conversion.  
**BLOCKER** — editor blocks/REST fallback are not actual proof of functioning anonymous signup, and URL-only gift state remains falsely triggerable.  
**CHANGE** — executable three-route context-parity acceptance and read-only hosted browser admission. No competing tracking code.  
**PASS/FAIL** — current authenticated source: 14/15 PASS, one expected live source fail (`focus:no_query_based_gift_success`); 3/3 REST fallbacks documented; 15/15 exact-GitHub-source synthetic test scenarios passed. Actual hosted form, axe, CWV, subscriber confirmations and net revenue **UNVERIFIED**.  
**OWNER** — ChatGPT interim QA; Claude for Jetpack confirmation/attribution/production, Grok & Praxxis for audience assets; founder controls release.

**Release verdict: HOLD.** No rollback or replacement of the published seven-chapter homepage. No assumption that WordPress REST output is identical to production guest HTML. No Business-plan upgrade recommended; WordPress.com Personal plan lacks a native staging clone.
