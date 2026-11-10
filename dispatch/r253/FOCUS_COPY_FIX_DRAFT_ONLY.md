# /focus/ copy/measurement remediation proposal — REVIEW ONLY, NO CMS WRITE
**Owner:** Claude/Focus (#129) with independent Dispatch consent QA (#174). **Not approved or live.**

**Current read-only source** (page 1579): the hidden gift display says “Your fieldbook is ready to download.” It includes a direct link to the public 52-page PDF and separately advises “Please confirm your email to join The Dispatch.” Its `fvf-gift-v2` script reveals the gift on any non-empty `subscribe` query except five negative values, or on `is-subscriber` class. Five negative strings are not an authenticated positive state. This may be an intentional pre-confirmation gift experience; do not mislabel it as a security vulnerability or assume the published page fails.

**Proposed UI adjustment, subject to owner + founder review:** Keep the useful PDF accessible; use neutral confirmation wording whenever a client-only state changes:
> Your free Focus Fieldbook is available here. If you entered an email to join The Dispatch, check for a confirmation request from WordPress.com. You're subscribed to email updates only after your email is confirmed (or WordPress.com has already verified your account). You can read the fieldbook without joining.

Do **not** claim “Your subscription is confirmed” or emit `confirmed_signup` from client-side `subscribe` query/class, the download button, document opening, or repeated visits. Because the PDF is already linked publicly from the welcome, client-side hiding is not a reliable access-control barrier. A direct download is not an email opt-in.

**Single measurement contract:** `focus_cta_click` (diagnostic); `focus_signup_attempt` (diagnostic, deduplicated, no email PII); `gift_ui_shown` (diagnostic); `focus_pdf_click` (diagnostic); `confirmed_signup` (only on provider-confirmed email subscription transition + consent + dedupe, without email addresses in analytics); `merchant_outbound_click` (diagnostic); `paid_customer` (independent settled order/commission, refunds/fees reconciled). Use existing scripts/analytics, don't install parallel instrumentation.

**Acceptance:** After separately approved page copy change, conduct anonymous desktop/mobile keyboard/voice-label and URL-state browser tests; never submit a form without distinct consent. Verify a genuine subscribed status **privately in aggregate** without reading email identities. Verify welcome delivery, Jetpack subject/preheader, legal postal address and unsubscribe in a separately authorized received-email. For signed-in WordPress users, provider documentation says confirmation email can be skipped; do not require an impossible double-confirm step for those already verified.

**Dispatch expectation consistency:** Proposed text for /dispatch/ (not implemented): “New investigations and archive finds by email, with occasional evidence-based Mind & Perception notes. Some issues may include clearly disclosed, optional product recommendations; if you purchase through an eligible link we may earn a commission. Subscribe once, unsubscribe any time.” Do not change the established list or default new-post email OFF.

**Release:** HOLD_UNSENT; merchant hold issue 03/05; no publishing, sending, test messages or subscriber writes.
