# Read-only conversion remediation — proposed release-ready copy (NOT DEPLOYED)
**Target:** WordPress published /dispatch/ page ID 523, only after explicit founder permission; owner Claude/Focus. No homepage PR #49 edits.
**Observed:** Native Jetpack Subscribe block exists; REST exposes placeholder anchor (public-browser behavior not independently observed), copy currently mentions confirmation, privacy policy, Fieldbook, and unsubscribing, but not the occasional commission-earning recommendations already disclosed on /focus/.

### Copy to place adjacent to the existing form
"By subscribing, you'll receive The Dispatch: evidence-led investigations and occasional Mind & Perception field notes. Some emails may include recommendations that earn us a commission. Unsubscribe anytime. [Privacy Policy]."
**Required link destination:** existing /privacy-policy/. Preserve ordinary visibility and keyboard/screen-reader access; no small-print hide, pop-up or new consent requirement. Explain confirmation before or immediately after form as already done. This gives comparable informed expectations between two routes into **one existing Jetpack newsletter**. It does not replace a commercial email's own near-offer commission disclosure.

### Acceptance checklist before any authorized live edit
1. Confirm draft exact words and legal review. Test spacing/contrast at 360, 390, 768, 1440px, keyboard and screen-reader reading order; inspect real public browser native Subscribe field **without submitting**.
2. In WordPress private dashboard read aggregate `Email subscription` filters (receiving, Reader-only, bounced, paused/unconfirmed); DO NOT access/export identities to GitHub. Distinguish 2 confirmed from 0 WordPress Stats email followers until authoritative mapping exists.
3. Confirm `focus_signup_click` is a **click**, never `confirmed_signup`. Proposed `confirmed_signup` only after a native authoritative transition and permitted attribution, with deduplication. Unconditional Focus PDF link doesn't demonstrate confirmation.
4. Only separately authorized existing genuine Jetpack received email can provide MIME/header/footer clues (use R108); never infer working unsubscribe from a link alone or from Automattic's mailing address.
5. No merchant promotion until named publisher-specific Inspire3 approval + email permission + exact allowed links + buyer privacy terms + vetted live guides + founder campaign sign-off.
6. Independently verify a valid rights-cleared paid offer, checkout, fulfillment, fees/refunds and confirmed order reporting before claiming revenue or activating a sale-led sequence.

**Status:** proposed-only; no publication, no tests involving a subscriber, no settings or list mutations. All six newsletters HOLD_UNSENT; issue #03/#05 HOLD_MERCHANT.
