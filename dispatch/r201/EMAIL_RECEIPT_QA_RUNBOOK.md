# Received Jetpack email proof protocol (read-only / no recipients contacted)

## What counts as evidence
1. **Native WordPress editor preview** — only after an editor draft/preview action separately authorized. Jetpack newsletter switch ON within the editor exposes Preview Email, which can render desktop/tablet/mobile; *preview is not delivery.* Do not press Send test email or Publish without founder's separate permission. Current site default new-post emails OFF.
2. **Actual previously received Final Vestige newsletter** — inspect legally obtained, authorized message. A WordPress 2026-10-25 *subscription confirmation* alone does not qualify; its Automattic address is Automattic's, not Final Vestige's. The Fieldbook welcome's configured text does not prove actual delivery.
3. **Headers and MIME** — verify From is accurate, subject exactly matches issue, HTML and plaintext parts, explicit visible unsubscribe text and operational target, List-Unsubscribe if provider offers it; a header without a conspicuous body mechanism does NOT satisfy review on its own.
4. **Valid Final Vestige physical postal address** — a qualifying verified street address, registered PO box or regulated commercial receiving mailbox; never substitute Automattic's or Inspire3's address. Keep actual address out of repository and log a redacted proof reference.
5. **Unsubscribe operation** — test only with founder-authorized isolated recipient/flow so legitimate subscriber preferences are not changed; verify no sign-in/purchase, successful opt-out and timely suppression. Do not follow token-bearing unsub links by automated crawler.
6. **Commercial near-offer disclosure** — if linked guide may earn commissions, state that relationship in the message *near the CTA*, not only on website policy page. If directly affiliate-linking, disclose next to direct link. Offer #03/#05 stays inactive now.
7. **Jetpack preheader caution** — WP docs say title becomes subject; do not claim `Preheader` in Markdown is a native editor field until proven in actual rendered MIME.
8. **Privacy** — never push raw email, recipient, signed unsubscribe token, physical private address, email headers or personal IDs to public GitHub. Only boolean QA summary + internally restricted proof pointer.

Official: https://wordpress.com/support/newsletter/email-appearance/
https://wordpress.com/support/newsletter/send-newsletter-emails/
https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

### Disposition at this exact sprint
- Jetpack native editor preview: **NOT VERIFIED**.
- Received commercial newsletter: **NONE VERIFIED**.
- Valid FV postal address: **NOT VERIFIED**.
- Operational unsubscribe: **NOT VERIFIED**.
- Welcome Fieldbook receipt: **NOT VERIFIED**.
- All six: **HOLD_UNSENT**.
