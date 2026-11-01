# Dispatch R44: commercial clickpath quarantine and practical release triage

**Owner:** FV Dispatch Campaign Studio, master GitHub Issue #174. Companion Mind & Affiliate Studio Issue #171. **Branch state:** draft-only, stacked on PR #460 / ultimately canonical PR #175. **Preserves:** four original editorial issues, two original commercial-review issues, all existing manuscripts and all earlier review candidates. The original manuscripts were inspected; this sprint did NOT silently substitute optional R37/R38 copy. Homepage PR #49 was not touched.

## Executive decision

The highest-value editorial and compliance problem that can be advanced without mailing, changing WordPress or contacting a merchant is a proven **clickpath bypass**: the original Zen12 edition uses the vendor's live sales site as a clickable source citation, despite saying the product recommendation and independent first-party guide are not active. Source citations are not affiliate URLs, but a recipient following one still reaches a purchase-capable vendor environment without the promised independent guide.

**Measured against the exact current R43 PR head (2026-11-01):**

| Format | Issue 03 Zen12 clickable merchant hrefs | Issue 05 Total Focus merchant hrefs |
| --- | ---: | ---: |
| Canonical Markdown source | 2 | 0 |
| Original rendered HTML preview | 2 | 0 |
| Gutenberg review candidate blocks | 2 | 0 |
| **Total distinct link instances** | **6** | **0** |

The six instances are two distinct vendor destinations repeated across three formats (the Zen12 homepage and About page). They have no evidenced affiliate parameters; no sale, tracking, referral right, or customer action is inferred. The optional R37 Issue 03 and optional R38 Issue 05 safer HTML treatments each show zero active merchant hrefs in this specific static test. They remain **unapproved** and not usable as automatic canonical replacements.

The new source-controlled standard-library Python auditor reads all eight *existing* representations, extracts actual hrefs from HTML or inline Markdown, and distinguishes ordinary text that names a source from an actionable link. It flags direct official merchant domains and subdomains, first-party redirect parameters to merchant domains, and active JavaScript/data/vbscript schemes. It does not remove source attributions, rewrite manuscripts or alter links automatically. This suite is a security and editorial routing check, **not** a declaration that source-free pages are send-ready. The new static HTML reviewer board deliberately contains four editorial links to already published destinations and two visually disabled commercial destinations, accessible from keyboard and smaller screens without scripts, forms, tracking or external merchant anchors.

### Why source-level safety is still not inbox-level safety

Jetpack Newsletter is configured for **excerpt** delivery and post-date/featured-image inclusion. Official Jetpack documentation, accessed November 1, 2026, states that when a post has no custom excerpt, its newsletter excerpt may be taken from the first **350 characters**; that is not the generic WordPress 55-word excerpt rule. Neither of the two canonical commercial issues places its commercial disclosure in the first 350 simplified story characters. Existing optional custom excerpts are designed to disclose early, but they are **not installed or proven in a real received Jetpack message**.

Therefore a clean offline preview cannot establish the actual subject, Gmail preview text, date and hero image placement, from/address authenticity, legal footer, unsubscribe operation or delivered editorial/merchant routing. A real received-email preview or authorized controlled test is a founder-gated action; this sprint did not request or perform it.

## Verified live system snapshot, read-only

At **2026-11-01 14:39 UTC**, authenticated WordPress connector calls returned: newsletter enabled; technically able to send; automatic email on publishing a new post OFF; excerpt delivery; featured images and post dates in messages ON; reply-to set to no-reply; display sender Final Vestige; no reported *recent* sends. The 52-page Seven Day Focus Fieldbook is still configured in the welcome message; configuration is not evidence a recipient successfully received it.

Subscriber diagnostics remain **total=2, confirmed=2, unconfirmed=2**. These are not additive counts and do not demonstrate four distinct people, two proven eligible people or zero remaining unconfirmed people. The unique consent-eligible recipient audience is unknown, and private reconciliation in WP Admin is required. No subscriber addresses or tokens are included in this PR. Published WordPress pages Dispatch (ID 523), Focus (1579), and Editorial Standards (17) were read without changes. The existing editorial promise is investigations and archival finds, not repeated commercial blasts.

### Merchant-specific evidence and limits

- Official Zen12 offer: https://zen12.com/hnp . Public seller page advertises twelve-minute sessions as equivalent to an hour of advanced meditation and uses strong meditation/brainwave benefit language. That is **seller marketing, not a validated product trial**. The canonical Issue 03 distinguishes Beginner/Premium/Advanced package specifications; actual fulfillment, live checkout/refund, independent efficacy and authorized email marketing need their own proof.
- Official Hypnosis Live Total Focus product page: https://hypnosislive.com/mental-skills/total-focus . The seller lists a 33-minute, 47 MB recording and public discounted pricing, and advertises substantial concentration improvements. No approved Final Vestige checkout price, refund outcome, product-specific efficacy study or email marketing permission follows from this public page.
- Inspire3 public partner information and different-product swipe resources cannot establish rights to use any Zen12 or Total Focus earning links or to email a subscriber list. Do not adopt any claimed discount deadline, fake scarcity, testimonials, client results or efficacy promises.
- Mind Studio's current Zen12 guide work (PRs #456 and #464) is unpublished and unmerged. Neither commercial newsletter may point readers to an unapproved or non-live first-party guide. Do not bypass the guide through a secondary source link.

FTC CAN-SPAM guidance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . FTC endorsement disclosures: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking . A commercial email needs accurate identity/subject, clear commercial context, a real physical postal address for the sender and understandable working opt-out. Editorial classification alone is not a substitute for reviewing primary purpose. Conservatively verify the actual Final Vestige business mailing address and unsubscribe in *every* received issue. Automattic's corporate address in a signup confirmation is not our sender's mailing address.

## Exact operational path to a legitimate launch

**1. Founder/business operations: legal and actual mail proof.** Supply an authentic business postal address (the FTC permits, subject to its rules, a qualifying registered USPS PO box or properly registered private mailbox), then separately authorize a controlled native WordPress email preview/test without delivering to the actual subscriber list. Capture privately the complete received MIME, mobile and desktop rendering, subject, preview, from and reply-to identity, footer physical address, unsubscribe target and opt-out operation. No address or unsub token in GitHub. No authorized test/send presently exists.

**2. WordPress subscriber operations: deduplicate privately.** Determine the denominator and confirmed opt-in eligibility from WP Admin's underlying subscriber states, not by arithmetic on the inconsistent API totals. No importing, exporting to GitHub, contacting, or guessing addresses. If status is ambiguous, continue HOLD.

**3. Mind & Affiliate Studio: approved commerce.** Obtain per-product written acceptance, exact permitted email channel, earning URL/tracking format, approved/forbidden creative, fresh checkout and refund evidence, and founder-approved *published* Zen12 and Total Focus independent guides. A generic product listing or another brand's swipe file is insufficient.

**4. Campaign editor: single-CTA and disclosure checks.** Keep exactly six issues with four editorial and two conditional product-guide placements. If a commercial alternative is chosen, require founder sign-off on the actual replacement, with one clear reader action and disclosure beside the possible commission-bearing recommendation and in a visible early excerpt. Evidence citations in the full website guide can be reviewed separately, without hidden checkout hops or unapproved shortening services. The underlying official sources remain cited accurately.

**5. Founder: separate final permission.** Only after all gates are verifiably complete should the founder explicitly approve the complete creative, recipients and schedule. Publishing a WordPress article does not itself grant permission to email. Leave new-post automatic sends OFF absent a separate authorized change.

## How to reproduce this sprint

Run the R44 source-only auditor: python dispatch/campaign-2026-mind/r44-click-quarantine/route_guard.py . It prints privacy-safe JSON describing the original links and optional alternatives without fetching a URL or performing a write. Run R44 tests: python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r44_route_guard.py -v . The ordinary Dispatch GitHub Actions workflow also exercises the full stacked regression suite against the exact PR head; its hosted results must be independently inspected before a test-pass assertion is made.

Limitations: HTMLParser processes plain HTML anchor/area links and the current inline Markdown citation syntax; it does not emulate JavaScript redirects or all Markdown reference syntaxes, inspect browser navigation, inspect mail MIME, validate partner permissions or prove a legal determination. The live public site is not modified. Old canonical issue 03 link instances remain blocked **for release** and are intentionally reported as unresolved; safe optional variants are still unapproved. No dry-run or static audit can move any issue out of HOLD on its own.

**Release decision:** 01, 02, 04, 06 HOLD_UNSENT. 03, 05 HOLD_UNSENT plus HOLD_MERCHANT. Existing signup list and Focus welcome unchanged. No mail, test mail, affiliate link, post, setting, tracking, purchase or new email platform.
