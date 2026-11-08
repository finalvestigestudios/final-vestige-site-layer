# Dispatch R33 — actual received-email evidence intake (DRAFT ONLY)

Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Merchant coordination: [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Master six-issue manuscript: draft PR #175. Independent per-edition legal and merchant release gates: draft PR #201. Parent: draft PR #384 at SHA \`42e75c0298e053bac5589c557a3578714eaf1b97\`. Homepage flagship #49 untouched.

## Why this is new, rather than another mocked email preview

The existing campaign has 6 full manuscripts, HTML/plaintext previews, Gutenberg post candidates, modeled WordPress excerpts, 163 passing hosted Python tests at R32, and eight real hosted Node safety suites. None establishes the actual email WordPress.com/Jetpack would send or its real footer. A screenshot of the editor preview does not prove inbox receipt, opt-out behavior or lawful commercial identity. Nor does the Oct 25 **subscription confirmation** prove delivery of the subsequent welcome message. This sprint adds an **offline, PII-safe parser for the first real \`.eml\` once the founder separately authorizes and obtains it**, rather than pretending one was received.

## Current source-of-truth snapshot (read only)

Authenticated WordPress at **2026-11-01 02:31 UTC**: Final Vestige site 256784396; newsletter subscriptions ON, site_can_send=true, new-post email default OFF, default email body **excerpt**, reply-to no-reply, sender display "Final Vestige", recent_sends empty; welcome configured with existing 52-page Seven Day Focus Fieldbook PDF link. This is configuration, **not proof of welcome delivery**.

Subscriber dashboard shows \`total=2\`, \`confirmed=2\`, \`unconfirmed=2\`, \`suppressed=0\` and \`paid=0\`. Categories **must NOT be summed**; eligible unique consented recipients remain UNKNOWN. A mismatch is not resolved by declaring either 2 or 4 reachable. Reconciliation must occur through the permissioned WordPress subscriber dashboard, without names/addresses in GitHub, exporting the list or contacting anyone.

Read-only WordPress source checked: published \`/dispatch/\` (page 523), \`/focus/\` (page 1579), and \`/editorial-standards/\` (page 17). The Editorial Standards require distinguishing record/inference and disclosing commercial relationships. No CMS settings, subscribers or posts were changed.

Read-only Gmail search (2026-10-31 PT): **no complete received Final Vestige Focus Fieldbook welcome or unambiguous merchant affiliate permission located**. One prior subscription confirmation is not an actual welcome email; the Automattic address in its footer does not count as Final Vestige's business address. Never expose recipient identity.

New Jetpack official references, dated late October 2026:
- https://jetpack.com/support/newsletter/ — editor **Preview email** and **Send test email** are different features. The latter sends to a recipient and is explicitly **not authorized** in this campaign.
- https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ — confirms default full/excerpt may be overridden on individual posts in editor, but actual applicability to this site/post must be checked.
- https://wordpress.com/support/newsletter/email-appearance/ — excerpt is an email configuration, not a design-quality guarantee.
- https://wordpress.com/support/newsletter/send-newsletter-emails/ — preview and the prepublish recipient panel are available in editor; no post should be created or published to obtain these without separate founder approval.
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — valid business postal address and functioning unsubscribe essential for applicable commercial email.
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking — clear and proximate endorsements/affiliate disclosures.

## Evidence acquisition, ONLY after separate founder authorization

1. Founder selects **one editorial issue first**, e.g., #02, and approves the exact native WordPress DRAFT creation / on-screen preview action. Draft creation itself is a CMS WRITE and is currently disallowed; this protocol is informational only. Keep global new-post auto-send OFF. Never publish or schedule. Retain source draft blockers until a reviewed delivery copy exists.
2. In Jetpack's **unpublished post editor**, inspect the actual Newsletter sidebar and per-post "Send this post to subscribers" setting. Some preview controls appear only when this switch is ON; switching it on for an unpublished draft is not a send, but changing post state is still an action requiring explicit permission. Do **not** use it under current authorization.
3. Capture native visual preview at desktop/mobile, confirm actual subject and displayed text versus the source. Confirm whether a per-post full-text override is present and whether footer/CTA/disclosure survives. A visual preview alone does **not** satisfy real delivered mail verification.
4. Separately request explicit founder approval of a controlled **test email**, its single authorized address, and the exact content; do not treat this runbook or an existing subscriber as that approval. No test email is currently authorized.
5. **Only after** founder sends/receives an authorized test email, founder may export the exact raw \`.eml\` privately and run the offline parser in a local controlled environment. DO NOT commit raw MIME, screenshots containing email addresses, IP addresses, unsub tokens or mailing address text. Do not upload the email to GitHub or send it to an assistant automatically.
6. The parser returns **only booleans plus SHA-256 and size**; it never prints the body, From/To, address, links, unsub token or postal marker. HTML link-shape checks do **not** test endpoint functionality. An actual test click, safe endpoint and the resulting unsubscribe state would require separately approved operator work; NEVER unsubscribe a real subscriber as an experiment.
7. The founder (or counsel) verifies a valid **Final Vestige** commercial postal address, not the vendor's/Automattic's address, and checks exact footer presence against a PRIVATE postal marker file, without uploading the address. Even a matching string cannot prove the postal address is valid or compliant.
8. If recipient consent, privacy, precise campaign post audience, claims, and supported commercial promotion have not all been approved, hold. The operator must also manually verify applicable mail client renderings (plain/HTML, images blocked, mobile, keyboard/screen-reader cues, subject/preheader truth).

### Safe local command (not an instruction to contact anyone)

\`\`\`bash
python dispatch/campaign-2026-mind/r33-received-mime-proof/native_mime_proof.py \
  /private/path/to/founder-authorized-received.eml \
  --expected-subject "Before hypnosis had a name" \
  --postal-marker-file /private/path/to/verified-fv-postal-line.txt \
  --report /private/path/to/pii-safe-candidate.json
\`\`\`

The CLI deliberately exits **2 even for a completely well-formed message** and marks \`HOLD_UNSENT\`. A syntactically plausible email can be fabricated; the parser is NOT a proof-of-delivery oracle. Exit 0 is deliberately impossible. For the two commercial emails, append \`--commercial\` (result always \`HOLD_MERCHANT\`). Nothing in this tool sends, posts, imports, subscribes, tracks, calls a vendor or connects to a network. Unit tests use fabricated \`example.invalid\` messages only.

## Specific failure modes the tests cover

Exact subject drift; sender display ambiguity; missing From/Subject; multipart handling; size/part bounds; evidence from attachments erroneously treated as body; HTML vs plaintext; header vs body unsubscribe HTTPS link; RFC8058 declaration without working endpoint; fake "unsubscribe anytime" without a link; JavaScript/http/credential-bearing URLs; draft warnings and inert guide placeholders leaking into recipient-visible content; absent/irrelevant postal marker; disclosure missing for commercial content; PII accidentally entering audit JSON; nonzero CLI exit even with a structurally complete message.

**Not verified automatically:** SPF/DKIM/DMARC, sender authentication, inbox transport, deliverability, list eligibility, commercial classification under CAN-SPAM, address ownership/registration, functional unsubscribe, precise product-claim support, FTC sufficiency of disclosure position, customer rights, or genuine product-email authorization. All remain manual evidence and founder/counsel judgment.

## Merchant link/claims boundary

Mind Studio's Zen12 and Total Focus pre-sell guides remain unpublished draft candidates and **do not supply approved live email CTAs**. The specific product pages and affiliate program must establish in writing Final Vestige's acceptance and permission for *email marketing*, correct eligible SKU/package and tracking URL, creative rights, current checkout/refunds and accurate claims. Public signup, seller marketing pages, consumer promotions and generic affiliates pages do not satisfy this requirement. Zen12 advertises Beginner 6 levels/24 MP3, Premium 12/48, Advanced final 6/24; this does not prove efficacy. Total Focus advertised 33 minutes/47 MB and concentration claims remain seller assertions. No hypothetical price, earnings or conversion data.

## Release gate and scope

The founders' original cadence remains **4 editorial / 2 optional commercial**, weekly DRAFT ONLY. All six \`HOLD_UNSENT\`; #03/#05 additionally \`HOLD_MERCHANT\`. This new evidence intake does not alter #175 or #201, publish WordPress content, change Jetpack settings, merge a PR, enable any earning link, test-send, contact subscribers/merchant or spend money. CI green is engineering evidence, never a sign-off to send. Required: genuine received MIME and visual/client review; working unsubscribe; business postal address; reconciled permissioned audience; actual approved merchant email terms, guide URLs and links; final **explicit founder campaign approval**.

Run all exact-checkout tests:

\`\`\`bash
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
\`\`\`
