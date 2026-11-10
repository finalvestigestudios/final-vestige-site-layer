# Consent-source and subscriber-expectation parity — proposed copy only

Status: **COPY PROPOSAL / NOT ADOPTED / NO CMS WRITE**. Authenticated WordPress source read 2026-11-10 UTC. See accompanying JSON for exact snippets and modification timestamps.

## What is materially different today

- **Entry point A, /dispatch/ (page 523).** “New investigations and archive finds by email, when we publish them.” The signup section promises a 52-page Fieldbook, says WordPress *may* ask for address confirmation, and offers unsubscribe. It does **not** mention commercial recommendations or affiliate commission. Its WordPress API representation includes a self-linking Subscribe control; that alone cannot resolve whether the public browser actually shows a functional email field.
- **Entry point B, /focus/ (page 1579).** Fieldbook signup explicitly says joining The Dispatch may involve emails recommending commission-earning products and provides unsubscribe language. The public extraction shows an email input; no completed signup or double opt-in was tested. Earlier source QA found that a download-ready state can appear without server-confirmed opt-in, so do not use it as a conversion event.
- **Current configured welcome.** Mentions original investigations/archive finds and the 52-page PDF link. The proposed six-issue pilot contains Mind & Perception material and two reserved offer evaluation issues; that detail does not appear in the configured welcome. **Configured is not delivered.**
- **Existing recipients:** No subscriber-level subscription origin, original wording accepted, confirmed delivery status, or actual `Email subscription: Subscribed` aggregate has been verified. Do **not** assume that three confirmed accounts equal three email recipients. Do **not** presume anyone subscribed via /focus/ rather than /dispatch/, older forms, or WordPress Reader.

The gap is reader-expectation and attribution quality. It is **not by itself** a legal finding of invalid consent. U.S. CAN-SPAM uses message primary purpose and prescribes truthful headers/subjects, qualifying ad identification, a publisher postal address and working opt-out. It does not make a generalized opt-in checkbox the sole test of compliance. This studio adopts a stricter internal consent and transparency gate as a trust choice. Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Proposed /dispatch/ signup note (NOT LIVE)

> Get the free 52-page Seven Day Focus Fieldbook and subscribe to The Dispatch. We send historical investigations, evidence-led Mind & Perception stories, and useful archive finds, not daily promotions. A small number of editions may discuss tools we have evaluated, with clear disclosures if a qualifying link could earn Final Vestige a commission. You can read our research without buying anything. Please confirm your email if WordPress asks; unsubscribe whenever you wish.

Why: matches /focus/ commercial transparency without claiming all issues advertise a product, a confirmed opt-in that we have not witnessed, or any merchant endorsement. This is proposed wording, not consent obtained from current users.

## Proposed /focus/ parity note (NOT LIVE)

> The free Fieldbook is yours to use without a purchase. Subscribing also joins The Dispatch for new research, historical investigations and occasional Mind & Perception reports. At most two of the six proposed pilot editions may feature clearly disclosed product evaluations, but only if the seller has authorized our specific promotion; otherwise those issues remain editorial. We may earn a commission through qualifying links in an approved guide. Confirm your address if prompted. Unsubscribe at any time.

Why: aligns the two entry points while keeping a **promise** separate from a vendor claim. Do not announce “two issues” in a live recurring-signup contract unless founder approves a durable policy; use the first note's evergreen phrasing if not.

## Optional welcome clarification (NOT LIVE; no update authorized)

> Welcome to The Dispatch, where we follow the evidence across history, perception and the archives. Your free 52-page Seven Day Focus Fieldbook is here: [keep the same existing verified PDF URL]. We publish when we have something worthwhile. Occasionally we may discuss an independently researched tool; any qualifying affiliate relationship will be identified beside the recommendation. You do not need to buy anything to use the Fieldbook or read our investigations. Unsubscribe whenever you wish.

This is editorial direction only. Do not paste this placeholder or change the existing welcome without the founder's explicit approval; the original full PDF URL is already configured and must not be replaced by an invented link.

## Required recipient-provenance check, read-only only

1. Identify the **aggregate** provider-filtered “Email subscription: Subscribed” count, not the WordPress.com follower count or unconfirmed requests, and confirm if available the original opt-in source and basis **without exporting addresses**. If origin is unknown, mark UNKNOWN; don't backfill from pageviews or subscribe attempts.
2. If the provider exposes opt-in timestamps, evidence of verified confirmation transitions and consent language, capture **aggregate non-personal counts** by source cohort. Do not rely on ZIP files, tracking pixels, cookies or visitor emails.
3. Keep the actual welcome email, new newsletter issues and confirmation emails **distinct**. A 2026-10-25 confirmation notice is not proof that a Fieldbook welcome arrived.
4. Verify real unsubscribe mechanism and Final Vestige business postal address in a **received** commercial message only if the founder separately authorizes a safe test. Automattic's own address on a provider confirmation does not qualify as Final Vestige's business postal address.
5. Even after copy parity, merchant acceptance, EMAIL promotion rights, approved earning link, actual guide, cart/refund and evidence of benefit claims remain independent HOLD gates. Do not import, resubscribe or “clean” the list to resolve it.

**Owner:** Dispatch proposes copy and documents audience gates. Focus #129 / Claude verify implementation only after separate production approval. Mind #171 authenticates seller rights. Founder retains all communications and release approvals.
