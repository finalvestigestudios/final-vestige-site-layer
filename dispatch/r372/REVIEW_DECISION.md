# Dispatch R372 — consent repair reference and release-blocker decision

**2026-11-14 PT | REVIEW ONLY | NEVER SEND / PUBLISH / CHANGE SETTINGS FROM THIS PACKET**

## What this new sprint actually solves

R371 reproduced a live /focus/ client-state bug: ?subscribe=unconfirmed and ?subscribe=failed make a free Fieldbook panel visible. The PDF is intentionally free; the defect is a *conversion-label inference*, not a paywall/security bypass. R372 provides a runnable non-sending replacement **state interpretation reference** and accessible HTML copy review. The client can show the free PDF under every state, but **cannot emit confirmed_signup**. Claude / Focus retains ownership of any production UX and event change. No WordPress change is proposed as already authorized.

## Five material conversion obstacles, in owner order

| OFFER → funnel | BLOCKER | CHANGE / proposed experiment | Evidence / pass condition | Owner |
|---|---|---|---|---|
| Existing free Fieldbook → confirmed eligible lead | Download panel/query/CSS class cannot authenticate consent; total=3, confirmed=3, unconfirmed=2 and Stats wpcom=3/email=0 are different populations | Separate free-resource UI from confirmation copy; count confirmed_signup only from authoritative provider-confirmed, active **Email subscription: Subscribed** event deduped to unique opaque ID | R371 actual script VM reproduction; R372 native fixture tests (offline PASS). Real Jetpack provider receipts **HOLD** | Claude / Focus |
| Existing welcome → retained reader | Welcome text configured but no received post-confirmation message or guest download proof | Owner-authorized receipt verification through existing mailbox and safe guest PDF access check; don't send a test email without founder approval | Gmail found only Oct 25 confirmation notice, **not a welcome**; real inbox/PDF **HOLD** | Founder / Focus |
| Zen12 → approved independent guide → buyer | No SKU-specific named affiliate **EMAIL** permission, issued link or approved LIVE guide; standard vs coupon checkout differ | Mind/Commerce presents authority, earning URL, final referred SKU terms and purchase evidence; Dispatch holds issue 03 CTA | Official seller pages show $87.99 standard checkout vs separate $37 coupon ad as of Nov 14; neither is FV-referral evidence. **HOLD** | Mind / Commerce |
| Total Focus → approved independent guide → buyer | Seller page offers a 33-minute 47-MB MP3, but claims unproven and checkout/refund nuance unvalidated for FV | Claims matrix: content description vs efficacy; offer-specific email rights, authentic referral checkout, seller FAQ limits | Official product page shows $24.44 public standalone and FAQ 14 days, at most five refunded sessions/year. **HOLD** | Mind / Commerce |
| Dispatch → commercial inbox | Authentic Jetpack render not observed; publisher postal address and working opt-out unverified; reply_to=no-reply | Owner-only browser non-sending preview / settings, consent-filtered subscriber count, sender/footer validation; no reply CTA while no-reply | FTC CAN-SPAM guidance + WordPress native Preview distinction; **HOLD** | Dispatch / Founder |

**Original drafts:** Original six remain unchanged: editions 01/02/04/06 editorial; 03/05 commercial and additionally HOLD_MERCHANT. Existing R363–R370 alternates are NOT adopted. The original Issue 04 subject claims a specific fourteen-second span without defining its endpoints and needs a correction or historical proof before send. Issue 01 and 02 share the same Puységur CTA. Issue 06 sends existing subscribers back to the signup page. These are conversion/credibility risks, not proof of outcomes.

## Measurement contract (not deployed)

Use Grok's established utm_source, utm_medium=organic_social, utm_campaign=<topic_cluster>_pilot_2026_11, utm_content=<actual_unique_asset_id> only for actual creator assets. Claude owns first-party instrumentation; no duplicate pixels. State progression: qualified human session → *relevant guide CTA click* → unique provider-confirmed email lead when applicable → independently reported settled paid order/commission → refunds/fees → net revenue. Unconfirmed signup attempts, Fieldbook downloads, email CTA clicks and affiliate outbound clicks are separate **non-revenue** events. Seven- and thirty-day cohorts with tiny-N cautions. Net revenue per thousand qualified-human sessions is **N/A** until valid numerator and denominator exist; do not report zero as observed revenue.

## Source-of-truth links and qualification

- GitHub master six-issue draft https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175 and historical gate #201; Dispatch owner https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; Mind owner https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 ; Focus #129; revenue #820.
- WordPress subscriber categories (unconfirmed excluded from total): https://wordpress.com/support/subscribers/ ; WordPress preview vs actual test: https://wordpress.com/support/newsletter/email-appearance/ ; confirmation/welcome behavior: https://wordpress.com/support/newsletter-settings/ .
- FTC CAN-SPAM (valid postal address, opt-out, honest subject, commercial identity): https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Public official Zen12 order https://zen12.com/getstarted and distinct coupon https://zen12.com/secret/ ; Hypnosis Live Total Focus https://hypnosislive.com/mental-skills/total-focus and FAQ https://hypnosislive.com/faq ; public Inspire3 affiliate network https://affiliates.inspire3.com/ . **Public promotion pages never establish named Final Vestige email rights or settled commissions.**

**Evidence level:** Current authenticated read-only Jetpack settings/status as of 2026-11-15 06:37 UTC; original #175 SHA compared to its source fixtures and six native Python tests PASS; R372 native Node tests and static HTML semantics recorded in QA_EVIDENCE.md. Browser screenshot attempted but environment timed out, so visual viewport verification remains unperformed. No real inbox receiving, native WordPress preview, subscriber identifiers, merchant authorization, sales or paid revenue established. No CMS, live code, social queue, email/test email, list import, analytics tags, merchant contacts, merges, deployments or spending performed.
