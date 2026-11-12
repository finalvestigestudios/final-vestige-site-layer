# Dispatch R299 — subscriber-journey repair (UNSENT draft review)

**Owner:** [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Companion [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Business [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Base: draft PR #2156, which itself is stacked on #2149. Master six-issue campaign: draft PR #175; legacy release QA: draft PR #201. Frozen homepage PR #49 untouched.

## Material finding — original Issue 06 leads an already-subscribed reader back to signup

The original sixth newsletter's primary CTA points to `https://finalvestige.com/focus/`. That is a legitimate **acquisition** page, but it contains the same Jetpack signup route used by new visitors. An already-subscribed reader was promised the 52-page Fieldbook in the welcome message. Sending that subscriber back through signup is avoidable friction. It is **not proof of a broken link, duplicate lead, or completed delivery failure**.

Authenticated read-only WordPress inspection (Nov 12 2026 07:35 UTC) finds /focus/ page ID 1579 PUBLISHED with a direct link to the public file:
https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf

This is a **link found in published page content**, not an independent HTTP download integrity or accessibility signoff. The WordPress welcome-message setting also contains the same PDF URL. It remains UNKNOWN whether a subscriber actually received or could open the welcome email; do not infer that from configuration. Keep /focus/ as the normal social acquisition destination. Consider direct PDF only as the Issue 06 CTA for recipients whose subscription is already verified.

An optional, original, no-product Issue 06 review candidate is provided in Markdown, accessible inline-style HTML and plaintext. It is **NOT ADOPTED**, not post-ready, and intentionally retains hard-stop placeholders for actual publisher postal and unsubscribe. No affiliate or price links, tracking or email sends.

## Second finding — subject and preheader are different delivery problems

Each original issue stores subject and preheader in Markdown + manifest; source equality passes. But WordPress's documented email subject comes from **the post title**. The connected `get_settings` surface does NOT provide a proven independently editable preheader field. Current full-text mode still requires a native WordPress pre-publish **Preview email**, not a simulated static HTML rendering. Proposed preheaders must be marked **UNVERIFIED_IN_ACTUAL_JETPACK_RENDER**; never imply a subject/preview pairing is live. A visible, honest opening line is preferable to hidden-preview-text tricks or unsupported CSS in WordPress.

Official WordPress documentation (last reviewed November 9 2026):
https://wordpress.com/support/newsletter/send-newsletter-emails/
https://wordpress.com/support/newsletter/email-appearance/

## Six-issue copy / CTA review against exact master #175

| Edition | Current primary CTA | Priority copy-to-conversion redline | Decision |
|---|---|---|---|
| 01, editorial | Puységur file | The series introduction is intriguing but makes broad memory/attention claims without a direct named experiment; include a specific sourced mechanism if revised. | HOLD; candidate R290 not adopted |
| 02, editorial | Same Puységur file | Two consecutive emails send readers to same destination; may be valid if their research value differs, but progression is weak. | REVIEW progression, don't invent clicks |
| 03, commercial | Reserved Zen12 guide token | Not live; no FV email affiliate rights, specific earning URL, or claim/checkout clearance. | HOLD_MERCHANT |
| 04, editorial | Apollo investigation | “Fourteen seconds” lacks event-interval definition; clarify fire report versus rupture, not ignition or crew outcome. | REVIEW R291 candidate; HOLD |
| 05, commercial | Reserved Hypnosis Live guide token | Not live; cannot promote unverified audio benefits, checkout price/refund or affiliate terms. | HOLD_MERCHANT |
| 06, editorial | /focus/ signup-oriented landing | Re-enters signup for people already subscribed; optional direct resource CTA less friction; public PDF URL still needs runtime verification. | REVIEW R299 candidate; HOLD |

**Source review:** NASA Apollo 204 Review Board report for Issue 04 chronology; https://www.nasa.gov/history/ . NCCIH for Issue 06's evidence-strength caution: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety . Official seller pages https://zen12.com/about , https://zen12.com/getstarted , https://hypnosislive.com/mental-skills/total-focus . Public affiliate enrollment https://affiliates.inspire3.com/ is not account acceptance or email promotion permission. The seller-described Zen12 12 levels / 48 MP3s and Total Focus 33 min / 47 MB are product descriptions, not verified effectiveness, stable prices or terms.

## Read-only, reproducible source audit

`campaign_cta_preflight.cjs` exports `auditCampaign(manifest, manuscripts, evidence)`. Feed it the six original Markdown bodies in manifest order; returns only a no-PII flags/owner ledger. The output **always** says `HOLD_UNSENT`, even if a test fixture sets approval booleans true. It rejects unauthorized inserted merchant links, warns when two adjacent sends share their CTA, flags customer-facing link friction and surfaces real provider/footer/rendering hold evidence. It cannot verify working links, actual subject/preheader delivery, buyer behavior, consent, paid orders or legal compliance.

Executed against the **actual seven GitHub blobs** at PR #175 SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647` with **26/26 isolated V8 assertions passed**; the optional HTML/plaintext parity/specimen received **15/15 offline assertions**. **NOT** native Node/CI, browser, Jetpack preview, inbox or physical PDF opening. The prior R298 native master Python 6/6 is historic evidence, not a new R299 execution.

## Source-of-truth settings and consent gate (Nov 12 2026 ~07:35 UTC)

- Jetpack enabled; `site_can_send=true`; new-post auto-send **off**; `email_content_format=full`, replies no-reply; Fieldbook welcome **configured**, not proven received.
- Provider diagnostic total/confirmed/unconfirmed: **3/3/2**. Distinct WordPress.com/email follower stats: **3/0**, not additive. Actual consenting, deliverable email audience remains **unknown**.
- Recent five post notifications have `never_sent_opted_out`; this is not proof of no historical sends.
- Provider's subscriber-level Email Subscription statuses, deduplicated `confirmed_signup`, native non-sending preview, **Final Vestige** physical address and working opt-out remain **unverified**.
- Never output private subscriber identifiers, emails, tokens, recipient-level data or merchant credentials.

## Offer → funnel step → blocker → change → evidence → owner

1. **Zen12 → vetted live guide → paid conversion:** email-promotion approval, signed account-specific terms, issued earning URL and approved source-led guide absent → Mind/Commerce privately verify first → **HOLD_MERCHANT**.
2. **Focus → consented recipient → welcome PDF:** email eligibility/dedup and actual welcome receipt unknown → Claude/Focus inspect provider status privately; use existing consent architecture, no duplicate event scripts → **UNKNOWN**.
3. **Dispatch → rendered inbox CTA:** native Jetpack preview, legal postal and unsubscribe unproven → Dispatch/Founder obtain **non-sending preview** and later an explicitly authorized received-email specimen; verify direct PDF if adopted → **HOLD**.
4. **Grok asset → qualified human session → lead:** preserve TASK-008 source `utm_source`, `utm_medium=organic_social`, `utm_campaign` and `utm_content=asset_id` metadata using existing Claude analytics; never infer a human/session from a tagged URL alone → Grok/Praxxis/Claude → **UNVERIFIED**.
5. **Confirmed settled order → realized net revenue:** merchant/owned-order receipts, refunds, fees and 7/30-day cohort denominators missing → Commerce/Claude authenticate. Report net revenue per 1,000 qualified-human sessions as **NOT COMPUTABLE**, never zero sales or zero revenue by assumption.

**FTC commercial email requirements:** https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Actual sender identification, truthful subject, commercial disclosure, Final Vestige valid physical mailing address and functional unsubscribe must be checked from rendered mail, not simulated markup.

## Release governance

The founder approved **a draft campaign**, NOT any send or alternate adoption. All six `HOLD_UNSENT`; Issues 03/05 `HOLD_MERCHANT`. No WordPress changes, post publication, test sends, list imports/exports, affiliate activation, checkout, paid service, Grok content production, analytics scripts or homepage PR modifications. Preserve original four editorial/two commercial mix.