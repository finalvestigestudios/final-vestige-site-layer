# Source-of-truth: browser success UI is NOT newsletter confirmation
**Observed on 2026-11-17 PT / 2026-11-18 UTC. Read-only, aggregate-only.**

## Exact observed live Focus logic
The stored /focus/ page (ID 1579, published, last modified 2026-11-16 14:54:58 as returned by WP) includes `<script id="fvf-gift-v2">` with:
```js
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
var q=null; try { q=new URLSearchParams(window.location.search).get('subscribe'); } catch(e) {}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){ if(c){ if(/\bis-subscriber\b/.test(c.className)){show();} } }
```
The `show()` implementation simply sets `g.hidden=false` for the downloadable Fieldbook panel. The panel explains that email confirmation is separate. A URL such as `?subscribe=pending` or an arbitrary nonblocked value may expose the panel; this is acceptable for a freely available PDF **only if not counted as consent**. The `is-subscriber` CSS class is UI state, not proof of provider eligibility. No `confirmed_signup` instrumentation appeared in the stored page.

Other observed markup: `data-fv-event="focus_signup_click"` on in-page subscribe invitations, `data-fv-event="focus_pdf_click"` on a Fieldbook download anchor. The presence of attributes does not prove analytics are firing, their collection accuracy, unique visitors, or any joined sale. The stored subscribe block appears as generated HTML with a page-url subscribe anchor; do **not** infer actual JavaScript-enabled visitor rendering from this read-only editor representation.

## Provider categories remain separate
- Jetpack newsletter diagnostic at 2026-11-18 00:31:52 UTC: total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**, paid **0**. WordPress documented unconfirmed addresses are excluded from total: do NOT add these fields.
- Prior follower overview: WordPress.com Reader followers **3**; direct-email followers **0**. These are **different** measurements, neither an authenticated count of `Email subscription=Subscribed` receiving inboxes.
- Newsletter enabled, send capability true, automatic post-send default false, full content, reply-to `no-reply`. Five latest post notices `never_sent_opted_out`; lifetime sends not inferred.
- Welcome text configured with 52-page PDF. Configuration is **not** a delivered inbox witness.
- WordPress Media **1737**, `application/pdf`, filename `Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf`, recorded filesize **599,946 bytes**. The same HTTPS link is present in /focus/ and welcome configuration. External web fetch reported cache miss/inaccessible, NOT a proven HTTP 404. Media existence is NOT successful mobile download proof.

## Event naming and attribution decision
`focus_signup_click`: CTA engagement; `focus_pdf_click`: PDF click; `focus_download_panel_shown`: an OPTIONAL future UI-display event (not presently deployed), never a lead. **Only** `confirmed_signup` is a qualified lead and it must be emitted server/provider-side on an authenticated consent transition with an opaque provider subscription key, approved consent scope, transition timestamp and evidence reference. Repeat attempts and Reader follows must not increment it. No raw email addresses, hashes of emails, IPs, names, or individual subscription IDs in published analytics or GitHub. Do not add a second browser conversion script.

## Acceptance owner and failure modes
1. **Focus / Claude:** privately read WordPress provider filter `Email subscription=Subscribed` and deduplicate deliverable eligible subscribers without exporting personal addresses. Record aggregate number, query timestamp/filters and provider evidence reference. Do not invent a count from total/confirmed/Reader followers.
2. **Focus / founder:** verify one existing, explicitly authorized personal receiving inbox's original welcome/attachment or PDF link if already delivered; no new subscription, test mail or subscriber contact without consent. Message should contain the right gift, subject, publisher identity, and actual sent timestamp.
3. **Dispatch / founder:** native non-sending Jetpack post-editor Preview on mobile/desktop; separate authorization required for a received test mail. Verify publisher valid physical postal address and real unsubscribe in actual email, not Automattic's confirmation email.
4. **Mind / Affiliate:** named Final Vestige account accepted and **EMAIL-channel** permission, exact SKU and issued earning URL, rights-cleared live guide, current checkout/refunds and independently settled affiliate orders.
5. **Claude / revenue:** dedupe only a provider-confirmed transition; connect consent to Grok `utm_content=asset_id` when lawful/observable, but do not assert a paid sale without merchant/Payhip settlement after fees and refunds.

**Result:** lead conversion cannot be truthfully calculated from the current frontend, 3/3/2 newsletter snapshot, or WP follower overview. Genuine settled revenue / 1,000 audited human sessions remains **NOT_COMPUTABLE**, not zero.
