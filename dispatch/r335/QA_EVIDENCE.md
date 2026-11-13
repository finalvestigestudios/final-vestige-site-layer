# R335 verified evidence, limitations, and owner handoff

**Date:** November 13, 2026 PT (live provider snapshots at 18:03 UTC).
**Parent:** R334 draft PR #2372, exact prior HEAD 9e779fe8bfb6d8685b18151a6b4ebdfe158d97fd.
**Original source:** draft PR #175 exact HEAD d57ccdba3aee8f065e143e101c2945f4f3d01647; originals UNMODIFIED. Prior release gates #201, preview #2337, inbox checker #2343, site-transfer check #2348, and frozen homepage #49 are not changed.

## Independently executed tests
1. Native Python: restored the previous archived nine-file master campaign, compared eight files used by tests to independently fetched current GitHub blob IDs (manifest, test and six issue markdown files; **8/8 matching**). Ran python -m unittest discover against the actual original test source: **6/6 PASS**.
2. Native Node: on local sources with exactly matching GitHub blob SHA signatures for signup_boundary.cjs (b9c6d29382d182027aa9b1ce17e986d510a4f7b3) and signup_boundary.test.cjs (a7f6026cc56bb827dfd909b6b635b0cb9ff039cf), ran node --test: **36/36 PASS**. Initial draft found a false-positive PII field rejection of the permitted email_subscription_status key. Corrected before remote commit and reran clean.
3. GitHub connector independently fetched **6/6 newly committed R335 files**. Source content inspected; 36 tests declared; send authorization remains hard-coded false and real email-eligible/paid metrics null. Offline review HTML checked structurally (language/viewport, no scripts), **not** browser or actual inbox tested.
4. Live WP newsletter read-only action status: subscriptions on, site_can_send true (technical capability only), new-post automatic emails off, full email content, sender Final Vestige Studios, 52-page Fieldbook welcome configured. Subscriber count total 3 / confirmed 3 / unconfirmed 2. Separate followers source WordPress.com 3 / direct email 0. Five recent posts each never_sent_opted_out. **Email eligibility and actual welcome receipt remain UNKNOWN.**
5. Inspected WordPress published /dispatch/ and /focus/ pages and Editorial Standards. On /focus/ the direct 52-page download hyperlink exists independently of subscriber eligibility and the page explicitly requests a confirmation when needed. A direct click is not a confirmed signup.
6. Verified official WordPress.com documentation: already-verified WordPress.com accounts can bypass the new confirmation email; other email subscribers confirm the link. Real subscription status (Subscribed vs Not confirmed, Bounced, Emails paused) is distinct from follower totals. Sources: https://wordpress.com/support/newsletter-settings/ and https://wordpress.com/support/subscribers/ .
7. Refreshed seller source comparison: https://zen12.com/about (seller 12-level audio promise), https://zen12.com/welcome (merchant's separate newsletter), https://hypnosislive.com/mental-skills/total-focus (33 minutes/47 MB and claims; no independently verified efficacy); https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . No authenticated Final Vestige email affiliate authority was found/established by public material.

## Real-world release and business verification NOT achieved
- NO account-specific Inspire3/ZEN12/Hypnosis Live email permission or issued commission URL, merchant approved first-party guides, current final checkout rights/prices, paid settlements, fees/refunds, independently qualified-session denominator.
- NO native Jetpack actual received email, functional opt-out witness, independently verified Final Vestige publisher physical mailing address, founder authorization for test or real send.
- NO verified real eligible Dispatch email-recipient count or actual welcome/Fieldbook arrival; counters overlap and the WP followers endpoint tracks a separate population.
- NO native browser screenshot test of GitHub board; board is static source inspected, not an actual Jetpack email render. No new production analytics, WordPress write, test email or subscriber action.

## Conversion-first required actions by owner
- **Mind/Commerce:** prove Zen12 Premium *EMAIL* earning rights and a disclosed, already-live approved independent guide. HOLD_MERCHANT.
- **Claude/Focus:** privately reconcile provider email subscription states, both legitimate verification mechanisms and deduplicated confirmed_signup, then independently check welcome receipt without exposing addresses. UNKNOWN/HOLD.
- **Dispatch/Founder:** after separately approved safe test only, witness actual rendered email with valid FV physical postal address, truthful subject, opt-out and commercial disclosure. NOT RUN/HOLD.
- **Grok/Praxxis/Claude:** use genuine platform asset_id and existing privacy-safe site analytics; independently verify human session and any later paid settlement. UNKNOWN.
- **Commerce:** independently settle orders/commission and refunds/fees. **Net revenue / 1,000 qualified-human sessions NOT COMPUTABLE** (not assumed zero).

**Final release decision: all six original drafts HOLD_UNSENT, commercial 03 and 05 HOLD_MERCHANT. 4:2 allocation unchanged. No emails, tests, contacts, WordPress changes, affiliate activations, merges or expenses.**