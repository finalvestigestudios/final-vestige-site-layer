# Dispatch R181 — received-mail evidence, native-preview route, conversion-first gates
**UNSENT, UNPUBLISHED, REVIEW ONLY.** 2026-11-07 08:34Z source snapshot. Owner Issue #174; companion Mind #171, Focus #129, conversion #820. Master campaign PR #175 d57ccdba3aee8f065e143e101c2945f4f3d01647; readiness PR #201; stacked on unmerged R180 #1375 exact e9affb27440ea7023b7b909a3506441f4ac00a88. Homepage PR #49 untouched.

## New read-only preview path documented by WordPress on October 30, 2026

Official newsletter design documentation last reviewed October 30, 2026: https://wordpress.com/support/newsletter-email-design/ says an already PUBLISHED post can be viewed in the WordPress post editor using **View → Email preview**. This potentially avoids toggling the post-level **Send this post to subscribers** checkbox merely to expose a preview. THIS SITE'S EDITOR HAS NOT BEEN TESTED; DO NOT CLAIM A NATIVE PREVIEW WAS CAPTURED. Keep operations read-only; never click Send test email, publish, save, schedule, or flip the per-post email toggle.

Older email appearance support, reviewed October 6: https://wordpress.com/support/newsletter/email-appearance/ says the Newsletter sidebar preview control appears when the per-post email toggle is on, beside a distinct **Send test email** action. Neither static HTML nor native editor preview proves a received email, actual header, mailing address, functioning unsubscribe, inbox preheader or Fieldbook welcome delivery.

## Real provider source of truth — read-only 2026-11-07T08:34Z

Jetpack newsletter **enabled**, can-send true, **automatic new-post email OFF**. Full-content mode; sender display Final Vestige Studios; reply mode no-reply. Configured welcome links to the 52-page Seven Day Focus Fieldbook; actual delivery UNKNOWN. Latest five post notifications status never_sent_opted_out, not five bounced sends. Diagnostics: counted 3, confirmed 3, unconfirmed 2 (nonadditive), suppressed 0, paid 0. Independent WordPress follower breakdown: WordPress.com 3, email-only 0; this does not prove three deliverable email addresses. Actual email-eligible audience UNKNOWN. /dispatch/ page 523 and /focus/ page 1579 published. API-view Subscribe link vs earlier public crawler email input is NOT a demonstrated broken visitor form. Focus download-panel success is NOT provider confirmation. No signed-out subscription submission authorized.

## New privacy-safe received-mail proof tool

Use only for PRE-EXISTING, AUTHORIZED local raw .eml. Run: python -I -m unittest discover -s campaign/r181 -p test_receipt_gate.py -v . Inspector: python campaign/r181/receipt_gate.py /private/path/to/authorized-received.eml . It makes no network calls or sends. Output contains only nonidentifying booleans; never sender, recipient, subject, full body or token. NEVER commit real messages, subscriber data or tokenized unsubscribe URLs. Header/presence indicators do NOT independently verify authenticity, legal publisher address, working opt-out, correct sender or real delivery. The HTML visibility heuristic is NOT an email-client accessibility certification; manually review actual HTML + plaintext separately.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer / step | Blocker | Change or experiment | Evidence | Owner |
|---|---|---|---|---|
| Fieldbook → confirmed lead | Aggregate counts but no known email-eligible recipient or guest flow | Provider read-only status and eventually authorized signed-out test | HOLD; no address-level proof | Claude/Site QA; Dispatch |
| Confirmed lead → welcome | Fieldbook configured only | Inspect an existing authorized received welcome and provider evidence | HOLD; no actual receipt | Dispatch |
| Dispatch → recipient | Native template, FV postal, actual opt-out unknown | Try published-post View → Email preview read-only; then separately verify real received email | NEW RESEARCH, NOT NATIVE CAPTURE | Dispatch |
| Zen12 / Total Focus → buyer | Named merchant approval, permitted email creative/channel/link and live vetted guide missing | Authenticate signed terms and guide before issue03/05 guide CTA | HOLD_MERCHANT | Mind #171 |
| Buyer → net revenue | No independently settled paid orders, refunds/fees and qualified-human denominator | Real immutable Grok asset_id, 7/30-day cohorts, reconciled partner/order evidence | NOT COMPUTABLE | Commerce / Praxxis |

## Seller claims and price drift (no price in emails)

Exact Zen12 Premium official page https://zen12.com/hnp describes 12 levels, 48 MP3, four listening styles and an advertised one-year refund. The seller asserts one-hour effects in twelve minutes, brainwave effects and health gains; product efficacy not independently proven. Search's cached snapshot shows $87 while a prior November 6 Mind review recorded $87.99: neither authenticates final checkout or refund performance.

Exact Hypnosis Live Total Focus official page https://hypnosislive.com/mental-skills/total-focus describes 33-minute / 47 MB audio and advertises 14-day refund. The sales copy says limitless/100% focus and brain reprogramming; these are NOT established outcome evidence. The retrieved page simultaneously shows $2 and $22.95 while prior Mind review noted $24.44. No promotional price or discount should appear without checkout verification. Public https://affiliates.inspire3.com/ is NOT proof of named FV acceptance, allowed email promotion or authorized earning links. Both buyer guides are not live. NO earnings link.

FTC commercial email guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires accurate header/subject, clear commercial identification when applicable, valid FV publisher physical postal address, practical opt-out and timely honoring opt-outs. Automattic and merchant addresses are NOT FV's address. FTC endorsement guidance https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking requires prominent near-link disclosures.

## New OPTIONAL historical Issue02, not original replacement

Subject "The blindfold changed the evidence"; proposed preheader "In 1784, investigators changed what a witness could see. The reports changed, too." Primary evidence: English 1785 printing of the 1784 French royal commission report https://www.gutenberg.org/files/78413/78413-h/78413-h.htm pp.56–58 ; Wellcome catalog https://wellcomecollection.org/works/enhgscmf . Actual reported sensations separated from hypothetical magnetic cause; the historical experiment is NOT proof of modern audio efficacy. ONE first-party editorial CTA to live https://finalvestige.com/2026/11/02/mesmerism/ rather than duplicating original issue01 Puységur CTA. HTML and plaintext are OFFLINE REVIEW assets, not native Jetpack previews; inbox preheader unverified.

## Proposed conversion contract, no invented performance

Only record confirmed_signup after provider-verified consent status, dedupe privately, never from Focus panel/query string. Grok posts require true public media URL and immutable asset_id (none provided) before tagging. Proposed organic-social URL scheme: utm_source=real_platform, utm_medium=organic_social, utm_campaign=approved_campaign, utm_content=real_asset_id; email CTA uses source=dispatch, medium=email, content=issue id. No subscriber identifier in URLs. Clicks, checkout starts, subscribers, page views and affiliate outbound traffic are NOT paid revenue. Realized net revenue per 1000 qualified-human sessions = 1000 * independently verified settled net revenue / independently verified unique qualified humans; if either absent, NOT COMPUTABLE. Tiny list means no statistical A/B winners.

**RELEASE: ALL SIX HOLD_UNSENT. COMMERCIAL 03 AND 05 ALSO HOLD_MERCHANT.** No site writes, newsletter edits, send/test send, imports, merchant activation, social posts, costs or merge. Founder final campaign approval remains required. Actual Jetpack native screenshot, received welcome, valid FV postal/opt-out, named affiliate permission, checkout and settlements all remain unverified.
