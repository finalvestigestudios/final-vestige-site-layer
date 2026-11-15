# R373 · WordPress + merchant release proof — read only
Site 256784396, snapshot 2026-11-15T07:36:52Z. No WordPress writes, real test messages or subscriber contact.

## Authenticated newsletter state
| Property | Read-only observation |
|---|---|
| Newsletter | enabled; site_can_send=true |
| New-post automatic email | OFF |
| Content mode | FULL |
| Sender display | Final Vestige Studios |
| Reply-to | no-reply |
| Configured welcome | Complete 52-page Fieldbook PDF; actual inbox receipt UNKNOWN |
| Total / confirmed / unconfirmed | 3 / 3 / 2 |
| Stats WP.com / direct-email followers | 3 / 0 |
| Exact provider filtered Email subscription = Subscribed count | UNKNOWN |
| Last 5 post notifications | never_sent_opted_out; actual recipients unknown |
| Native Jetpack preview / received email | NOT VERIFIED |
| Valid FV business postal address | NOT VERIFIED |
| Working newsletter opt-out | NOT VERIFIED |

WordPress subscriber documentation (updated Nov 4, 2026) explicitly excludes Not confirmed from subscriber total, so 3+2 must not be assumed to equal five addressable people. Subscriber status categories: Subscribed, Not subscribed/Reader, Not confirmed, Bounced, Emails paused, Not sending. WordPress Stats follower totals use a different taxonomy. Obtain private aggregate filtered recipient counts without copying addresses into GitHub.

Read-only WordPress view of /dispatch/ includes a fallback same-page Subscribe link, while the live public rendering includes an actual email input and Subscribe button. A saved-block fallback alone does NOT prove that the public form is broken. Public /focus/ shows a Fieldbook download panel, which does NOT prove provider-confirmed opt-in. Existing R371/R372 separately covered client-side signal misuse.

## Merchant: NOT authorized on the available evidence
| Offer | Verified publicly | Necessary proof not held |
|---|---|---|
| Zen12 | Official https://zen12.com/getstarted shows 12 levels, 48 MP3s and a $87.99 public checkout path. Separate https://zen12.com/secret/ advertises a $37 coupon pathway. | FV-specific partner account acceptance; named email/newsletter channel allowed; issued earning URL; approved guide; actual referred checkout and return/refund terms |
| Total Focus | https://hypnosislive.com/mental-skills/total-focus displays 33 minutes, 47 MB and a $24.44 price in the retrieved snapshot. Sales copy claims dramatic benefits as seller assertions. | Distinct offer-specific email channel approval, earning URL, live vetted guide, actual referred checkout price, current refund/format usage permissions |
| Limitless Labs | https://inspire3.com/ll/ has email copy and artwork and explicitly calls for approval. | NOT either campaign SKU and cannot establish Zen12/Total Focus email rights |

Connected Gmail searches for relevant partner acceptance and a delivered Fieldbook welcome yielded no authenticated FV-specific email-channel approval and no confirmed post-confirmation welcome. Generic marketing emails are not an account-approval record. No one was contacted.

## Native WordPress review before founder's send permission
1. In Jetpack Newsletter Subscribers, privately obtain ONLY aggregate counts for Email subscription = Subscribed, Not confirmed, Bounced, Emails paused and Not sending. No subscriber PII in repo.
2. Founder provides the actual valid Final Vestige publisher postal address privately. Neither Automattic's nor Inspire3's footer address suffices.
3. Authorized site editor produces a **non-sending** native Preview email and records actual subject, body, near-CTA disclosure and footer. No Send test email button should be invoked before approval.
4. Real inbox delivery, complete Fieldbook welcome, download response and functional unsubscribe remain distinct proof gates and may require expressly approved tests.
5. Mind/Commerce supplies named approval, exact SKU and EMAIL-channel grant, earning URL, current checkout/refund and approved live guide for each commercial placement.
6. Founder separately approves final creative, audience, cadence and actual send. A technical site_can_send=true is NOT authorization.

Official: https://wordpress.com/support/newsletter/email-appearance/
Official: https://wordpress.com/support/subscribers/
FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
