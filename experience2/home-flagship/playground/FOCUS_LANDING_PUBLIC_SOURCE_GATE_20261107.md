# EX2 conversion gate — published Focus page source audit (2026-11-07)

**Draft only — release HOLD.** Base: PR #1436 head `80a40e199b691354fca44eff03c1157d5c083e81`. No production writes, signup submissions, new scripts, customer data, commercial activation, or changes to the frozen PR #49. This is a conversion-route finding on the existing /focus/ destination, not another homepage chapter.

## Read-only source evidence

Connected WordPress API: production site ID `256784396`; Page 6 `home` published, modified `2026-11-05T12:07:24`; Focus Page 1579 `focus` published, modified `2026-11-05T17:44:02`. Page 1579's returned `content` includes `wp-block-jetpack-subscriptions`, a source `<h2 id="subscribe-blog">` destination, and a visually styled `Send me the fieldbook` fallback `<a>` whose href is `https://finalvestige.com/?post_type=page&p=1579` (the same page). Its inline background color is `#113AF5`, unlike FV's antique gold. In the API-returned markup, there is **no actual `<form>` or `<input>` element**. CSS selector references to `input[type=email]` are NOT form elements. The downloadable PDF is still listed and hidden until a client-side state rule is met.

**Do not conclude the live Jetpack experience is broken.** Jetpack may dynamically replace the fallback with a working form. WordPress API content is neither a rendered browser DOM nor subscription/confirmation evidence. A previously reported source-level `?subscribe=` success-message ambiguity is a separate issue (#1415); avoid duplicating its code or counting the message as a confirmed subscriber.

## Actual substantial acceptance addition

`focus_route_contract.py` introduces a deterministic, dependency-free HTML parser that extracts real tags (not JS strings or CSS selectors), distinguishes a native submit/email form from a same-page fallback, detects non-brand inline fallback, checks the existing signup jump target and returns HOLD (exit code 2) when runtime confirmation is required. It **does not** crawl production, submit email, or record PII. `test_focus_route_contract.py` tests 6 cases including adversarial script-tag lookalikes and a genuine semantic form that explicitly remains unverified for paid conversion.

Command from this folder: `python -m unittest -v test_focus_route_contract`. With an authorized **PUBLIC content-only** export of Page 1579, optionally run `python focus_route_contract.py --page path/to/public-focus-content.html --out /tmp/focus-source-receipt.json`. Never pass subscriber lists, private database dumps, or tokens. Native runtime/Jetpack/confirmed signups remain independent gates.

A separate offline 390px Chromium `set_content` demonstration of the *observed fallback fragment* (not the live page) displayed a bright blue button with computed `rgb(17, 58, 245)` pointing to the same-page URL, and 0 forms/0 email inputs. Reference screenshot in run evidence; no public visual claim.

## Offer → funnel → blocker → change → evidence → owner

**Offer:** existing 52-page Seven Day Focus Fieldbook. **Funnel:** social visitor → archival homepage → Focus CTA → usable signup form → verified lead → paid product or approved disclosed affiliate → independently confirmed net revenue. **Blocker:** the WP API source cannot establish a usable signup form and contains a self-looping blue fallback. **Change:** fail-closed public-content form contract and runtime acceptance requirement; *no current live fix*. **Pass/fail:** six offline tests PASS; browser-rendered Jetpack input, receipt email, and sales remain UNVERIFIED. **Owner:** homepage engineering/Site QA for source and preview; Claude for Jetpack, production form, events, commercial attribution; Grok/Praxxis for social landing inventory.

## Runtime acceptance to close HOLD

Using an explicitly authorized safe browser/site and no test subscriber without approval: verify actual 360/390/768/1440 mobile/desktop DOM shows an enabled, labeled email input and submit control; keyboard/tab/no-JS behavior and fallback; accessible focus target; brand-compliant styling; non-obstructed CTA; no console errors; no misleading completion message; then separately confirm a legitimate subscriber through approved first-party records. An isolated WordPress Playground cannot certify WordPress.com Jetpack or deliverability. CI/QD, archive rights, actual image bytes and Lighthouse/CWV still gate the seven-chapter release.

No production WordPress/theme/navigation/settings modifications, merge, emails, affiliate activation or spending.
