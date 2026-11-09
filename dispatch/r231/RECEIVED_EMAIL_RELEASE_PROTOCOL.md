# R231 — The missing delivered-message proof

**Owner:** Dispatch #174; Mind #171; Focus #129; Revenue #820. Stacked on R230 #1733 exact SHA 36bc69d7dbe9d5548c51ad443acd262fdbbf7de6. Source only. No founder authorization for test sends, WordPress drafts, publication, contact, scheduling or setting changes.

## Scope and four evidence boundaries

Prior QA examined Gutenberg-style sources and Jetpack configuration, not actual delivered multipart emails. New received_email_gate.py is a local-only inspector for a separately authorized, ALREADY RECEIVED .eml. It checks subject match, major mail headers, HTML/plain alternatives, placeholder leakage, literal presence of a separately verified publisher-address string, and plausible opt-out syntax. It returns no private values and never unlocks sending.

Do not confuse (1) a source preview, (2) parsed .eml bytes, (3) provider-confirmed opted-in recipient, or (4) independently settled paid order. A plausible List-Unsubscribe header cannot prove the link functions. Checking address text cannot prove the mailing address belongs to Final Vestige. An Automattic confirmation footer is not automatically Final Vestige's postal address. Email-only follower counts, page ?subscribe parameters and displayed downloads do NOT establish recipient marketing consent.

## Conditioned future evidence intake — NOT SEND AUTHORIZATION

Only if the founder separately authorizes an exact test message, recipient and WordPress procedure should an eligible consenting recipient receive a genuine Jetpack test. Privately capture the already received .eml, keeping it OUT of GitHub and broad chat logs. Record source provenance, send/receipt UTC, exact reviewed subject, postal-address documentary ownership and consent. Run the inspector privately by importing inspect_received_email(raw, expected_subject=..., verified_publisher_address=...). It has deliberately no CLI. Its output is only non-sensitive review booleans; never check the raw MIME or mailing address into source.

A reviewer still must verify the real unsubscribe mechanism works and opt-outs are honored/suppressed, that the physical mailing address is valid, and that the commercial disclosure is conspicuous beside an approved recommendation. Independently validate provider-authenticated consent, named Inspire3 acceptance, explicit EMAIL promotion rights, the account-issued earning URL, published reviewed guide and checkout/refund terms. No tool may auto-send if a checker looks green.

Without new founder permission for genuine delivery, actual email footer, opt-out and welcome receipt remain UNVERIFIED. All six issues HOLD_UNSENT; 03/05 additional HOLD_MERCHANT.

Official: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://finalvestige.com/editorial-standards/ .
