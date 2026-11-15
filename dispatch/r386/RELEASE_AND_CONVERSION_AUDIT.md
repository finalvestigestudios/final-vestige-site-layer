# Dispatch R386 — evidence, editorial and revenue release audit

**Scope:** New optional Issue 06 editorial review and source-only proof chain. **No original #175 text altered; no alternate approved.** Current ancestor #2657, original master #175 and readiness #201. Hard hold on every email, including editorial.

## First source-of-truth reads

- GitHub coordination [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), and latest owner updates, including Mind R405 [#2658](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2658). Mind has no authenticated per-SKU EMAIL permissions or approved live affiliate guides.
- [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) exact head d57ccdba3aee8f065e143e101c2945f4f3d01647 is open, draft; all eight campaign manifest/test/article blobs independently fetched and verified. Six original Python assertions **replicated directly in isolated V8 against the exact eight fetched GitHub file contents**: 6/6 PASS. **Native Python was not executed in R386**; do not convert this to a Python claim. The six tests check status, editorial mix, disabled affiliate links, merchant disclosures, placeholder footers and a small banned-claim list. They do **not** prove email compatibility, merchant permission or native CAN-SPAM compliance.
- [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) is a separate open/draft gate. Its fallback copy has not been adopted. Latest ancestor [#2657](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2657) is open/draft. Homepage PR #49 is frozen and untouched.
- Authenticated WordPress read-only November 15, 2026, 20:33:13–15 UTC: /dispatch/ id=523 and /focus/ id=1579 are published, as is [Editorial Standards](https://finalvestige.com/editorial-standards/) id=17. Standards favor primary records, reveal uncertainty, qualify interpretations, label commercial links, and cite sources.
- Jetpack newsletter subscriptions enabled; new-post email default OFF; content FULL; sender Final Vestige Studios; no-reply. Welcome configured to link the 52-page Fieldbook. Five recent published posts show never_sent_opted_out with false send flag; zero sent in that diagnostic window. **Site can send=true is a capability, not authorization.**
- Counts total=3, confirmed=3, unconfirmed=2; WordPress.com follower count noted separately as 3, direct-email follower count noted separately as 0. Those fields are not addable as five eligible recipients; actual unique receiving inboxes and provider-verified consent scope remain UNKNOWN. No subscriber PII was viewed, exported or stored.
- Public /focus/ client-side completion/download display does NOT prove Jetpack subscription confirmation, inbox receipt or Fieldbook access. A Gmail read-only search found no targeted Fieldbook welcome receipt, but absence of a result is not evidence none was ever delivered.

## New original subject and conversion review

**Optional Issue 06 (Stratton):** Subject 'He changed the image. His eyes had to relearn the room.' Proposed preheader 'An 1896 experiment, eight later days, and a warning about easy explanations.' Body distinguishes 1896 three-day, 21.5-hour self-experiment and longer 1897 eight-day, 81.5-hour observation, and deliberately avoids any claim that everyone's brain can be reprogrammed in eight days. One first-party editorial CTA leads to existing [Focus Fieldbook](https://finalvestige.com/focus/)—not a merchant link. Source: Stratton 1896 original DOI https://doi.org/10.1037/h0072918; Berkeley historical profile https://psychology.berkeley.edu/about/history/memoriam; Stanford Encyclopedia historical interpretation https://plato.stanford.edu/archives/win2021/entries/action-perception/.

**Original six honest conversion review (not rewriting):**
| Issue | Existing subject | Highest-impact copy/transport problem | Action |
|---|---|---|---|
| 01 | The mind is not a camera | Puységur archive CTA duplicates 02; the subject is accurate but broad and low intent | Keep editorial, compare engagement only if real authorized send someday |
| 02 | Before hypnosis had a name | Same destination, two weeks in a row, can feel repetitious | Cross-reference direct source and unique utility, NOT another affiliate pitch |
| 03 | The twelve-minute meditation question | Placeholder guide cannot be used; 12-minute convenience easily misread as claimed product efficacy | No commercial placement until Mind owner supplies permitted EMAIL offer and live vetted guide |
| 04 | Fourteen seconds. A much longer explanation. | Specific '14 seconds' not established as a single well-defined measured Apollo 1 event; risks an overly exact hook | HOLD_COPY; R379 correction candidate exists but NOT_ADOPTED |
| 05 | Before you press play on a hypnosis audio | Generic catalog is not a verified exact-SKU recommendation; guide missing | HOLD_MERCHANT; Total Focus exact recording only after authorization |
| 06 | What did seven days of attention reveal? | Asks for a seven-day result while new subscribers may not yet have finished the Fieldbook | Editorial email must not assume reader completed it; preserve CTA with no fabricated anecdote |

**Native Jetpack subject/preheader:** WordPress says post title becomes subject: https://wordpress.com/support/newsletter/send-newsletter-emails/ . No verified native separate preheader mapping; offline hidden text does not establish transport. WordPress [Preview email](https://wordpress.com/support/newsletter/email-appearance/) is a non-sending editor action; Send test email delivers a real message. Neither was invoked. Offline HTML is purely a reviewer specimen, not a native preview.

## Official merchant claim and permission alignment

1. [Zen12 seller](https://zen12.com/) lists Premium 48 MP3s, 12 levels, $87.99 public; [special coupon page](https://zen12.com/secret/) separately advertises $37 with condition. Seller asserts brainwave effects and one-hour-in-twelve-minute equivalence; these have NOT been independently shown for that SKU or cohort. Refund claim on the seller marketing page is not a verified future referred checkout term.
2. [Hypnosis Live Total Focus seller page](https://hypnosislive.com/mental-skills/total-focus) advertises a 33-minute, 47-MB recording and strong 'reprogram' / performance claims. Public price observations across snapshots range from $2 promotion to $17.95 / $24.44, with page variants; do not quote a universal referral price. [Seller FAQ](https://hypnosislive.com/faq) says request refund within 14 days, with a five-sessions-per-year limit; no guarantee of Final Vestige referred checkout terms.
3. [Inspire3 Limitless Labs partner swipe page](https://inspire3.com/ll/) concerns a DIFFERENT product and explicitly references approval for that program; its copy **cannot** be repurposed as Zen12 or Total Focus permission.
4. Public consumer marketing found in connected Gmail does not document named Final Vestige affiliate acceptance, SKU-specific email rights, approved email creative, sub-ID/tracking URLs, or independently settled commissions.
5. FTC requirements: https://www.govinfo.gov/content/pkg/USCODE-2024-title15/html/USCODE-2024-title15-chap103-sec7704.htm . Final Vestige's own qualifying physical mailing address, rendered unsub link and effective operation are unverified. Do not substitute the address of Automattic, Inspire3 or Hypnosis Live.

## Proof-chain QA

- Five new reviewer/source files plus one direct-source pure JS release firewall and its authored Node test suite. Offline HTML has a readable h1, hidden proposed preheader, table-based layout, inline styles, accessible link text, plain-text companion, no externally loaded images/scripts, and deliberately visible compliance placeholders.
- Source-only gate passed **21/21 directly executed isolated V8 assertions**, covering each issue HOLD, merchant per-SKU rights, no conflation of consumer checkout with publisher commission, dedup of provider confirmation IDs and settled orders, missing denominator, refund/fee completeness, and source-only status.
- New 'release_gate.test.mjs' is present for future reproducible native execution, but **native Node was not run**. This sprint also replicated the original #175 Python suite's six assertions on exact fetched GitHub source content (V8, not native Python).
- The positive synthetic fixture returns $6.50 commission net for 500 verified sessions (thus $13/1,000)—a **test fixture only**, NOT measured Final Vestige performance. Actual qualified human sessions and actual independently settled commissions are unavailable, so commercial KPI is **NOT_COMPUTABLE, not zero**.
- All merchant approvals in 'MERCHANT_PERMISSION_PROOF_LEDGER.json' are false/unverified. Genuine native WordPress preview, actual inbox delivery, postal footer, opt-out, source-linked real leads, paid referral checkout and merchant settlement are **not tested**. These are RELEASE BLOCKERS.

## OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER

| Offer | Funnel | Blocker | Next permitted non-sending change/experiment | Current evidence | Owner |
|---|---|---|---|---|---|
| Zen12 | Issue 03 → vetted guide → paid commission | Named EMAIL rights, issued earning URL, live vetted guide absent | Require authenticated per-SKU merchant scope / current final checkout + guide acceptance | FAIL merchant permission | Mind / Commerce |
| Focus | Grok asset → landing → confirmed opt-in → welcome | No provider-authoritative unique eligible inbox receipt, double opt-in or delivered Fieldbook proof | Reconcile provider aggregate read-only and define privacy-safe consent join | UNKNOWN, not 3 verified inboxes | Focus / Claude |
| Dispatch | Six-issue email → compliant received experience | True FV postal, native unsubscribe, mapped preheader, native preview absent | Founder-supervised non-sending Preview email once an editor draft is authorized | FAIL native proof | Dispatch / Founder |
| Grok → revenue | Qualified human session → CTA → paid commission | No complete merchant records and auditable session cohort | Claude validates existing asset IDs/UTMs; Commerce supplies settled payout after refunds/fees | NOT_COMPUTABLE | Grok / Praxxis / Claude / Commerce |

**Final verdict:** Six original editions HOLD_UNSENT, Issues 03/05 HOLD_MERCHANT, Issue 04 HOLD_COPY, new Stratton alternative NOT_ADOPTED. No email/test email, subscriber interaction, WordPress modification, affiliate activation, public post, paid service, deployment or merge. Founder final approval still required.
