# Dispatch R20 — Zen12 offer-specific audit + commercial email mobile-render correction

**Date:** 2026-10-31. **REVIEW ONLY / UNSENT.** Parent: draft PR #299 at `d22796de8cff09847cde7087715fde8a09a873fd`; owner Issue #174, companion affiliate owner Issue #171; original campaign PR #175. Keep the four-editorial/two-commercial allocation and ALL six HOLD_UNSENT. Issue 03 and 05 separately HOLD_MERCHANT. No founder approval to send or test-send.

## Independent editorial analysis and changed deliverables

Issue 03's earlier copy devoted more attention to short meditation being convenient than to the precise SKU being evaluated. The new original draft preserves the subject **The twelve-minute meditation question** and exact planned preheader, but begins with an honest distinction: twelve minutes is a measurement of time, **not evidence of improved concentration**. A useful 1-minute preparation / 9-minute practice / 2-minute record exercise gives value to nonbuyers and records interruptions and actual duration rather than creating manufactured results. This is not a medical trial. The independent warm-up-guide CTA is still the unsendable token `[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]`, directly after a clear nearby commercial disclosure. There is no earning URL, checkout anchor, product price, timed deal promise, invented testimonial, personal use assertion, or claimed proven effect.

The changed paths are the Issue03 Markdown, its deterministic HTML/plaintext previews, shared review-only preview generator, and Issue05's regenerated HTML with a **mobile overflow fix restricted to unsendable placeholder display**. The new 20-test Python suite and this review memo complete the seven-file isolated PR. The original preheaders are planning labels; their presence in a native Jetpack delivered preheader is NOT established.

## Official product-specific merchant ledger (checked October 31, 2026)

| Verifiable observation | Exact page | Allowed language / caution |
| --- | --- | --- |
| Sessions described as twelve minutes | https://zen12.com/about | Seller-described duration, NOT a proved result. |
| Twelve levels and four listening versions per level (guided, music, white noise, nature) | https://zen12.com/about | Seller-described package layout; no claim of verified progression. |
| 48 MP3 files listed | https://zen12.com/getstarted | Seller-described fulfillment, **not personally purchased or tested**. |
| Seller says twelve minutes achieves an hour's benefits | https://zen12.com/about | Unverified for this SKU; NEVER publish as independent equivalence. |
| Seller describes automatic brainwave and mental-state shifts | https://zen12.com/about | Unsupported product-specific outcome; describe only as marketing assertion. |
| Current checkout displays a timed promotion | https://zen12.com/getstarted | UI observation is NOT evidence of scarcity or deadline legitimacy. |
| Checkout requests a mobile number | https://zen12.com/getstarted | Worthy of privacy/delivery questions; do not assume compulsory or how data are used. |
| Checkout advertises its own refund/guarantee language | https://zen12.com/getstarted | No independent verification of eligibility or actual refund performance; avoid static terms. |
| Inspire3 has public affiliate marketing information | https://inspire3.com/ | **No confirmation of Final Vestige acceptance, email rights, approved creative or earning link.** |
| Independent meditation evidence | https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety | General interventions; DO NOT transfer clinical findings to Zen12. |

**Mind Studio #171:** Zen12 and Total Focus independent draft guides exist in separate unmerged/unpublished PRs, not verifiable public landing pages. The commercial email's lead CTA cannot activate before the reviewed guide is live, eligible affiliate offer/approved URL and email-channel rights are verified, and founder explicitly authorizes the campaign. Never bypass the guide with direct checkout or substitute unpublished /mind/ URLs. Buyer options should remain genuine, including doing the free routine instead.

## Compliance and platform audit

- FTC endorsement disclosures: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — prominent near-offer material-connection disclosure. The new Issue03 body places it **immediately above** the inactive primary CTA.
- FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — valid **Final Vestige** physical postal address, accurate identity/subject and working opt-out required for qualifying messages. An Automattic address in a subscription confirmation email is not Final Vestige's address.
- WordPress: https://wordpress.com/support/newsletter/send-newsletter-emails/ and https://wordpress.com/support/newsletter/email-appearance/ — WordPress post title supplies actual email subject. Planned preheader in this repo is NOT proven controllable; excerpt-only delivery may truncate the valuable long-form draft. Native editor/received MIME must be inspected with authorization.
- **Live authenticated WordPress (2026-10-31 13:39 UTC):** newsletter enabled, site_can_send true, new-post auto-email **OFF**, excerpt mode, sender Final Vestige, no-reply, zero recent sends, existing 52-page Focus Fieldbook welcome configured but receipt not proved. Subscriber counters total2/confirmed2/unconfirmed2 are logically possible because pending confirmations excluded from total; individual consent and reachable email audience remain unknown.
- Existing published /dispatch/ (page 523), /focus/ (page 1579), Editorial Standards (page 17) were inspected read-only. The standard mandates provenance, differentiated inference and commercial independence; no settings, subscriber list or content writes occurred.
- Connected Gmail read-only search found consumer Inspire3 promotions but no account-specific affiliate approval or confirmed email-channel permission, and no delivered revised Fieldbook welcome. An October 25 WordPress **confirmation** email exists, but it is not a campaign email, welcome receipt or sender legal-address proof. Do not disclose subscriber addresses.

## Genuine mobile overflow regression detected and fixed

Actual offline Chromium BEFORE the change reproduced an email-preview-only bug: the uninterrupted unverified product guide placeholder forced commercial nested tables wider than narrow viewports. At 320px, Issue03 measured **558px** and Issue05 **636px**; at 390px both also overflowed. This problem was not caught by earlier browser checks scoped only to editorial editions.

The only renderer logic change adds `overflow-wrap:anywhere;word-break:break-all;` **to the visible strong unverified-placeholder tag**, not to a real link, a CMS element or the email's normal copy. Regenerated both commercial HTML assets. **Actual offline Chromium afterwards: all six previews at 320, 390, 768 and 1440 pixels (24/24 viewport runs) showed no horizontal overflow.** Issue03 additionally retained its single H1, blocked commercial CTA, explicit draft/footer placeholders, and no remote image, external request or script. These are offline file renderings, not evidence of successful native Jetpack, Gmail, Outlook or Apple Mail rendering.

## Executed QA / scope

Before edits, 15 exact GitHub source blob SHA checks against PR #299 (all six manuscripts, five Python test files, manifest, generator and old Issue03 HTML/plaintext) **15/15 matched**. Baseline Python suite `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v`: **54/54 passed**. On modified source, the committed 20 additional tests passed, combined **74/74**, and `node --check` plus `node dispatch/campaign-2026-mind/tools/build_previews.cjs --check` validated all **13 generated preview assets**. Actual local Chromium 24/24 viewport checks; no send behavior is tested. Source filenames, test output and screenshots are retained in the run evidence bundle. Confirm seven GitHub blob identities and exact final PR HEAD before reviewer signoff.

Hosted GitHub Actions on parent #299 was **RED**: run https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41202291410 showed `local-content-safety` failure with no recorded runner assignment or executed steps. The failure's root cause is unknown. Do not alter shared CI, enable paid minutes, or claim green from local tests. Check the new PR's run independently when available.

## Required gate: all false / not attested

1. No explicit founder signoff on **final creative, recipient audience, date, and any test-send**.
2. No confirmed permissioned, reachable subscriber cohort demonstrated; pending double-opt-in contacts must not be counted.
3. No Final Vestige valid physical commercial mailing address and no real received Jetpack sample proving functioning unsubscribe and complete footer.
4. No real receipt of configured revised welcome.
5. No accepted Inspire3 account-specific permissions for email/newsletter, approved SKU affiliate earning URL, currently valid product terms, independently verified outcome evidence, or permissioned creative.
6. No published verified Zen12 or Total Focus guide at the proposed CTA destinations.
7. Native excerpt email may not show the full value/disclosure; WordPress delivery configuration cannot be silently changed. Real editor/MIME validation needs separate founder approval.
8. GitHub Actions remains red or unverified.

**RELEASE:** ALL six HOLD_UNSENT. Issues 03 and 05 HOLD_MERCHANT. No post publish, mail/test-mail/schedule, subscriber contact, signup/list migration, CMS setting, analytics activation, merchant outbound, paid expense, merge, or homepage PR #49 edit.
