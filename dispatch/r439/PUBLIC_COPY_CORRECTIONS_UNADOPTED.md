# R439 — Public signup promise: factual correction candidates (UNPUBLISHED)

**Owner:** Dispatch / Focus consent and copy QA. **Approver:** Founder. **Implementer, if explicitly approved:** Claude/site team. No CMS write, no new plugin, no new list, no automatic mail. Evidence: authenticated WordPress `/dispatch/` page 523 (modified 2026-11-05), `/focus/` page 1579 (modified 2026-11-16), Jetpack settings/status as of 2026-11-18 04:31 UTC.

## New documented issue: editorial promise vs sending control

The live Dispatch masthead says: **“New investigations and archive finds by email, when we publish them.”** The body says readers “will also get new investigations and useful finds ... when we publish them.” The default new-post email switch is **OFF**; the five latest inspected posts show `never_sent_opted_out`. WordPress permits an editor to turn emails on **per post**, but the active default does not ensure that a new publication becomes an email.

**Verdict:** An expectation mismatch that may reduce trust and conversion if readers believe every post triggers mail. Do *not* claim no subscriber has ever been emailed, and do *not* turn on automatic emails to make the copy literally true. The founder chose controlled, selectively approved releases.

### Candidate A — recommended, minimally invasive (not adopted)

**Masthead deck:** Occasional Dispatch editions: new investigations, original sources, and carefully chosen finds from the archive.

**Support copy:** Join The Dispatch, our existing WordPress newsletter, and get the free 52-page Seven Day Focus Fieldbook in the welcome message for a confirmed subscription. We send selected editions after editorial review, not an automatic email for every site post. Expect history and evidence first, with an occasional clearly disclosed guide to tools we're evaluating.

**Form helper:** Enter an email address using the WordPress Subscribe form. WordPress may ask you to confirm your address. Your ability to receive emails depends on your WordPress notification preferences.

**Guide note:** The Fieldbook is free to read at /focus/ even if you do not subscribe. A download does not subscribe you, and clicking Subscribe alone does not confirm your subscription.

**Privacy footnote:** Emails, when sent, contain a way to unsubscribe. See our Privacy Policy. [Do not assert this was tested in a delivered message until a native Jetpack receiving witness is recorded.]

### Candidate B — shorter acquisition-oriented (not adopted)

**Deck:** Evidence worth opening. Not another daily email.

**Support:** Our occasional newsletter moves between overlooked history, the documentary record and the ways perception can mislead. Subscribe to receive selected issues and the free 52-page Focus Fieldbook welcome gift. Not every new website post becomes an email.

**Form helper:** Confirm your subscription if WordPress requests it; existing WordPress.com accounts may follow a different confirmation path.

**Reader trust line:** You can use the Fieldbook without handing over an email address.

### Candidate C — if WordPress sends cannot be independently established yet (not adopted)

**Deck:** The Dispatch — an occasional newsletter in preparation.

**Support:** Get the free 52-page Focus Fieldbook now and explore our published investigations. Our six-issue newsletter pilot is still in draft review; we have not approved it for delivery. Subscribe only if you want future selected editions after launch.

**Why C has limited lifetime:** It is honest for the pilot state, but eventually needs updating when a real sending program has been approved. It should not imply the newsletter feature itself is disabled.

## Form/receipt distinctions for product and analytics QA

| Event/state | Proves | Does NOT prove |
|---|---|---|
| Jetpack Subscribe button click | Attempted interaction | Provider accepted subscriber, email consent, inbox eligibility |
| `?subscribe=` in Focus URL | URL parameter | Subscription, identity, permission |
| Focus PDF request | Resource interest | Newsletter signup, welcome receipt, buyer |
| WordPress.com Reader follow | Following within WordPress Reader | Current email-delivery preference |
| WordPress newsletter `confirmed` | Provider subscription status | Current eligible inbox, delivered welcome |
| Private provider Email subscription=Subscribed filter | Aggregate receiving eligibility, to be witnessed | Delivered message or monetization |
| Actual received welcome in authorized inbox | Receipt for that account | Every subscriber received it |
| Independently settled order | Paid conversion after proper merchant reconciliation | Net profit before refunds, fees and source attribution |

WordPress.com states that subscribers with existing WordPress.com accounts can receive the welcome without the separate confirmation email; non-account email subscribers receive a confirmation request first. Consequently, **never use receipt of a confirmation email as a universal prerequisite for a provider-confirmed signup**. See https://wordpress.com/support/newsletter-settings/.

## Copy QA acceptance criteria (founder may accept/reject)

1. Preserve single Jetpack Subscribe block and original `/focus/` link. No subscribe gating, capture endpoint or separate list.
2. No promise of automatic email per publication while `email_new_posts_by_default=false`.
3. No unsupported frequency guarantee, delivered-welcome claim, personal endorsement or unapproved affiliate link.
4. Explicitly identify subscription as optional for reading the free Fieldbook.
5. Consent helper must fit WordPress.com-account and email-only signup paths; do not assert every user receives a confirmation mail.
6. Preserve correction/source/affiliate independence consistent with https://finalvestige.com/editorial-standards/.
7. Founder and Claude must sign off on actual CMS copy before any change.

**No candidate was selected or published.** Any later implementation requires site QA for 360/390/768/1440px, keyboard navigation, no-JS state, visible Subscribe form, truthful CTA and privacy language, and a CMS render check.
