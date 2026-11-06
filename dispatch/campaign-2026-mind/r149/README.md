# Dispatch R149 — real guest first-click proof, native Jetpack release contract (DRAFT / HOLD)

**November 5, 2026, 16:35–17:00 Pacific.** Companion Issue #174; Mind #171; Focus #129; Conversion #820. Stacked **only** on R148 draft PR #1168, head `bcd3929539eb4e44cb8c571dddd6d1cb133ae52b`. Master six-issue PR #175 (`d57ccdba3aee8f065e143e101c2945f4f3d01647`) and first review PR #201 remain intact. Frozen homepage #49 is not modified.

## Why this is different from R148

R148 established an **API rendering discrepancy**, not a confirmed guest-browser defect. This increment specifies a non-submitting **real Chromium browser measurement** across four viewports, with explicit control cases for a form that mounts successfully, a circular self-link, a hidden form, and a disabled form. The Python Playwright harness and 17 native fixture/browser tests are **committed in this PR** and also bundled in a downloadable QA package; **the package must be executed against the actual signed-out production DOM before any guest failure is declared**. The locally tested fixture output is *not* production browser evidence.

### Source-of-truth snapshot, verified authenticated read-only at 2026-11-06T00:36Z
* Jetpack newsletter enabled; site's `site_can_send=true` means the platform can send **if explicitly commanded**, not permission to send.
* `email_new_posts_by_default=false`; five most recent article records each `never_sent_opted_out`. No campaign send was performed.
* `email_content_format=full`; from name **Final Vestige Studios**; `reply_to=no-reply`; newsletter category targeting off.
* Counts `total=3`, `confirmed=3`, `unconfirmed=2`, `imported_last_24h=0`. These are **not additive**, and cannot prove three eligible mailboxes.
* Welcome template contains the same 52-page Focus Fieldbook URL. Neither delivery nor file attachment/download was independently verified.
* Stored `/dispatch/` #523 has a native `jetpack/subscriptions` block but WordPress API view surfaced a Subscribe self-link to `?post_type=page&p=523`, with no form. That discrepancy warrants guest-browser examination, not a declaration of broken signup.
* Stored `/focus/` #1579 has permissive `?subscribe=` panel logic; a displayed success state is not native opt-in confirmation. Existing **Focus correction PR #1079** owns any production fix; do not duplicate or publish an overlapping patch.
* A targeted, bounded connected Gmail search found an Oct 25 **confirmation request**, but no actual *Welcome to The Dispatch* / Fieldbook receipt matching queries after Oct 20; this is negative mailbox evidence, **not** proof no welcome was ever delivered.
* Bounded searches found no named Inspire3 affiliate email-permission evidence; absence in one mailbox does not establish acceptance/rejection. Mind Studio still owns partner verification.

## Operational acceptance test — signed-out guest and no submission
Run from an environment with Python Playwright, Chromium, and external website reachability:

```shell
python -m unittest -v test_native_release_contract.py test_guest_browser_probe.py
python -I guest_browser_probe.py --mode fixture --chromium /usr/bin/chromium --out ./offline-proof
python -I guest_browser_probe.py --mode live --chromium /usr/bin/chromium --out ./guest-proof
```

**Safety:** A fresh anonymous browser context; GET navigation only; no typing into real inputs; no clicking subscribe, no submitted forms, no test emails, no checkout, no WordPress writes, no subscriber exports. 320×740 / 390×844 / 768×900 / 1440×900; wait for JS; inspect visible `input[type=email]`, its accessible name, enabled state, submit control, Jetpack ancestor, and visible Subscribe anchors. Record redacted DOM facts/screenshots; **do not include emails, query-string tokens, cookies, headers, or form values**. Keyboard focus/Tab and touch affordance need a human review of screenshots/DOM, not a fabricated pass.

### Interpretation
* `VISIBLE_SUBSCRIPTION_FORM_NOT_SUBMITTED`: guest UI appears actionable, **NOT a lead, delivery, or confirmed signup**.
* `SELF_LINK_WITHOUT_VISIBLE_EMAIL_INPUT`: evidence for a guest first-click defect ONLY when measured on live signed-out DOM, with URL & screenshot; API-only case remains `REPRESENTATION_DISCREPANCY`.
* `INDETERMINATE`: plugin hydration, browser policy, timeout, or nonstandard div controls; keep issue open. Never treat a missing form in a raw Gutenberg block as proof the actual guest form is broken.
* Browser runtime in the isolated authoring container blocks external navigation and also blocks `file:`/ `data:` pages; fixtures were rendered via `page.set_content`. Therefore **NO LIVE CHROMIUM PASS/FAIL CLAIM** is possible from this environment.

## The actual native Jetpack delivery obstacle

WordPress describes Jetpack Newsletter as **new-post-triggered** email, with a native *Preview email* editor action and a distinct *Send test email* button. We lack authority to send either a campaign or a test. For this campaign, the native preview requires creating/opening a **post draft**, turning on the *Send this post to subscribers* editor toggle to expose **Preview email**, and previewing without invoking Publish/Schedule/Send test. A preview is not a delivered RFC822 mail and does not verify postal/unsubscribe automatically.

**Editorial and founder gates remain independent:** four editorial drafts (#01/#02/#04/#06) and two commercial reserved (#03 Zen12 Premium, #05 Hypnosis Live **Total Focus**), ALL `HOLD_UNSENT`. #03/#05 additionally `HOLD_MERCHANT`. The founder has approved **draft preparation**, not distribution, category segmentation, recipient counts, editing production WP settings, or product-link activation. Do not flip the persistent `email_new_posts_by_default` switch. Do not impersonate a recipient or subscribe a test address.

## Compliance and conversion release gate

A delivered commercial message must have accurate sender/subject, unambiguous commercial disclosure near qualifying offer CTA, a **valid Final Vestige postal address** and functioning unsubscribe/opt-out (not Automattic's address). The original canonical commercial buyer guide URLs remain placeholders; Mind Studio must first verify named account acceptance, exact earning link, email-channel permission, guide publication, and checkout/refund/product claims. Seller marketing promises are not independently proven.

Never claim that a popup success panel, email click, or invoice draft is a paid conversion. Use only independent settled Payhip/merchant records, subtract refunds and fees, and attribute only when supported. In the tiny current audience, all A/B metrics remain exploratory, not statistically significant. Net realized revenue per 1,000 qualified human sessions is **NOT COMPUTABLE** until credible qualifying-session denominator and settled net order numerator both exist.

## One-offer reader pathway — hypothesis only

Grok (social content owner) uses immutable `asset_id` and qualified `utm_content` → relevant independently researched Mind investigation → voluntary /focus/ Fieldbook opt-in → authoritative native confirmed_signup → configured welcome → optional editorial follow-up → **only if named affiliate approvals clear**, a first-party Zen12 evaluation guide and verified earning link. No automated nurture/behavioral segmentation capability is assumed; post-based weekly schedule remains a **proposal**. Keep #05 Total Focus as second reserved pilot slot, not a simultaneous generic sales push. No forced opt-in: articles and guides remain readable without subscribing.

### Offer → funnel → blocker → next change → pass/fail evidence → owner

| Offer/funnel | Blocker | Safe next action | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Dispatch/Focus → guest signup | REST self-link discrepancy | Signed-out no-submit Chromium DOM & screenshots | **UNKNOWN** pending production run | Claude + Site QA |
| Focus → native confirmed subscriber | Display-only `?subscribe=` state; nonadditive totals | Reconcile provider confirmation and PR #1079 | **UNKNOWN**; zero verified records in this sprint | Dispatch + Claude |
| Fieldbook welcome → open PDF | Template configured, actual receipt absent | Authorized existing-received-message and PDF read-only check | **UNKNOWN**; template alone insufficient | Dispatch |
| Campaign → reader | Real full-text WordPress email not previewed | Native no-send Preview email and footer inspection | **UNKNOWN** | Dispatch + Claude |
| Zen12 / Total Focus → buyer guide → merchant | Named affiliate email rights and live guide not confirmed | Exact-merchant/partner acceptance handoff, no earning URL activated | **HOLD_MERCHANT** | Mind & Affiliate |
| Purchase → net revenue | Settled orders/fees/refunds not independently linked to qualified traffic | Verify first-party/partner transaction records | **NOT COMPUTABLE** | Commerce + Praxxis |

**Sources:** official WordPress Jetpack Newsletter https://jetpack.com/support/newsletter/ ; WordPress native Preview email https://wordpress.com/support/newsletter/email-appearance/ ; FTC CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; official Total Focus page https://hypnosislive.com/mental-skills/total-focus ; FV Editorial Standards https://finalvestige.com/editorial-standards/ . Official seller page currently shows a 33-minute/47-MB recording; promotional prices vary by fetch and are not checkout verification. Seller outcomes remain unsubstantiated.

**No sends, no subscriber contact, no actual guest form submission, no WordPress writes, no affiliate activation, no analytics snippet, no new vendor costs.**
